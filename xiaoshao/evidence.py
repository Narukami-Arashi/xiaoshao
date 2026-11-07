# -*- coding: utf-8 -*-
"""证据链辅助分析模块(融合版)。

用户输入描述 → 自动检测诈骗话术 + 识别诈骗类型 + 生成报案草稿 + 追问不确定细节。
"""

import re
import json
from typing import Dict, List, Optional

# ===== 诈骗话术模式库(扩展版) =====
SCAM_PATTERNS = [
    # --- 极高危 ---
    {'id': 'safe_account', 'pattern': r'安全账户|监管账户|清查账户|核查账户|验证账户',
     'level': '🔴 极高危', 'label': '「安全账户」话术', 'scam_type': '冒充公检法诈骗',
     'analysis': '公检法机关没有「安全账户」!这是冒充公检法诈骗的标志性话术,出现此词100%是诈骗。'},
    {'id': 'verify_code', 'pattern': r'验证码|短信码|动态码|校验码|手机验证|收到的码|报给我|告诉我验证',
     'level': '🔴 极高危', 'label': '索要验证码', 'scam_type': '各类诈骗',
     'analysis': '验证码是资金安全的最后一道防线。任何索要验证码的都是诈骗,没有例外。'},
    {'id': 'screen_share', 'pattern': r'屏幕共享|共享屏幕|远程协助|远程操作|共享手机屏幕|投屏',
     'level': '🔴 极高危', 'label': '诱导屏幕共享', 'scam_type': '冒充客服/公检法诈骗',
     'analysis': '屏幕共享=交出手机控制权。对方可以实时看到你输入的密码和验证码,直接盗刷。'},
    {'id': 'transfer', 'pattern': r'转账|打款|汇款|垫付|先交|转给我|转到.{0,10}账户|付款|支付|交钱|缴纳|充值',
     'level': '🔴 极高危', 'label': '要求转账/垫付', 'scam_type': '各类诈骗',
     'analysis': '所有诈骗的最终目的都是让你转账。只要涉及「先付钱」,100%是诈骗。'},
    {'id': 'brush', 'pattern': r'刷单|返利|佣金|垫付返|做任务|点赞赚钱|关注赚钱|动动手指|日赚|足不出户',
     'level': '🔴 极高危', 'label': '刷单返利话术', 'scam_type': '刷单返利诈骗',
     'analysis': '所有刷单都是诈骗!前期小额返利是诱饵,大额垫付后就会被拉黑。'},
    {'id': 'campus_loan', 'pattern': r'注销校园贷|校园贷记录|影响征信|清空额度|清零额度|注销贷款记录|学生贷记录',
     'level': '🔴 极高危', 'label': '注销校园贷话术', 'scam_type': '注销校园贷诈骗',
     'analysis': '征信不能通过电话注销!这是针对学生和毕业生的精准诈骗。'},
    # --- 高危 ---
    {'id': 'urgency', 'pattern': r'马上|立刻|限时|截止|最后.{0,4}分钟|名额有限|过期作废|不转就|今天.{0,4}之前|尽快|紧急|逾期|最后机会|倒计时',
     'level': '🟠 高危', 'label': '制造紧迫感', 'scam_type': '各类诈骗',
     'analysis': '紧迫感是诈骗的核心工具,让你来不及思考和核实。正规业务不会催你当场操作。'},
    {'id': 'secrecy', 'pattern': r'保密|不能告诉|不要告诉|别说出去|涉密|不要跟.{0,6}说|对谁都说|独自配合|不要联系',
     'level': '🟠 高危', 'label': '要求保密/隔离', 'scam_type': '冒充公检法诈骗',
     'analysis': '要求保密是骗子的操控手段,目的是切断你的求助渠道。越要求保密,越要告诉身边的人。'},
    {'id': 'authority', 'pattern': r'我是.{0,6}警察|我是.{0,6}警官|我是.{0,4}民警|公检法|检察院|法院|银监会|银保监|征信中心|公安局|刑侦|经侦',
     'level': '🟠 高危', 'label': '冒充权威机构', 'scam_type': '冒充公检法诈骗',
     'analysis': '公检法不电话办案!银监会不会电话要求操作。冒充权威是诈骗的常见开场白。'},
    {'id': 'download_app', 'pattern': r'下载.{0,10}APP|下载.{0,10}软件|安装.{0,10}应用|点击.{0,10}链接|扫码下载|下载这个|加我.{0,4}详聊|加.{0,3}QQ|加.{0,3}微信',
     'level': '🟠 高危', 'label': '诱导下载APP/加好友/点链接', 'scam_type': '各类诈骗',
     'analysis': '不明APP可能是木马,不明链接可能是钓鱼网站。正规业务不需要下载非官方APP或加私人好友。'},
    {'id': 'refund', 'pattern': r'退款|理赔|双倍赔偿|三倍赔偿|包裹丢失|快递丢失|商品有问题|甲醛超标|质量有问题|召回|退货理赔',
     'level': '🟠 高危', 'label': '虚假退款理赔', 'scam_type': '冒充客服退款诈骗',
     'analysis': '退款只走原路!任何主动来电的退款/理赔都是诈骗开端。'},
    {'id': 'investment', 'pattern': r'稳赚|保本|高收益|内部消息|涨停|投资平台|虚拟币|数字货币|带你赚钱|带你理财|理财群|收益截图|币圈|炒币|杠杆',
     'level': '🟠 高危', 'label': '虚假投资话术', 'scam_type': '杀猪盘/虚假投资诈骗',
     'analysis': '稳赚不赔的投资不存在!这是杀猪盘或虚假投资平台的典型话术。'},
    {'id': 'romance_invest', 'pattern': r'嘘寒问暖|宝贝|亲爱的|我们的未来|感情.{0,4}基础|信任我|我是.{0,4}真心|聊了.{0,4}天.{0,6}投资',
     'level': '🟠 高危', 'label': '网恋+投资组合(杀猪盘)', 'scam_type': '杀猪盘诈骗',
     'analysis': '网恋+投资=杀猪盘的标志性组合。网上认识的人一旦提到投资,100%是诈骗。'},
    {'id': 'fake_id', 'pattern': r'工号|警号|执照|证件号|逮捕令|通缉令|协查|立案号|警官证|工作证|身份证号是',
     'level': '🟡 中危', 'label': '出示伪造证件/文书', 'scam_type': '冒充公检法/客服诈骗',
     'analysis': '工号、警号、法律文书都可以伪造。网络发送的「证件」不可信。'},
    {'id': 'frozen', 'pattern': r'冻结|解冻|解冻金|卡单|系统卡|操作超时|资金冻结|账户异常|激活|保证金|押金|担保金',
     'level': '🟠 高危', 'label': '「冻结/解冻/卡单」连环话术', 'scam_type': '刷单/游戏交易诈骗',
     'analysis': '「冻结」「卡单」「解冻金」是连环诈骗话术。正规平台不会要求你交钱来「解冻」资金。'},
    {'id': 'fee_first', 'pattern': r'手续费|工本费|服务费|会员费|开通费|登记费|建档费|建档|开户费|认证费|保证金|押金',
     'level': '🟠 高危', 'label': '先交费才能领钱/办事', 'scam_type': '各类诈骗',
     'analysis': '领钱不需要先交钱!任何要求先交手续费、保证金才能领钱/办事的,100%是诈骗。'},
    {'id': 'help_money', 'pattern': r'借.{0,4}钱|借我|垫付|帮我转|帮我付|急用钱|家人住院|出车祸|住院费|手术费|医药费|保释金',
     'level': '🟠 高危', 'label': '紧急借钱/垫付', 'scam_type': '冒充熟人诈骗',
     'analysis': '紧急借钱是冒充熟人诈骗的典型话术。社交软件借钱必须电话或当面核实。'},
    {'id': 'exam_cheat', 'pattern': r'包过|保过|内部真题|原题|答案|改分|代考|枪手|包.{0,3}通过|不过退款',
     'level': '🟠 高危', 'label': '考试保过/代考话术', 'scam_type': '考试保过诈骗',
     'analysis': '考试没有「包过」!买卖考题和代考违法且是诈骗,「不过退款」是诱饵。'},
    {'id': 'subsidy', 'pattern': r'助学金|补助金|补贴|教育局|资助中心|发放.{0,4}补助|领取.{0,4}补助|国家.{0,4}补贴',
     'level': '🟠 高危', 'label': '助学金/补助发放话术', 'scam_type': '助学金补助诈骗',
     'analysis': '助学金/补助只通过学校发放,不需要先交手续费。领钱不需要先交钱!'},
    {'id': 'luoliao', 'pattern': r'裸聊|视频.{0,4}脱|录屏|通讯录.{0,4}发|视频发给你.{0,4}联系人|不转就发',
     'level': '🔴 极高危', 'label': '裸聊敲诈话术', 'scam_type': '裸聊敲诈诈骗',
     'analysis': '裸聊敲诈:不回复+不转账+立刻报警。骗子不会因你不转账就发视频(发视频=失去筹码)。'},
    {'id': 'credit_fix', 'pattern': r'征信修复|征信不良|内部渠道.{0,4}修复|修复征信|征信.{0,4}有问题|逾期记录.{0,4}修复',
     'level': '🟠 高危', 'label': '征信修复话术', 'scam_type': '征信修复诈骗',
     'analysis': '征信不能花钱修复!不良记录5年后自动消除。任何收费「修复征信」都是诈骗。'},
    {'id': 'game_trade', 'pattern': r'验号|游戏账号.{0,4}卖|买.{0,4}皮肤|游戏.{0,4}交易|代练|代打|装备.{0,4}买|低价.{0,4}皮肤',
     'level': '🟡 中危', 'label': '游戏交易话术', 'scam_type': '游戏交易诈骗',
     'analysis': '游戏交易只走平台担保!「验号」=盗号,私下交易被骗无法追回。'},
    {'id': 'training_loan', 'pattern': r'培训贷|包就业|培训费.{0,4}贷款|助学贷款.{0,4}培训|先培训后付款|学完还款',
     'level': '🟠 高危', 'label': '培训贷话术', 'scam_type': '培训贷诈骗',
     'analysis': '「包就业」是虚假承诺,「培训贷」是核心陷阱。骗子赚的是贷款提成。'},
    {'id': 'beauty_loan', 'pattern': r'美容贷|免费.{0,4}检测|医美.{0,4}分期|形象改造|零首付.{0,4}整形|免费体验.{0,4}皮肤',
     'level': '🟠 高危', 'label': '美容贷话术', 'scam_type': '美容贷诈骗',
     'analysis': '免费体验→制造焦虑→索要身份证→签字贷款。身份证不外借,不明文件不签字。'},
    {'id': 'member_fee', 'pattern': r'会员.{0,4}扣费|自动续费|取消会员|扣费.{0,4}取消|即将扣.{0,4}元|关闭.{0,4}扣费',
     'level': '🟠 高危', 'label': '会员扣费取消话术', 'scam_type': '冒充客服诈骗',
     'analysis': '挂断电话,自己打开官方APP查看会员状态。一切以APP显示为准。'},
]

