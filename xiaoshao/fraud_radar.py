# -*- coding: utf-8 -*-
"""反诈雷达模块:黑名单查询 + 最新骗局预警。

数据来源:国家反诈中心公开通报、各地公安反诈提示、安全厂商公开报告。
注:本地黑名单为精选高风险样本,实际查询建议结合官方渠道核实。
"""

import re
from typing import Dict, Optional

# ===== 已知高风险诈骗号码段(虚拟运营商/境外/标记高频) =====
HIGH_RISK_PHONE_PATTERNS = [
    {'pattern': r'^170\d{8}$', 'risk': 'medium', 'reason': '170号段为虚拟运营商,被标记为诈骗/骚扰的频率较高'},
    {'pattern': r'^171\d{8}$', 'risk': 'medium', 'reason': '171号段为虚拟运营商,被标记为诈骗/骚扰的频率较高'},
    {'pattern': r'^162\d{8}$', 'risk': 'medium', 'reason': '162号段为虚拟运营商,被标记频率较高'},
    {'pattern': r'^165\d{8}$', 'risk': 'medium', 'reason': '165号段为虚拟运营商,被标记频率较高'},
    {'pattern': r'^166\d{8}$', 'risk': 'low', 'reason': '166号段部分为虚拟运营商,需结合通话内容判断'},
]

# ===== 已知高风险网址特征 =====
HIGH_RISK_URL_PATTERNS = [
    {'pattern': r'\.top$', 'risk': 'medium', 'reason': '.top域名因注册便宜,被大量诈骗网站使用'},
    {'pattern': r'\.xyz$', 'risk': 'medium', 'reason': '.xyz域名因注册便宜,被大量诈骗网站使用'},
    {'pattern': r'\.cc$', 'risk': 'medium', 'reason': '.cc域名常被仿冒官网的钓鱼网站使用'},
    {'pattern': r'\.tk$|\.ml$|\.ga$|\.cf$', 'risk': 'high', 'reason': '免费域名,几乎仅被钓鱼/诈骗网站使用'},
    {'pattern': r'^(https?://)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'risk': 'high',
     'reason': '直接使用IP地址访问的网站,极大概率是钓鱼网站(正规网站都用域名)'},
]

# ===== 已知高风险APP名称/特征 =====
HIGH_RISK_APPS = {
    '安全账户': {'risk': 'high', 'reason': '不存在「安全账户」APP!这是冒充公检法诈骗的标志性话术'},
    '理赔通': {'risk': 'high', 'reason': '假冒理赔APP,实为木马,窃取银行卡信息'},
    '退款中心': {'risk': 'high', 'reason': '假冒退款APP,客服诈骗专用'},
    '清退办': {'risk': 'high', 'reason': '假冒P2P清退APP,针对投资人诈骗'},
    '数字人民币钱包': {'risk': 'high', 'reason': '假冒数字人民币APP!官方只有「数字人民币(试点版)」'},
    '会议宝': {'risk': 'high', 'reason': '诱导屏幕共享的会议APP,可实时窥探你的手机操作'},
    '云视讯': {'risk': 'medium', 'reason': '常被用于诱导屏幕共享,正规使用需确认对方身份'},
    '刷单宝': {'risk': 'high', 'reason': '刷单诈骗专用APP,前期返利后期卷款'},
    '兼职猫': {'risk': 'medium', 'reason': '需核实是否为正规兼职平台,大量仿冒APP存在'},
    '投资达人': {'risk': 'high', 'reason': '虚假投资理财APP,杀猪盘专用'},
    '币圈大佬': {'risk': 'high', 'reason': '虚拟货币诈骗APP,后台可控涨跌'},
    '助学贷': {'risk': 'high', 'reason': '假冒助学贷款APP,校园贷诈骗专用'},
    '注销校园贷': {'risk': 'high', 'reason': '不存在此APP!注销校园贷诈骗的标志'},
    '极速退款': {'risk': 'high', 'reason': '假冒退款APP,索要验证码后盗刷'},
}

# ===== 本周高发诈骗预警 =====
SCAM_ALERTS = [
    {
        'title': 'AI换脸视频通话诈骗',
        'level': '🔴 极高危',
        'date': '本周高发',
        'desc': '骗子利用AI换脸技术伪造好友/亲人的视频通话,以紧急事由借钱。已有大学生被骗数万元。',
        'tip': '视频通话中让对方做指定动作(摸耳朵/转头)验证,借钱必须电话或当面核实。'
    },
    {
        'title': '屏幕共享盗刷诈骗',
        'level': '🔴 极高危',
        'date': '本周高发',
        'desc': '冒充客服/公检法,诱导下载会议APP开启屏幕共享,实时窥探密码和验证码,直接盗刷银行卡。',
        'tip': '任何要求屏幕共享的「客服」都是骗子!屏幕共享=交出手机控制权。'
    },
    {
        'title': '会员自动扣费取消诈骗',
        'level': '🟠 高发',
        'date': '本周高发',
        'desc': '谎称你开通了会员即将扣费,诱导下载APP或索要验证码「取消」,实则盗刷。',
        'tip': '挂断电话,自己打开官方APP查看会员状态,一切以APP显示为准。'
    },
    {
        'title': '注销校园贷诈骗',
        'level': '🟠 高发',
        'date': '持续高发',
        'desc': '冒充银监会/支付宝客服,以「注销校园贷记录影响征信」为由,诱导从网贷平台借款转入「监管账户」。',
        'tip': '征信不能电话注销!政府机关没有「监管账户」。凡是要求转账注销贷款的都是诈骗。'
    },
    {
        'title': '虚假购物退款理赔',
        'level': '🟡 中高发',
        'date': '本周高发',
        'desc': '冒充快递/电商客服,谎称包裹丢失或商品有问题可理赔,诱导加QQ、填银行卡、点钓鱼链接。',
        'tip': '退款只走原路!快递理赔请通过官方APP核实物流,不加QQ不点链接。'
    },
]


