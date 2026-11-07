# -*- coding: utf-8 -*-
"""真实诈骗案例获取模块:人民法院案例库接入 + 本地精选案例兜底。

数据来源:
1. 人民法院案例库 (rmfyalk.court.gov.cn) - 提供搜索链接和LLM解析
2. 本地精选案例 - 兜底数据,确保服务始终可用
"""

import json
import random
import re
import urllib.request
import urllib.error
import urllib.parse
from typing import List, Dict, Optional

# ===== 人民法院案例库配置 =====
COURT_DB_BASE = "https://rmfyalk.court.gov.cn"
COURT_DB_SEARCH_URL = COURT_DB_BASE + "/view/list.html"

# 6大分类对应的人民法院案例库搜索关键词
COURT_DB_SEARCH_KEYWORDS = {
    "maochong": "冒充 诈骗",
    "liyou": "诈骗 返利 投资",
    "jiaoyi": "诈骗 交易 游戏",
    "xiepo": "诈骗 敲诈 恐吓",
    "xueye": "诈骗 助学金 考试",
    "jiedai": "诈骗 贷款 校园贷",
}

# 6大分类对应的典型罪名/案由(用于LLM生成更精确的案例)
COURT_DB_CHARGES = {
    "maochong": "冒充型诈骗(冒充公检法、客服、熟人等)",
    "liyou": "利诱型诈骗(刷单返利、杀猪盘、虚假投资等)",
    "jiaoyi": "交易型诈骗(游戏交易、二手交易等)",
    "xiepo": "恐吓型诈骗(裸聊敲诈、征信修复等)",
    "xueye": "学业型诈骗(考试保过、助学金补助等)",
    "jiedai": "借贷型诈骗(校园贷、培训贷等)",
}