# ===== 追问问题模板 =====
# 根据草稿中缺失的信息自动生成追问
FOLLOWUP_QUESTIONS = [
    {'id': 'time', 'check': r'被骗时间[\s\S]{0,4}【待补充】', 'question': '你大约是什么时候被骗的?(例如:2026年1月5日下午3点左右)'},
    {'id': 'amount', 'check': r'被骗金额[\s\S]{0,4}【待补充】', 'question': '你一共被骗了多少钱?是通过什么方式转的?(银行转账/支付宝/微信等)'},
    {'id': 'method', 'check': r'如何接触到骗子[\s\S]{0,6}【', 'question': '你是怎么接触到骗子的?(电话/短信/QQ/微信/网页广告/交友APP等)'},
    {'id': 'process', 'check': r'骗子如何取得信任[\s\S]{0,6}【', 'question': '骗子是怎么取得你的信任的?(对方自称什么身份?说了什么让你相信?)'},
    {'id': 'transfer_detail', 'check': r'关键转账节点[\s\S]{0,6}【', 'question': '对方以什么理由让你转账?你转了几次?每次转了多少?'},
    {'id': 'discovery', 'check': r'发现被骗的经过[\s\S]{0,6}【', 'question': '你是怎么发现被骗的?(对方失联/要求继续转账/别人提醒等)'},
]


