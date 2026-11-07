# -*- coding: utf-8 -*-
"""校园反诈助手「小哨」- 主程序入口。

用法:
    python -m xiaoshao          # 在项目根目录下运行
    python xiaoshao/main.py     # 直接运行(自动处理包导入)
"""

import sys
import os

# 修复 Windows cmd 中文/emoji 编码问题(GBK 无法显示 emoji 会报错)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 允许直接以 python xiaoshao/main.py 方式运行
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from xiaoshao import config, prompts
    from xiaoshao.agent import XiaoShaoAgent
else:
    from . import config, prompts
    from .agent import XiaoShaoAgent


# 本地命令(无需调用大模型)
LOCAL_COMMANDS = {"帮助", "help", "h", "?", "退出", "quit", "exit", "q",
                  "清空", "重置", "reset", "类型", "列表", "types",
                  "紧急", "电话", "emergency", "关于", "about"}


def print_banner():
    """打印启动横幅。"""
    print(prompts.WELCOME_TEXT)


from typing import Optional
def handle_local_command(agent: XiaoShaoAgent, user_input: str) -> Optional[str]:
    """处理本地命令,返回回复文本;非本地命令返回 None。

    Args:
        agent: 智能体实例。
        user_input: 用户输入(已去除首尾空白)。

    Returns:
        命令回复文本,或 None(表示不是本地命令,需走大模型)。
    """
    cmd = user_input.lower()

    if cmd in ("帮助", "help", "h", "?"):
        return prompts.HELP_TEXT

    if cmd in ("退出", "quit", "exit", "q"):
        return "__EXIT__"

    if cmd in ("清空", "重置", "reset"):
        agent.reset()
        return "🔄 对话已清空,我们重新开始!有什么可疑场景,尽管告诉小哨~"

    if cmd in ("类型", "列表", "types"):
        return agent.list_fraud_types()

    if cmd in ("紧急", "电话", "emergency"):
        return agent.show_emergency()

    if cmd in ("关于", "about"):
        return (
            "🛡️ 关于小哨\n"
            "────────────────\n"
            "小哨是一位校园反诈助手智能体,基于大语言模型构建。\n"
            "核心能力:场景识别 → 风险分析 → 应对建议\n"
            "知识库覆盖 12 类常见校园诈骗,并支持本地高危关键词即时预警。\n"
            "⚠️ 小哨的分析仅供参考,紧急情况请拨打 110 / 96110。"
        )

    # 支持「详情 刷单」这类本地知识查询
    if cmd.startswith(("详情 ", "查询 ")):
        keyword = user_input[3:].strip()
        if keyword:
            return agent.get_fraud_detail(keyword)
        return "请指定要查询的诈骗类型,例如:「详情 刷单」"

    return None


def main():
    """主交互循环。"""
    # 加载 .env 配置
    config.load_dotenv_if_exists()

    # 校验配置
    missing = config.validate()
    if missing:
        print("⚠️ 配置不完整,缺少以下环境变量:" + "、".join(missing))
        print("请复制 env.example 为 .env 并填写,或直接设置环境变量。")
        print("示例(Windows cmd):")
        print('  set LLM_API_KEY=sk-xxxx')
        print('  set LLM_BASE_URL=https://api.openai.com/v1')
        print('  set LLM_MODEL=gpt-4o-mini')
        print()
        choice = input("是否仍要进入对话?(y/n): ").strip().lower()
        if choice not in ("y", "yes"):
            return

    agent = XiaoShaoAgent()
    print_banner()

    while True:
        try:
            user_input = input("🧑 你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见!记得:不轻信、不转账、不透露验证码!")
            break

        if not user_input:
            continue

        # 1. 优先处理本地命令
        local_reply = handle_local_command(agent, user_input)
        if local_reply == "__EXIT__":
            print("\n👋 再见!记得:不轻信、不转账、不透露验证码!小哨随时守护你~")
            break
        if local_reply is not None:
            print(f"\n🛡️ 小哨 > {local_reply}\n")
            continue

        # 2. 调用智能体(大模型分析)
        print("\n🛡️ 小哨正在分析中..." + " (首次响应可能稍慢)\n")
        try:
            reply = agent.chat(user_input)
        except Exception as e:
            reply = f"⚠️ 发生未知错误:{e}\n🚨 紧急情况请拨打 110 或 96110!"
        print(f"🛡️ 小哨 > {reply}\n")


if __name__ == "__main__":
    main()