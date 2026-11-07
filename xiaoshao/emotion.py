# -*- coding: utf-8 -*-
"""情绪检测与心理急救模块。

检测用户语言中的恐慌、绝望、自责、焦虑等情绪,触发共情式安抚。
"""

from typing import Dict, Optional

# ===== 情绪关键词库 =====
# 级别: critical(可能有自杀倾向/极度绝望) > panic(正在被骗/极度恐慌) > distress(焦虑自责)

CRITICAL_KEYWORDS = [
    '不想活', '活不下去', '想死', '自杀', '跳楼', '了结', '没脸活',
    '对不起父母', '还不上', '还不了', '走投无路', '一辈子完了', '毁了我一生',
    '不想见人', '没救了', '钱全没了', '全部积蓄', '倾家荡产',
]

PANIC_KEYWORDS = [
    '正在转账', '正在操作', '马上要转', '对方让我转', '他催我转',
    '验证码发了', '已经给了验证码', '屏幕共享中', '正在共享屏幕',
    '来不及了', '马上截止', '快帮我', '怎么办啊', '急急急',
    '已经转了', '钱转出去了', '刚转完', '转了钱',
]

DISTRESS_KEYWORDS = [
    '被骗了', '我上当了', '我好蠢', '我怎么这么傻', '太后悔了',
    '不敢告诉', '不敢跟家里说', '不敢报警', '怕被笑话',
    '压力好大', '睡不着', '吃不下', '崩溃', '绝望',
    '自责', '恨自己', '都怪我', '我太天真',
    '贷款', '网贷', '借呗', '花呗还不上',
]


def detect_emotion(text: str) -> Optional[Dict]:
    """检测用户输入中的情绪信号。

    Returns:
        None: 无明显情绪信号
        {'level': 'critical|panic|distress', 'keywords': [...], 'prefix': str}
        prefix 为应插入到回复最前面的安抚文本。
    """
    if not text:
        return None

    # 按优先级检测: critical > panic > distress
    critical_hits = [kw for kw in CRITICAL_KEYWORDS if kw in text]
    if critical_hits:
        return {
            'level': 'critical',
            'keywords': critical_hits,
            'prefix': _critical_response(),
        }

    panic_hits = [kw for kw in PANIC_KEYWORDS if kw in text]
    if panic_hits:
        return {
            'level': 'panic',
            'keywords': panic_hits,
            'prefix': _panic_response(),
        }

    distress_hits = [kw for kw in DISTRESS_KEYWORDS if kw in text]
    if distress_hits:
        return {
            'level': 'distress',
            'keywords': distress_hits,
            'prefix': _distress_response(),
        }

    return None


def _critical_response() -> str:
    """极度绝望/自杀倾向的紧急安抚。"""
    return (
        '🫂 **小哨想对你说**\n'
        '我知道你现在非常痛苦,但请先听我说完:\n'
        '1️⃣ **这不是你的错。** 现在的骗术经过专业设计,连律师、教授都会中招,你不是蠢,你是被算计了。\n'
        '2️⃣ **钱可以再赚,你的人生不能重来。** 被骗的钱是沉没成本,但你的未来还有无限可能。\n'
        '3️⃣ **你现在最需要的不是自责,而是行动。** 报警越快,追回的可能性越大。\n\n'
        '📞 **请立即拨打:**\n'
        '• 110 报警(说清被骗经过和转账时间)\n'
        '• 96110 全国反诈专线\n'
        '• 全国心理援助热线: 400-161-9995\n\n'
        '如果你觉得撑不住了,请打上面最后一个电话,有人24小时在听。\n\n'
    )


def _panic_response() -> str:
    """正在被骗/极度恐慌的紧急止损SOP。"""
    return (
        '🚨 **停止操作!立刻做这三件事!** 🚨\n'
        '1️⃣ **挂断电话/退出聊天** — 现在就做,不要犹豫\n'
        '2️⃣ **不要转账、不要给验证码、不要开屏幕共享** — 任何要求你做这些的都是骗子\n'
        '3️⃣ **拨打 110 或 96110** — 告诉警察:你正在被诈骗,对方要求你转账\n\n'
        '⏱️ **黄金止付时间只有几分钟到几小时,每一秒都很重要!**\n\n'
    )


def _distress_response() -> str:
    """焦虑/自责的共情安抚。"""
    return (
        '🫂 **小哨理解你的感受**\n'
        '被骗后感到自责、害怕、睡不着,这些反应都很正常。但请记住:\n'
        '• **这不是你的错** — 骗术经过专业团队设计,利用的是人性弱点,不是你的智商问题\n'
        '• **越早行动越好** — 现在最重要的是止损和报警,不是自责\n'
        '• **你并不孤单** — 每天都有很多人被骗,说出来才能得到帮助\n\n'
    )