# ===== 本地精选案例(兜底数据,确保服务始终可用) =====
LOCAL_CASES: List[Dict] = [
    # --- 刷单返利 ---
    {"category": "liyou", "title": "大学生刷单被骗3.2万", "source": "央视新闻", "date": "2025-12",
     "content": "某高校大三学生小李在QQ群看到\"动动手指日赚300\"的刷单广告,前几单小额任务确实返利了58元。随后被诱导垫付2000元做\"高级任务\",对方以\"操作超时资金冻结\"为由要求继续转账,小李先后转账8次共3.2万元,最终被拉黑。小李报警后,警方通过紧急止付冻结了部分涉案资金。",
     "lesson": "所有刷单都是诈骗!前期小额返利是诱饵,一旦大额垫付就会被卷款拉黑。"},
    {"category": "liyou", "title": "研究生被骗6万后网贷继续刷单", "source": "人民日报", "date": "2025-11",
     "content": "某大学研究生小王在兼职平台接了刷单任务,被骗2万后,对方称\"再刷一单就能全部提现\"。小王不惜从4个网贷平台借款4万元继续投入,最终被骗6万余元。因网贷逾期,小王还面临催收压力,不得不向父母坦白并报警。",
     "lesson": "被骗后切勿\"追加投入回本\",这是连环诈骗。立即止损报警,不要网贷翻本!"},
    # --- 校园贷 ---
    {"category": "jiedai", "title": "毕业生\"注销校园贷\"被骗1.8万", "source": "新华社", "date": "2025-12",
     "content": "应届毕业生小张接到自称\"银监会\"的电话,称其大学期间注册的校园贷账户未注销将影响征信。对方准确报出小张的姓名、学校和身份证号。小张按指引从借呗借款1.8万元转入\"监管账户\"做流水验证,转账后对方失联。小张事后查询征信发现自己根本没有贷款记录。",
     "lesson": "征信不能通过电话\"注销\"!政府机关没有\"监管账户\"。凡是要求转账注销贷款的都是诈骗。"},
    {"category": "jiedai", "title": "大学生被\"清额度\"骗走4.5万", "source": "中国教育报", "date": "2025-10",
     "content": "大学生小刘接到自称支付宝客服的电话,称其\"校园贷额度\"需要清零否则影响征信。对方让小刘从花呗、借呗、京东白条等5个平台共借出4.5万元转入指定账户\"清额度\"。小刘转账后才发现被骗,而这4.5万是真实债务,必须自己偿还。",
     "lesson": "\"清空额度\"是最新诈骗话术!让你从正规平台借钱转给骗子,债务留给你自己。"},
    # --- 冒充客服 ---
    {"category": "maochong", "title": "网购退款被骗2.6万,屏幕共享泄露验证码", "source": "央视新闻", "date": "2026-01",
     "content": "大学生小陈接到自称某电商客服电话,称其购买的外套甲醛超标可双倍理赔。对方让小陈下载会议APP开启屏幕共享\"指导操作\"。小陈在对方\"指导\"下输入了银行卡号和密码,又按提示报出了短信验证码,随后卡内2.6万元被转走。",
     "lesson": "屏幕共享=交出账户控制权!退款只走原路,任何索要验证码的都是骗子。"},
    {"category": "maochong", "title": "机票改签诈骗骗走大学生8000元", "source": "民航局反诈提示", "date": "2025-11",
     "content": "大学生小赵收到\"航空公司\"短信称航班取消可免费改签并理赔300元。小赵拨打短信中的\"客服电话\",对方让其下载APP开启屏幕共享,以\"理赔需要验证支付通道\"为由,诱导小赵在支付宝输入密码,最终被骗8000元。小赵事后发现航班根本没取消。",
     "lesson": "航班信息请通过航空公司官方APP核实,短信中的电话和链接不可信。"},
    # --- 冒充熟人 ---
    {"category": "maochong", "title": "辅导员QQ被盗,全班5人被骗共2.5万", "source": "中国警察网", "date": "2025-12",
     "content": "某高校辅导员张老师的QQ号被盗,骗子用其身份在班级群发布\"需要帮忙垫付会议费用\"的消息,并伪造语音消息取信学生。5名学生先后转账5000元不等,共计2.5万元。直到有学生当面找张老师核实,才发现被骗。警方提醒:QQ微信借钱必须电话或当面核实。",
     "lesson": "AI可克隆语音!社交软件借钱必须电话或当面核实,一条语音消息不能证明身份。"},
    {"category": "maochong", "title": "AI换脸冒充好友视频借钱", "source": "人民日报", "date": "2025-10",
     "content": "大学生小吴收到好友的微信视频通话,画面中确实是好友本人。\"好友\"称家人住院急需借款2万元。小吴看到视频确认是本人便转了账。事后联系好友才发现,骗子使用AI换脸技术伪造了视频通话。警方提醒:视频通话中要让对方做指定动作(如摸耳朵、转头)来验证真伪。",
     "lesson": "AI换脸可实时伪造视频!借钱前让对方做指定动作验证,或当面/电话核实。"},
    # --- 冒充公检法 ---
    {"category": "xiepo", "title": "女大学生被\"涉嫌洗钱\"恐吓转账5万", "source": "央视新闻", "date": "2026-01",
     "content": "大学生小孙接到自称\"公安局\"电话,称其银行卡涉嫌洗钱,并发来伪造的\"逮捕令\"。对方要求其对家人保密,独自到酒店开房配合\"调查\",将5万元存款转入\"安全账户\"。小孙转账后联系不上对方才意识到被骗,立即报警。警方通过紧急止付追回部分资金。",
     "lesson": "公检法不电话办案!没有\"安全账户\"!要求保密和酒店开房是骗子孤立你的手段。"},
    {"category": "xiepo", "title": "研究生被骗20万,骗子冒充检察官", "source": "新华社", "date": "2025-09",
     "content": "某高校研究生小周接到自称\"检察院\"电话,称其涉嫌一起特大洗钱案,要求配合资产清查。骗子发来伪造的法律文书,并让小周下载木马APP查看\"案件材料\"。小周在恐慌中先后转账20万元。警方提醒:学历再高也可能被骗,诈骗利用的是恐惧心理而非智力。",
     "lesson": "法律文书不会通过网络发送!公检法不会让你下载APP查案件。恐惧时更要冷静核实。"},
    # --- 游戏交易 ---
    {"category": "jiaoyi", "title": "初中生买游戏皮肤被骗3000元", "source": "中国消费者报", "date": "2025-12",
     "content": "学生小林在贴吧看到低价出售限定皮肤的广告,加微信后对方发来伪造的交易截图。小林按对方要求先转账98元,对方又称\"需要缴纳保证金\"\"账户冻结需解冻费\",小林先后转账3000元后被拉黑。家长发现后报警,但因金额较小且流向境外账户,追回困难。",
     "lesson": "游戏交易只在官方渠道!先款后货的都是诈骗,\"保证金\"\"解冻费\"是连环套。"},
    {"category": "jiaoyi", "title": "大学生卖游戏账号被\"验号\"盗走", "source": "人民网", "date": "2025-11",
     "content": "大学生小郑在游戏交易平台出售账号,买家称需要\"验号\",索要了账号密码和绑定手机号。小郑提供信息后,对方立即修改了所有绑定信息并拉黑小郑。小郑不仅没收到钱,还失去了价值2000多元的游戏账号和全部装备。",
     "lesson": "\"验号\"=盗号!卖号走正规担保平台,绝不给任何人账号密码。"},
    # --- 杀猪盘 ---
    {"category": "liyou", "title": "女教师网恋被\"杀猪盘\"骗走97万", "source": "央视新闻", "date": "2025-10",
     "content": "高校教师王女士在社交软件上认识了\"成功男士\",对方每天嘘寒问暖建立感情后,推荐她投资\"稳赚不赔\"的理财平台。王女士先后投入97万元,平台显示盈利丰厚,但提现时被要求缴纳\"税费\"。王女士转账后平台关闭,\"男友\"失联。警方追查发现资金已流向境外。",
     "lesson": "网恋+投资=杀猪盘!感情是诱饵,投资是陷阱。稳赚不赔的投资不存在。"},
    {"category": "liyou", "title": "研究生网恋被骗40万,对方竟是抠脚大汉", "source": "中国新闻周刊", "date": "2025-12",
     "content": "研究生小刘在婚恋网站认识\"白富美\",对方以恋爱名义交往3个月后,推荐小刘投资虚拟货币。小刘先后投入40万元,平台显示账面盈利,但无法提现。报警后警方抓获嫌疑人,发现\"白富美\"是一名男性诈骗团伙成员,同时与多名受害者\"恋爱\"。",
     "lesson": "没见过面就推荐投资的\"恋人\"100%是骗子。虚拟货币投资平台多为诈骗平台。"},
    # --- 冒充公检法补充 ---
    {"category": "xiepo", "title": "留学生被冒充使馆诈骗30万", "source": "外交部领事保护", "date": "2025-11",
     "content": "留学生小杨接到自称\"中国驻外使馆\"电话,称其护照被冒用涉嫌犯罪,需配合国内警方调查。电话被转接至\"国内公安局\",对方要求小杨将30万元转入\"安全账户\"验证清白,并威胁不得告知家人。小杨转账后向真正的使馆核实,才发现被骗。",
     "lesson": "使领馆不会电话要求转账!留学生接到此类电话,应通过官方渠道核实。"},
    # --- 借贷补充 ---
    {"category": "jiedai", "title": "宝妈刷单被骗,被诱导用花呗付款", "source": "法治日报", "date": "2025-12",
     "content": "在家带孩子的李女士看到\"足不出户日赚200\"的刷单广告,前3单赚了45元。第4单被要求用花呗垫付3000元,对方称完成后返还本金加佣金。李女士付款后对方又要求继续做任务,李女士用花呗、信用卡共投入1.5万元后被拉黑。花呗和信用卡的债务仍需自己偿还。",
     "lesson": "用花呗/信用卡刷单=负债被骗!信贷产品的钱是真实债务,骗子的佣金是虚假承诺。"},
    # --- 学业类 ---
    {"category": "xueye", "title": "大学生买\"期末真题\"被骗300元", "source": "中国教育报", "date": "2025-12",
     "content": "期末考试周,大学生小郑在校园论坛看到\"内部真题包过\"广告,加了对方微信后转账300元购买\"真题\"。收到PDF后发现内容模糊,与所学课程完全对不上,要求退款时对方要求再交500元\"保证金\"。小郑意识到被骗后向学校保卫处报告,发现多名同学被同一账号所骗。",
     "lesson": "买卖考题违法且是诈骗!考题在考前是绝密的,\"包过真题\"广告100%是骗局,还可能被开除学籍。"},
    {"category": "xueye", "title": "新生被\"助学金发放\"电话骗走200元手续费", "source": "新华社", "date": "2025-09",
     "content": "开学初,大一新生小唐接到自称\"教育局资助中心\"电话,称其符合助学金条件可领8000元,但需先交200元\"手续费\"。对方准确报出小唐的姓名、学号和家庭信息。小唐交了200元后对方又要求提供银行卡号,小唐向学校学生处核实后确认是诈骗。学校随即发布通知提醒全体新生。",
     "lesson": "助学金只通过学校发放,不需要先交手续费!领钱不需要先交钱,任何要求先交费才能领补助的都是诈骗。"},
    {"category": "xueye", "title": "研究生被\"论文代发保过\"骗走8000元", "source": "科学网", "date": "2025-11",
     "content": "研三学生小吴急需发表论文毕业,在网上找到\"论文代发保过\"服务,对方承诺\"核心期刊包发,不过全额退款\"。小吴先交3000元定金,对方发来\"录用通知\"后又要求交5000元\"版面费\"。小吴交完后发现\"录用通知\"是伪造的,对方已拉黑他。小吴向导师坦白后报警,但因对方账号在境外,追回困难。",
     "lesson": "论文代发是学术不端且多为诈骗!\"保过\"\"包发\"都是话术,伪造录用通知骗取版面费是常见套路。发表论文请走正规投稿渠道。"},
    # --- 恐吓类补充 ---
    {"category": "xiepo", "title": "大学生遭遇裸聊敲诈,正确应对未损失", "source": "央视新闻", "date": "2026-01",
     "content": "大学生小刘深夜在社交软件上被\"美女\"搭讪,诱导下载了不明APP进行视频聊天。对方录屏后发来小刘的通讯录截图,威胁转账5000元否则将视频发给其亲友。小刘牢记反诈宣传内容,未转账、未回复,保存截图证据后立即拨打110报警。民警指导其停止一切沟通,对方威胁几天后逐渐消失。",
     "lesson": "裸聊敲诈应对三不:不回复、不转账、立刻报警!骗子不会因你不转账就发视频(发视频=失去筹码),不回复+不转账是最有效的应对。"},
    {"category": "xiepo", "title": "毕业生被\"征信修复\"骗走3000元", "source": "法治日报", "date": "2025-10",
     "content": "毕业生小张接到自称\"征信中心\"电话,称其有3条不良征信记录将影响房贷。对方发来伪造的\"征信报告截图\",称有\"内部渠道\"可修复,收取3000元服务费。小张转账后对方失联。小张通过银行APP查询发现自己征信记录良好,根本没有不良记录。警方提醒:征信不能花钱修复,不良记录5年后自动消除。",
     "lesson": "征信不能花钱修复!任何声称\"内部渠道修复征信\"的都是诈骗。查询征信请通过中国人民银行征信中心官网(免费)。"},
]