def check_fraud_source(query: str) -> Dict:
    """查询手机号/网址/APP名称是否为已知高风险诈骗源。

    Returns:
        {'type': 'phone|url|app|unknown', 'risk': 'high|medium|low|safe',
         'reason': str, 'advice': str}
    """
    query = query.strip()

    # 检测手机号(含境外+号开头)
    clean = re.sub(r'[\s\-]', '', query)
    if re.match(r'^\+?\d{7,15}$', clean) or re.match(r'^00\d{6,}$', clean):
        return _check_phone(query)

    # 检测网址
    if re.search(r'(https?://|www\.|\.com|\.cn|\.net|\.org|\.top|\.xyz|\.cc)', query, re.IGNORECASE):
        return _check_url(query)

    # 检测APP名称
    return _check_app(query)


def _check_phone(phone: str) -> Dict:
    """检查手机号风险。"""
    clean = re.sub(r'[\s\-]', '', phone)

    # 境外号码
    if clean.startswith('+') or clean.startswith('00'):
        return {
            'type': 'phone', 'risk': 'high',
            'reason': '这是一个境外来电号码。大量跨境诈骗电话来自境外,冒充公检法、使馆、客服的诈骗高发。',
            'advice': '不要接听陌生境外来电!如确有海外联系需求,通过微信/邮件等可信渠道核实。'
        }

    # 虚拟运营商号段
    for p in HIGH_RISK_PHONE_PATTERNS:
        if re.match(p['pattern'], clean):
            return {
                'type': 'phone', 'risk': p['risk'],
                'reason': '该号码属于' + p['reason'] + '。号段本身不代表一定是诈骗,但需结合通话内容判断。',
                'advice': '如果对方谈到转账、验证码、安全账户、屏幕共享,立即挂断!拨打96110核实。'
            }

    # 正常号段
    if re.match(r'^1[3-9]\d{9}$', clean):
        return {
            'type': 'phone', 'risk': 'low',
            'reason': '该号码属于常规手机号段,未被列入高风险号段库。但请注意:骗子可以使用改号软件伪装任意号码!',
            'advice': '号段正常不代表来电可信。关键看内容:涉及金钱、验证码、屏幕共享的,一律挂断核实。'
        }

    return {
        'type': 'phone', 'risk': 'unknown',
        'reason': '无法识别该号码格式。',
        'advice': '建议拨打96110反诈专线核实。'
    }


def _check_url(url: str) -> Dict:
    """检查网址风险。"""
    url_lower = url.lower().strip()

    for p in HIGH_RISK_URL_PATTERNS:
        if re.search(p['pattern'], url_lower):
            risk = p['risk']
            if risk == 'high':
                advice = '极高风险!不要点击、不要输入任何信息!正规网站不会使用此类域名。'
            elif risk == 'medium':
                advice = '较高风险!请勿在此网站输入账号密码或个人信息。如需访问,请通过官方APP进入。'
            else:
                advice = '需谨慎!请仔细核对是否为仿冒官网(对比官方域名拼写)。'
            return {
                'type': 'url', 'risk': risk,
                'reason': p['reason'],
                'advice': advice
            }

    # 检查是否包含常见仿冒关键词
    fake_map = {
        'alipay': 'alipay.com', 'taobao': 'taobao.com', 'jd': 'jd.com',
        'weixin': 'weixin.qq.com', 'wechat': 'wechat.com',
        'icbc': 'icbc.com.cn', 'ccb': 'ccb.com', 'abc': 'abchina.com'
    }
    for kw, official_domain in fake_map.items():
        if kw in url_lower and official_domain not in url_lower:
            return {
                'type': 'url', 'risk': 'high',
                'reason': '该网址包含「' + kw + '」但不是官方域名!极大概率是仿冒钓鱼网站。',
                'advice': '不要访问!请通过官方APP或搜索引擎认证入口进入。'
            }

    return {
        'type': 'url', 'risk': 'low',
        'reason': '未在本地黑名单中匹配到高风险特征。但这不代表一定安全,新钓鱼网站每天都在产生。',
        'advice': '访问前请核对域名拼写,不在不明网站输入账号密码。有疑问拨打96110。'
    }


def _check_app(name: str) -> Dict:
    """检查APP名称风险。"""
    name_clean = name.strip()

    for app_name, info in HIGH_RISK_APPS.items():
        if app_name in name_clean or name_clean in app_name:
            return {
                'type': 'app', 'risk': info['risk'],
                'reason': info['reason'],
                'advice': '不要下载安装!如已安装,立即卸载并修改相关密码。拨打96110报告。'
            }

    return {
        'type': 'app', 'risk': 'unknown',
        'reason': '未在黑名单库中找到「' + name_clean + '」。诈骗APP名称每天都在变化,不在黑名单不等于安全。',
        'advice': '下载APP请只通过手机官方应用商店。任何通过链接/二维码安装的APP都要高度警惕。'
    }


def get_scam_alerts() -> list:
    """获取最新高发诈骗预警。"""
    return SCAM_ALERTS