def analyze_chat_text(text: str) -> Dict:
    """分析用户提供的聊天文本,识别诈骗话术模式。"""
    if not text or not text.strip():
        return {'total_patterns': 0, 'risk_level': 'low', 'found_patterns': [], 'summary': '未提供文本内容。', 'scam_types': []}

    found = []
    scam_types = []
    for p in SCAM_PATTERNS:
        matches = re.findall(p['pattern'], text)
        if matches:
            m = re.search(p['pattern'], text)
            start = max(0, m.start() - 10)
            end = min(len(text), m.end() + 10)
            context = text[start:end].replace('\n', ' ').strip()
            found.append({
                'label': p['label'],
                'level': p['level'],
                'matched_text': context,
                'analysis': p['analysis'],
            })
            if p['scam_type'] not in scam_types:
                scam_types.append(p['scam_type'])

    extreme = sum(1 for f in found if '极高危' in f['level'])
    high = sum(1 for f in found if '高危' in f['level'] and '极高危' not in f['level'])

    if extreme >= 2:
        risk = 'extreme'
        summary = '⚠️ 检测到多个极高危诈骗话术!这几乎可以确定是诈骗,请立即停止一切操作并报警!'
    elif extreme >= 1:
        risk = 'high'
        summary = '🚨 检测到极高危诈骗话术!对方极大概率是骗子,不要转账、不要给验证码,立即报警!'
    elif high >= 2:
        risk = 'high'
        summary = '⚠️ 检测到多个高危诈骗特征!强烈建议停止操作,通过官方渠道核实对方身份!'
    elif high >= 1:
        risk = 'medium'
        summary = '⚠️ 检测到疑似诈骗特征,请提高警惕,不要进行任何金钱操作,通过官方渠道核实!'
    elif found:
        risk = 'medium'
        summary = '检测到一些需要留意的特征,请谨慎对待。'
    else:
        risk = 'low'
        summary = '未检测到明显诈骗话术特征。但仍建议保持警惕,涉及金钱操作务必核实对方身份。'

    return {
        'total_patterns': len(found),
        'risk_level': risk,
        'found_patterns': found,
        'summary': summary,
        'scam_types': scam_types,
    }


