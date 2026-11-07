# -*- coding: utf-8 -*-
"""小哨 Web 版 - Flask 后端服务。"""

import sys
import os
import socket

# 加载 .env 配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xiaoshao import config
config.load_dotenv_if_exists()

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from xiaoshao.agent import XiaoShaoAgent
from xiaoshao.case_fetcher import get_cases, CASE_CATEGORIES, get_court_db_search_url, get_court_db_search_urls, get_court_cases, llm_generate_court_case
from xiaoshao.fraud_radar import check_fraud_source, get_scam_alerts
from xiaoshao.evidence import analyze_chat_text, generate_report_draft, analyze_and_draft, update_draft_with_answers, get_followup_questions, llm_generate_video_script, fallback_video_script
from xiaoshao.roleplay import get_personas, get_persona, evaluate_roleplay, get_randomized_system_prompt, get_personas_by_category
from xiaoshao.llm_client import LLMClient, LLMError

app = Flask(__name__, template_folder="web", static_folder="web/static")
CORS(app)

# 禁用静态文件缓存,确保前端更新即时生效
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# 每个会话一个智能体实例
sessions: dict[str, XiaoShaoAgent] = {}

# 模拟演练会话管理
roleplay_sessions: dict = {}  # {session_key: {"persona_id": str, "history": [], "llm": LLMClient}}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "消息不能为空"}), 400

    if session_id not in sessions:
        sessions[session_id] = XiaoShaoAgent()

    agent = sessions[session_id]
    reply = agent.chat(user_input)

    return jsonify({
        "reply": reply,
        "session_id": session_id,
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")
    if session_id in sessions:
        sessions[session_id].reset()
    return jsonify({"ok": True})


@app.route("/api/network-info")
def network_info():
    """返回本机局域网IP,用于生成分享二维码。"""
    addresses = []
    # 方法1:通过连接外部地址获取本机出口IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addresses.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    # 方法2:遍历主机名解析的地址
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            addr = info[4][0]
            if addr != "127.0.0.1" and addr not in addresses:
                addresses.append(addr)
    except Exception:
        pass
    port = 5000
    return jsonify({
        "port": port,
        "addresses": addresses,
        "urls": ["http://%s:%d" % (a, port) for a in addresses],
    })


@app.route("/api/fraud-cases", methods=["GET"])
def fraud_cases():
    """获取真实诈骗案例。参数: category分类id, exclude已看过的标题列表。"""
    category = request.args.get("category", "")
    exclude = request.args.getlist("exclude") if request.args.get("exclude") else []
    if not category:
        return jsonify({"error": "请选择案例分类"}), 400
    cases = get_cases(category, count=1, exclude_titles=exclude)
    return jsonify({"cases": cases, "total_local": len([c for c in CASE_CATEGORIES if c["id"] == category])})


@app.route("/api/fraud-case-categories", methods=["GET"])
def fraud_case_categories():
    """返回案例分类列表。"""
    return jsonify({"categories": CASE_CATEGORIES})


# ===== 人民法院案例库接入 =====

@app.route("/api/court-db/search-url", methods=["GET"])
def court_db_search_url():
    """获取人民法院案例库搜索链接。参数: category分类id。"""
    category = request.args.get("category", "")
    if not category:
        return jsonify({"error": "请选择分类"}), 400
    url = get_court_db_search_url(category)
    return jsonify({"url": url, "source": "人民法院案例库"})


@app.route("/api/court-db/search-urls", methods=["GET"])
def court_db_search_urls():
    """获取所有分类的人民法院案例库搜索链接。"""
    return jsonify({"urls": get_court_db_search_urls(), "base": "https://rmfyalk.court.gov.cn"})


@app.route("/api/court-db/cases", methods=["GET"])
def court_db_cases():
    """获取人民法院案例库风格的案例(LLM基于真实判例生成)。参数: category分类id。"""
    category = request.args.get("category", "")
    if not category:
        return jsonify({"error": "请选择案例分类"}), 400

    llm = LLMClient()
    cases = get_court_cases(category, count=1, llm=llm)
    search_url = get_court_db_search_url(category)

    return jsonify({
        "cases": cases,
        "court_db_url": search_url,
        "source_name": "人民法院案例库",
        "source_url": "https://rmfyalk.court.gov.cn",
    })


# ===== 反诈雷达 =====

@app.route("/api/fraud-check", methods=["POST"])
def fraud_check():
    """查询手机号/网址/APP是否为已知高风险诈骗源。"""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "请输入要查询的手机号、网址或APP名称"}), 400
    result = check_fraud_source(query)
    return jsonify(result)