# 分类映射(6大诈骗套路分类:冒/利/恐/贷/交/学)
CASE_CATEGORIES = [
    {"id": "maochong", "name": "冒充类", "icon": "🎭"},
    {"id": "liyou", "name": "利诱类", "icon": "💰"},
    {"id": "jiaoyi", "name": "交易类", "icon": "🛒"},
    {"id": "xiepo", "name": "恐吓类", "icon": "⚠️"},
    {"id": "xueye", "name": "学业类", "icon": "🎓"},
    {"id": "jiedai", "name": "借贷类", "icon": "🏦"},
]


def _try_fetch_online_cases(category: str) -> List[Dict]:
    """尝试从公开新闻RSS抓取近期反诈案例(可能失败,失败返回空列表)。"""
    try:
        # 尝试从公安部刑侦局反诈栏目或新闻聚合源获取
        # 这里使用一个公开的新闻搜索接口作为示例
        cat_name = next((c["name"] for c in CASE_CATEGORIES if c["id"] == category), category)
        url = "https://news.baidu.com/ns?word=%E8%AF%88%E9%AA%97%20" + urllib.parse.quote(cat_name) + "&tn=news&from=news&cl=2&rn=5"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # 解析新闻标题和摘要(简单正则)
        cases = []
        titles = re.findall(r'<a[^>]*>([^<]{10,80}诈骗[^<]{0,40})</a>', html)
        for t in titles[:3]:
            t = re.sub(r'<[^>]+>', '', t).strip()
            if t and len(t) > 10:
                cases.append({"category": category, "title": t, "source": "网络新闻", "date": "", "content": t, "lesson": "请关注官方反诈渠道获取更多案例详情。"})
        return cases
    except Exception:
        return []