def generate_report_draft(description: str, analysis: Optional[Dict] = None) -> str:
    """根据用户描述生成《被骗经过说明书》报案草稿模板。"""
    amounts = re.findall(r'(\d+(?:\.\d+)?)\s*(?:元|块|万)', description)
    phones = re.findall(r'1[3-9]\d{9}', description)
    scam_types = analysis.get('scam_types', []) if analysis else []

    amount_str = '、'.join(amounts[:5]) + ' 元' if amounts else '【待补充】'
    phone_str = '、'.join(phones[:3]) if phones else '【待补充】'
    scam_type_str = '、'.join(scam_types[:3]) if scam_types else '【待判断】'

    draft = f"""==============================
     被骗经过说明书(报案草稿)
==============================

【报案人信息】
姓名: 【待补充】
身份证号: 【待补充】
联系电话: 【待补充】
住址: 【待补充】

【案件概述】
被骗类型: {scam_type_str}
被骗金额: {amount_str}
被骗时间: 【待补充】
涉案对方联系方式: {phone_str}

【被骗经过(请按时间线详细填写)】

1. 如何接触到骗子:
   【待补充】

2. 骗子如何取得信任:
   【待补充】

3. 关键转账节点:
   【待补充】

4. 发现被骗的经过:
   【待补充】

【关键证据清单】(请打勾确认已准备)
□ 聊天记录截图(完整,不要截断)
□ 通话记录截图(含对方号码和通话时间)
□ 转账凭证(银行流水/支付宝/微信转账记录)
□ 对方提供的链接/APP/二维码截图
□ 对方的账号信息(QQ号/微信号/银行卡号)
□ 其他: 【待补充】

【资金流向】
转出账户: 【待补充】
转入账户: 【待补充】
转账方式: 【待补充】

【已采取的措施】
□ 已拨打110报警
□ 已联系银行冻结账户
□ 已保存所有证据截图
□ 已下载国家反诈中心APP

==============================
备注:本草稿由小哨反诈助手根据您的描述自动生成,
请补充【待补充】部分后带到派出所报案。
报案时请携带身份证原件和所有证据材料。
=============================="""
    return draft