@app.route("/api/scam-alerts", methods=["GET"])
def scam_alerts():
    """获取最新高发诈骗预警。"""
    return jsonify({"alerts": get_scam_alerts()})


# ===== 模拟演练 =====

@app.route("/api/roleplay-personas", methods=["GET"])
def roleplay_personas():
    """获取演练角色列表。"""
    personas = get_personas()
    return jsonify({"personas": [
        {"id": p["id"], "name": p["name"], "icon": p["icon"],
         "category": p.get("category", ""),
         "desc": p["desc"], "difficulty": p["difficulty"], "target": p["target"]}
        for p in personas
    ]})


@app.route("/api/roleplay-categories", methods=["GET"])
def roleplay_categories():
    """获取按6大分类组织的演练角色列表。"""
    grouped = get_personas_by_category()
    categories = []
    for cat_id, personas in grouped.items():
        categories.append({
            "id": cat_id,
            "personas": [
                {"id": p["id"], "name": p["name"], "icon": p["icon"],
                 "desc": p["desc"], "difficulty": p["difficulty"], "target": p["target"]}
                for p in personas
            ]
        })
    return jsonify({"categories": categories})


@app.route("/api/roleplay-start", methods=["POST"])
def roleplay_start():
    """开始模拟演练,返回骗子的开场白。"""
    data = request.get_json() or {}
    persona_id = data.get("persona_id", "")
    session_key = data.get("session_key", "default")

    persona = get_persona(persona_id)
    if not persona:
        return jsonify({"error": "未找到该演练角色"}), 400

    # 创建演练会话(使用随机变体prompt,每次骗子形象不同)
    llm = LLMClient()
    system_prompt = get_randomized_system_prompt(persona_id) or persona["system_prompt"]
    history = [{"role": "system", "content": system_prompt}]

    # 获取开场白
    try:
        # 用空用户消息触发开场白
        history.append({"role": "user", "content": "(请开始你的开场白)"})
        opening = llm.chat(history)
        history.append({"role": "assistant", "content": opening})
    except LLMError as e:
        return jsonify({"error": f"演练启动失败: {e}"}), 500

    roleplay_sessions[session_key] = {
        "persona_id": persona_id,
        "history": history,
        "llm": llm,
    }

    return jsonify({"opening": opening, "persona_name": persona["name"], "persona_icon": persona["icon"]})


@app.route("/api/roleplay-chat", methods=["POST"])
def roleplay_chat():
    """模拟演练对话:用户回复,骗子(大模型)回应。"""
    data = request.get_json() or {}
    session_key = data.get("session_key", "default")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "请输入你的回应"}), 400

    session = roleplay_sessions.get(session_key)
    if not session:
        return jsonify({"error": "演练会话不存在,请重新开始"}), 400

    persona = get_persona(session["persona_id"])
    if not persona:
        return jsonify({"error": "角色信息丢失"}), 400

    # 追加用户消息
    session["history"].append({"role": "user", "content": user_message})

    # 调用大模型获取骗子回应
    try:
        reply = session["llm"].chat(session["history"])
        session["history"].append({"role": "assistant", "content": reply})
    except LLMError as e:
        return jsonify({"error": f"演练对话失败: {e}"}), 500

    # 检查是否结束
    is_ended = "演练结束" in reply

    return jsonify({"reply": reply, "ended": is_ended})