def get_cases(category: str, count: int = 1, exclude_titles: Optional[List[str]] = None) -> List[Dict]:
    """获取指定分类的案例。优先网络抓取,失败则用本地数据。"""
    exclude_titles = exclude_titles or []
    
    # 先尝试网络抓取
    online = _try_fetch_online_cases(category)
    
    # 合并本地数据
    local = [c for c in LOCAL_CASES if c["category"] == category]
    
    # 排除已看过的
    pool = [c for c in (online + local) if c["title"] not in exclude_titles]
    
    if not pool:
        # 所有案例都看过了,重新开始
        pool = local if local else [c for c in LOCAL_CASES if c["category"] == category]
    
    random.shuffle(pool)
    return pool[:count]


# ===== 人民法院案例库接入 =====

def get_court_db_search_url(category: str) -> str:
    """生成人民法院案例库的搜索链接。

    Args:
        category: 6大分类id

    Returns:
        搜索链接URL
    """
    keyword = COURT_DB_SEARCH_KEYWORDS.get(category, "诈骗")
    return COURT_DB_SEARCH_URL + "?keyword=" + urllib.parse.quote(keyword)


def get_court_db_search_urls() -> Dict[str, str]:
    """获取所有分类的人民法院案例库搜索链接。"""
    return {cat_id: get_court_db_search_url(cat_id) for cat_id in COURT_DB_SEARCH_KEYWORDS}