def get_followup_questions(draft: str, limit: int = 3) -> List[Dict]:
    """根据草稿中缺失的信息,生成追问问题(每次最多limit个)。

    Args:
        draft: 当前草稿文本
        limit: 每次最多返回的问题数(默认3)

    Returns:
        追问问题列表。
    """
    questions = []
    for q in FOLLOWUP_QUESTIONS:
        if re.search(q['check'], draft):
            questions.append({'id': q['id'], 'question': q['question']})
    return questions[:limit]


def update_draft_with_answers(draft: str, answers: Dict[str, str]) -> str:
    """根据用户的追问回答,更新草稿中的待补充部分。"""
    updated = draft
    # 时间
    if answers.get('time'):
        updated = re.sub(r'被骗时间: 【待补充】', f'被骗时间: {answers["time"]}', updated)
    # 金额
    if answers.get('amount'):
        updated = re.sub(r'被骗金额: 【待补充】', f'被骗金额: {answers["amount"]}', updated)
    # 接触方式
    if answers.get('method'):
        updated = re.sub(r'1\. 如何接触到骗子:\s*\n\s*【待补充】', f'1. 如何接触到骗子:\n   {answers["method"]}', updated)
    # 取得信任
    if answers.get('process'):
        updated = re.sub(r'2\. 骗子如何取得信任:\s*\n\s*【待补充】', f'2. 骗子如何取得信任:\n   {answers["process"]}', updated)
    # 转账节点
    if answers.get('transfer_detail'):
        updated = re.sub(r'3\. 关键转账节点:\s*\n\s*【待补充】', f'3. 关键转账节点:\n   {answers["transfer_detail"]}', updated)
    # 发现被骗
    if answers.get('discovery'):
        updated = re.sub(r'4\. 发现被骗的经过:\s*\n\s*【待补充】', f'4. 发现被骗的经过:\n   {answers["discovery"]}', updated)
    return updated


def analyze_and_draft(text: str, llm=None) -> Dict:
    """融合分析:检测话术 + 识别类型 + 生成草稿 + 追问问题。

    Args:
        text: 用户输入
        llm: 可选LLM客户端,用于深度自主分析

    Returns:
        融合分析结果。
    """
    # 第一步:正则快速分析(即时)
    regex_analysis = analyze_chat_text(text)

    # 第二步:LLM自主深度分析(如果可用)
    analysis = regex_analysis
    if llm is not None:
        llm_result = llm_analyze_evidence(text, llm)
        if llm_result:
            analysis = merge_analysis(regex_analysis, llm_result)

    # 第三步:生成草稿和追问
    draft = generate_report_draft(text, analysis)
    questions = get_followup_questions(draft)
    return {
        'analysis': analysis,
        'draft': draft,
        'followup_questions': questions,
        'has_questions': len(questions) > 0,
    }