@app.route("/api/roleplay-end", methods=["POST"])
def roleplay_end():
    """结束模拟演练,生成复盘评价。"""
    data = request.get_json() or {}
    session_key = data.get("session_key", "default")

    session = roleplay_sessions.pop(session_key, None)
    if not session:
        return jsonify({"error": "演练会话不存在"}), 400

    persona = get_persona(session["persona_id"])
    if not persona:
        return jsonify({"error": "角色信息丢失"}), 400

    evaluation = evaluate_roleplay(session["history"], persona, llm=session.get("llm"))
    return jsonify({"evaluation": evaluation})


# ===== 证据链分析(融合版) =====

# 证据分析会话管理
evidence_sessions: dict = {}  # {session_key: {"draft": str, "questions": [], "answered": []}}


@app.route("/api/analyze-evidence", methods=["POST"])
def analyze_evidence():
    """分析聊天文本中的诈骗话术模式。"""
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "请粘贴要分析的聊天内容"}), 400
    result = analyze_chat_text(text)
    return jsonify(result)


@app.route("/api/report-draft", methods=["POST"])
def report_draft():
    """根据描述生成报案材料草稿。"""
    data = request.get_json() or {}
    description = data.get("description", "")
    if not description.strip():
        return jsonify({"error": "请描述你的被骗经过"}), 400
    draft = generate_report_draft(description)
    return jsonify({"draft": draft})


@app.route("/api/evidence-analyze", methods=["POST"])
def evidence_analyze():
    """融合分析:LLM自主分析 + 正则检测 + 识别类型 + 生成草稿 + 追问问题。"""
    data = request.get_json() or {}
    text = data.get("text", "")
    session_key = data.get("session_key", "default")

    if not text.strip():
        return jsonify({"error": "请描述你遇到的情况或粘贴聊天记录"}), 400

    # 使用LLM进行自主深度分析(正则作为即时补充)
    llm = LLMClient()
    result = analyze_and_draft(text, llm=llm)

    # 保存会话
    evidence_sessions[session_key] = {
        "draft": result["draft"],
        "questions": result["followup_questions"],
        "answered": [],
        "original_text": text,
        "analysis": result["analysis"],
    }

    return jsonify(result)


@app.route("/api/evidence-answer", methods=["POST"])
def evidence_answer():
    """用户回答追问,更新草稿并返回下一批问题(1-3个)。"""
    data = request.get_json() or {}
    session_key = data.get("session_key", "default")
    answers = data.get("answers", {})  # {question_id: answer_text}

    session = evidence_sessions.get(session_key)
    if not session:
        return jsonify({"error": "分析会话不存在,请重新描述"}), 400

    # 更新草稿(纯正则操作,即时完成)
    updated_draft = update_draft_with_answers(session["draft"], answers)
    session["draft"] = updated_draft

    # 记录已回答的问题
    for qid in answers:
        if qid not in session["answered"]:
            session["answered"].append(qid)

    # 获取下一批问题(每次最多3个)
    all_remaining = get_followup_questions(updated_draft, limit=99)
    remaining = [q for q in all_remaining if q["id"] not in session["answered"]][:3]

    return jsonify({
        "draft": updated_draft,
        "remaining_questions": remaining,
        "has_questions": len(remaining) > 0,
    })


@app.route("/api/evidence-video", methods=["POST"])
def evidence_video():
    """生成小哨讲解视频(LLM生成脚本 + Pillow生成GIF视频文件)。"""
    data = request.get_json() or {}
    session_key = data.get("session_key", "default")

    session = evidence_sessions.get(session_key)
    if not session:
        return jsonify({"error": "分析会话不存在,请重新描述"}), 400

    analysis = session.get("analysis", {})
    draft = session.get("draft", "")

    # 1. LLM生成视频脚本
    llm = LLMClient()
    video_script = llm_generate_video_script(analysis, draft, llm)
    if not video_script:
        video_script = fallback_video_script(analysis)

    slides = video_script.get("slides", [])

    # PPT模式: 直接返回幻灯片数据,前端渲染PPT播放器+TTS配音
    return jsonify({"slides": slides})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)