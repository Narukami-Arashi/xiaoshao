# -*- coding: utf-8 -*-
"""智能体核心逻辑:管理对话状态、调用大模型、本地快速预警。"""

from . import config, prompts, knowledge
from .llm_client import LLMClient, LLMError
from .emotion import detect_emotion
from .evidence import analyze_chat_text
from .fraud_radar import check_fraud_source


class XiaoShaoAgent:
    """校园反诈助手"小哨"智能体。"""

    # 高危关键词:出现这些词时,在等待大模型回复前先给出即时警告
    HIGH_RISK_KEYWORDS = [
        "安全账户", "屏幕共享", "验证码", "转账", "垫付",
        "先交费", "保证金", "解冻金", "刷单返利", "注销校园贷",
    ]

    # 诈骗类型识别规则:关键词 → 诈骗类型标签
    SCAM_TYPE_RULES = [
        (["安全账户", "涉嫌洗钱", "公检法", "检察院", "逮捕令", "资金清查"], "👮 冒充公检法诈骗"),
        (["注销校园贷", "校园贷记录", "影响征信", "清空额度", "监管账户"], "🏦 注销校园贷诈骗"),
        (["刷单", "返利", "做任务", "垫付返", "佣金", "点赞关注赚钱"], "💰 刷单返利诈骗"),
        (["退款", "理赔", "双倍赔偿", "包裹丢失", "甲醛超标", "商品有问题"], "📞 冒充客服退款诈骗"),
        (["屏幕共享", "远程协助", "共享屏幕"], "📱 屏幕共享盗刷诈骗"),
        (["投资", "稳赚", "理财平台", "虚拟币", "带你赚钱", "内部消息"], "📈 虚假投资诈骗"),
        (["网恋", "交友", "嘘寒问暖", "带你投资"], "💘 杀猪盘诈骗"),
        (["游戏账号", "游戏皮肤", "验号", "代练", "游戏交易"], "🎮 游戏交易诈骗"),
        (["助学金", "补助金", "教育局", "资助中心"], "🎓 助学金补助诈骗"),
        (["考试保过", "内部真题", "包过", "改分"], "📝 考试保过诈骗"),
        (["培训贷", "包就业", "培训费贷款"], "🏦 培训贷诈骗"),
        (["美容贷", "免费皮肤检测", "医美分期"], "💄 美容贷诈骗"),
        (["裸聊", "录屏", "通讯录"], "🔞 裸聊敲诈诈骗"),
        (["征信修复", "征信不良", "内部渠道修复"], "📋 征信修复诈骗"),
        (["会员扣费", "自动续费", "取消会员"], "📞 会员扣费诈骗"),
        (["借钱", "垫付", "我是你老师", "我是你同学", "辅导员"], "👥 冒充熟人诈骗"),
    ]

    def __init__(self):
        self.client = LLMClient()
        self.history: list = []  # 对话历史 [{"role","content"}]

    # ---------- 核心对话 ----------
    def chat(self, user_input: str) -> str:
        """处理用户输入,返回小哨的回复。

        Args:
            user_input: 用户输入的文本。

        Returns:
            小哨的回复文本(可能包含本地即时警告 + 大模型分析)。
        """
        user_input = user_input.strip()
        if not user_input:
            return "小哨在听,请描述你遇到的情况~"

        # 1. 本地即时高危预警(不等大模型,先提醒)
        instant_warning = self._instant_warning(user_input)

        # 2. 情绪检测与心理急救(恐慌/绝望/自责时先安抚)
        emotion_result = detect_emotion(user_input)
        emotion_prefix = emotion_result['prefix'] if emotion_result else ''

        # 3. 诈骗类型识别(自动标注用户描述的诈骗类型)
        scam_type_label = self._detect_scam_type(user_input)

        # 4. 组装消息并调用大模型
        messages = prompts.build_messages(self._trimmed_history(), user_input)
        try:
            reply = self.client.chat(messages)
        except LLMError as e:
            error_reply = (
                f"⚠️ 小哨暂时无法连接大脑(大模型服务),请稍后再试。\n"
                f"错误详情:{e}\n\n"
                f"🚨 如果情况紧急,请直接拨打 110 报警或 96110 反诈专线!"
            )
            self._append_history(user_input, error_reply)
            return error_reply

        # 5. 拼接即时警告、情绪安抚、诈骗类型与大模型回复
        final_reply = f"{instant_warning}{emotion_prefix}{scam_type_label}{reply}"

        # 4. 更新对话历史
        self._append_history(user_input, reply)
        return final_reply

    # ---------- 本地快速预警 ----------
    def _instant_warning(self, user_input: str) -> str:
        """检测高危关键词,返回即时警告文本(无命中则返回空串)。"""
        hits = [kw for kw in self.HIGH_RISK_KEYWORDS if kw in user_input]
        if not hits:
            return ""
        warning = (
            "🚨 **小哨紧急提醒** 🚨\n"
            f"你的描述中出现了高危信号:{'、'.join(hits)}\n"
            "**在继续之前,请牢记:不要转账!不要提供验证码!不要开启屏幕共享!**\n\n"
        )
        return warning

    # ---------- 诈骗类型识别 ----------
    def _detect_scam_type(self, user_input: str) -> str:
        """识别用户描述中涉及的诈骗类型,返回类型标签(无命中返回空串)。"""
        matched_types = []
        for keywords, label in self.SCAM_TYPE_RULES:
            if any(kw in user_input for kw in keywords):
                if label not in matched_types:
                    matched_types.append(label)
        if not matched_types:
            return ""
        if len(matched_types) == 1:
            return f"🔍 **小哨识别:** 这属于 **{matched_types[0]}**\n\n"
        return f"🔍 **小哨识别:** 这涉及 **{'、'.join(matched_types)}**\n\n"

    # ---------- 历史管理 ----------
    def _trimmed_history(self) -> list:
        """按配置裁剪历史对话,避免超出上下文窗口。"""
        max_msgs = config.MAX_HISTORY_ROUNDS * 2  # 每轮含 user + assistant
        if len(self.history) <= max_msgs:
            return list(self.history)
        return list(self.history[-max_msgs:])

    def _append_history(self, user_input: str, reply: str):
        """将本轮对话追加到历史。"""
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": reply})

    def reset(self):
        """清空对话历史,开启新会话。"""
        self.history.clear()

    # ---------- 知识查询(本地,不依赖大模型) ----------
    def list_fraud_types(self) -> str:
        """列出知识库中所有诈骗类型(本地快速查询)。"""
        lines = ["📚 小哨的诈骗类型知识库收录了以下类型:"]
        for i, item in enumerate(knowledge.FRAUD_TYPES, 1):
            lines.append(f"  {i}. {item['name']}")
        lines.append("\n💡 想了解某一类型的详细套路和应对方法,直接问我即可!")
        return "\n".join(lines)

    def get_fraud_detail(self, name_keyword: str) -> str:
        """按名称关键词查询诈骗类型详情(本地快速查询)。"""
        for item in knowledge.FRAUD_TYPES:
            if name_keyword in item["name"]:
                return (
                    f"📖 {item['name']}\n"
                    f"识别关键词:{'、'.join(item['keywords'])}\n"
                    f"典型套路:{item['description']}\n"
                    f"应对方法:{item['response']}"
                )
        return f"小哨没有找到包含【{name_keyword}】的诈骗类型,换个关键词试试?或直接描述你遇到的场景,我来帮你分析!"

    def show_emergency(self) -> str:
        """显示紧急联系方式。"""
        lines = ["🚨 紧急联系方式"]
        for k, v in knowledge.EMERGENCY_CONTACTS.items():
            lines.append(f"  • {k}:{v}")
        lines.append("\n遇到紧急情况,请立即求助!")
        return "\n".join(lines)