def llm_analyze_evidence(text: str, llm) -> Optional[Dict]:
    """使用LLM对用户输入进行自主深度分析。

    Args:
        text: 用户输入的描述或聊天记录
        llm: LLM客户端实例

    Returns:
        LLM分析结果dict,失败返回None。
    """
    prompt = f"""你是一位资深反诈分析专家。请对以下用户描述的内容进行自主深度分析。

【用户输入】
{text}

请严格按照以下JSON格式输出分析结果(不要输出其他内容,只输出JSON):

{{
    "risk_level": "extreme/high/medium/low",
    "summary": "一句话总体风险评估(50字以内)",
    "scam_types": ["识别到的诈骗类型1", "诈骗类型2"],
    "found_patterns": [
        {{
            "label": "话术特征名称(如:制造紧迫感)",
            "level": "🔴 极高危/🟠 高危/🟡 中危",
            "matched_text": "用户输入中的原文片段(20字以内)",
            "analysis": "为什么这是诈骗特征的分析(50字以内)"
        }}
    ],
    "key_findings": ["关键发现1(如:对方要求转账到安全账户)", "关键发现2"],
    "advice": "给用户的核心建议(80字以内)"
}}

分析要求:
1. 仔细阅读用户输入的每一句话,识别所有诈骗特征,不要遗漏
2. 即使没有明显关键词,也要根据语境判断是否有诈骗嫌疑
3. scam_types使用标准名称:冒充公检法诈骗/冒充客服退款诈骗/刷单返利诈骗/杀猪盘诈骗/注销校园贷诈骗/游戏交易诈骗/助学金补助诈骗/考试保过诈骗/征信修复诈骗/裸聊敲诈诈骗/培训贷诈骗/美容贷诈骗/冒充熟人诈骗/虚假投资诈骗/其他诈骗
4. found_patterns至少列出1条(如果确实没有诈骗特征,列1条说明"未发现明显诈骗特征")
5. key_findings列出用户描述中最重要的风险点
6. 只输出JSON,不要输出markdown代码块标记"""

    try:
        messages = [
            {"role": "system", "content": "你是反诈分析专家,擅长从用户描述中识别诈骗特征。只输出JSON。"},
            {"role": "user", "content": prompt},
        ]
        raw = llm.chat(messages)
        # 清理可能的markdown代码块标记
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        result = json.loads(raw)
        # 确保必要字段存在
        result.setdefault('risk_level', 'medium')
        result.setdefault('summary', '分析完成')
        result.setdefault('scam_types', [])
        result.setdefault('found_patterns', [])
        result.setdefault('key_findings', [])
        result.setdefault('advice', '')
        return result
    except Exception:
        return None


def merge_analysis(regex_result: Dict, llm_result: Optional[Dict]) -> Dict:
    """合并正则分析结果和LLM分析结果。"""
    if not llm_result:
        return regex_result

    # 合并诈骗类型(去重)
    scam_types = list(regex_result.get('scam_types', []))
    for t in llm_result.get('scam_types', []):
        if t not in scam_types:
            scam_types.append(t)

    # 合并话术特征(去重,LLM优先)
    found = []
    seen_labels = set()
    for p in llm_result.get('found_patterns', []):
        label = p.get('label', '')
        if label and label not in seen_labels:
            seen_labels.add(label)
            found.append(p)
    for p in regex_result.get('found_patterns', []):
        label = p.get('label', '')
        if label and label not in seen_labels:
            seen_labels.add(label)
            found.append(p)

    # 风险等级取更高的
    level_order = {'low': 0, 'medium': 1, 'high': 2, 'extreme': 3}
    regex_level = regex_result.get('risk_level', 'low')
    llm_level = llm_result.get('risk_level', 'low')
    risk_level = regex_level if level_order.get(regex_level, 0) >= level_order.get(llm_level, 0) else llm_level

    # 摘要优先用LLM的(更准确)
    summary = llm_result.get('summary', regex_result.get('summary', ''))

    # 添加LLM的关键发现和建议
    key_findings = llm_result.get('key_findings', [])
    advice = llm_result.get('advice', '')

    return {
        'total_patterns': len(found),
        'risk_level': risk_level,
        'found_patterns': found,
        'summary': summary,
        'scam_types': scam_types,
        'key_findings': key_findings,
        'advice': advice,
    }