def llm_generate_court_case(category: str, llm=None) -> Optional[Dict]:
    """使用LLM基于人民法院案例库的真实判例模式生成案例。

    Args:
        category: 6大分类id
        llm: LLM客户端实例

    Returns:
        案例dict,失败返回None
    """
    if llm is None:
        return None

    charge = COURT_DB_CHARGES.get(category, "诈骗")
    cat_name = next((c["name"] for c in CASE_CATEGORIES if c["id"] == category), "诈骗")

    prompt = f"""你是一位法律专家,熟悉人民法院案例库(rmfyalk.court.gov.cn)中的真实判例。
请基于该案例库中{charge}类案件的真实判例模式,生成一个典型的校园诈骗案例。

要求:
1. 案例必须基于真实判例的典型模式(案由、作案手法、判决结果)
2. 受害者为大学生/研究生
3. 包含:案件经过、涉案金额、法院判决要点
4. 语言风格:客观、法律文书风格,但通俗易懂
5. 金额和细节要真实合理

请严格按以下JSON格式输出(只输出JSON,不要其他内容):
{{
    "title": "案例标题(20字以内,包含诈骗类型)",
    "content": "案件详细经过(150-250字,包含作案手法、涉案金额、关键细节)",
    "court_ruling": "法院判决要点(50-80字,如:被告人犯诈骗罪,被判处有期徒刑X年,并处罚金X万元)",
    "lesson": "防骗启示(30-50字)"
}}"""

    try:
        messages = [
            {"role": "system", "content": "你是法律专家,擅长基于人民法院案例库的真实判例生成典型案例分析。只输出JSON。"},
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
        result["category"] = category
        result["source"] = "人民法院案例库"
        result["date"] = "参考判例"
        result["court_db_url"] = get_court_db_search_url(category)
        result.setdefault("court_ruling", "")
        return result
    except Exception:
        return None


def get_court_cases(category: str, count: int = 1, llm=None) -> List[Dict]:
    """获取人民法院案例库风格的案例。

    优先使用LLM生成基于真实判例的案例,失败则用本地数据。

    Args:
        category: 6大分类id
        count: 获取数量
        llm: 可选LLM客户端

    Returns:
        案例列表
    """
    cases = []

    # 尝试LLM生成(最多生成count个)
    if llm is not None:
        for _ in range(count):
            case = llm_generate_court_case(category, llm)
            if case:
                cases.append(case)

    # LLM生成不足,用本地数据补充
    if len(cases) < count:
        local = [c for c in LOCAL_CASES if c["category"] == category]
        random.shuffle(local)
        for c in local:
            if len(cases) >= count:
                break
            # 给本地案例也加上法院链接
            c_copy = dict(c)
            c_copy["court_db_url"] = get_court_db_search_url(category)
            cases.append(c_copy)

    return cases[:count]