def llm_generate_video_script(analysis: Dict, draft: str, llm) -> Optional[Dict]:
    """使用LLM生成小哨讲解视频脚本(3-5个幻灯片)。

    Args:
        analysis: 分析结果(risk_level/scam_types/key_findings/advice等)
        draft: 当前报案草稿(用于提取已补充的信息)
        llm: LLM客户端实例

    Returns:
        {'slides': [{'title','text','icon'}, ...]}, 失败返回None。
    """
    risk_map = {'extreme': '极高危', 'high': '高危', 'medium': '中危', 'low': '低风险'}
    risk_label = risk_map.get(analysis.get('risk_level', 'medium'), '中危')
    scam_types = '、'.join(analysis.get('scam_types', [])) or '待进一步判断'
    key_findings = '\n'.join('- ' + f for f in analysis.get('key_findings', [])) or '- 暂无'
    advice = analysis.get('advice', '') or '保持警惕,及时核实。'

    # 提取草稿中已补充的关键信息
    draft_summary = draft[:600] if draft else ''

    prompt = f"""你是"小哨"——一只蓝色小企鹅反诈助手。请根据以下诈骗分析结果,生成一个亲切温暖的讲解视频脚本(3-5个幻灯片)。

【分析结果】
- 风险等级: {risk_label}
- 诈骗类型: {scam_types}
- 关键发现:
{key_findings}
- 核心建议: {advice}

【报案草稿中的已知信息】
{draft_summary}

请生成3-5个幻灯片,要求:
1. 第一张:安抚用户情绪+总结现状(如"别慌,小哨已经帮你分析过了")
2. 中间:用大白话讲解这是什么诈骗、骗子用了什么套路、为什么危险
3. 倒数第二张:现在应该做什么(报警/保留证据/联系银行等具体行动)
4. 最后一张:温暖鼓励(如"你不是一个人,小哨一直陪着你")
5. 语气:像好朋友聊天,亲切温暖,有同理心,不说教
6. 每张幻灯片的text控制在30-60字,简短易读

严格按以下JSON格式输出(只输出JSON,不要其他内容):
{{
    "slides": [
        {{"title": "幻灯片标题(10字以内)", "text": "小哨说的话(30-60字)", "icon": "😊"}},
        {{"title": "...", "text": "...", "icon": "🛡️"}},
        {{"title": "...", "text": "...", "icon": "🚨"}},
        {{"title": "...", "text": "...", "icon": "💪"}}
    ]
}}"""

    try:
        messages = [
            {"role": "system", "content": "你是小哨,一只亲切温暖的蓝色小企鹅反诈助手。只输出JSON。"},
            {"role": "user", "content": prompt},
        ]
        raw = llm.chat(messages)
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        result = json.loads(raw)
        slides = result.get('slides', [])
        if not slides or not isinstance(slides, list):
            return None
        # 确保每个slide有必要字段
        cleaned = []
        for s in slides[:5]:
            if isinstance(s, dict) and s.get('text'):
                cleaned.append({
                    'title': s.get('title', ''),
                    'text': s.get('text', ''),
                    'icon': s.get('icon', '🐧'),
                })
        if not cleaned:
            return None
        return {'slides': cleaned}
    except Exception:
        return None


def fallback_video_script(analysis: Dict) -> Dict:
    """LLM不可用时的默认视频脚本。"""
    risk_map = {'extreme': '极高危', 'high': '高危', 'medium': '中危', 'low': '低风险'}
    risk_label = risk_map.get(analysis.get('risk_level', 'medium'), '中危')
    scam_types = '、'.join(analysis.get('scam_types', [])) or '诈骗'
    advice = analysis.get('advice', '') or '保持警惕,及时核实,不要转账。'

    return {
        'slides': [
            {'title': '别慌,有小哨', 'text': '小哨已经帮你分析过了,你的情况属于' + risk_label + '的' + scam_types + ',别担心,我们一步步来应对。', 'icon': '🐧'},
            {'title': '骗子用了什么套路', 'text': advice[:50] + ('...' if len(advice) > 50 else ''), 'icon': '🛡️'},
            {'title': '现在该做什么', 'text': '1.立即停止一切转账操作 2.保存聊天记录和转账凭证 3.拨打110或96110报警 4.联系银行申请紧急止付', 'icon': '🚨'},
            {'title': '你不是一个人', 'text': '被骗不是你的错,骗子太狡猾了。小哨一直陪着你,有问题随时来问我!', 'icon': '💪'},
        ]
    }