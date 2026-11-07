# -*- coding: utf-8 -*-
"""配置管理模块:管理大模型 API 连接配置和智能体运行参数。"""

import os

# ============ 大模型 API 配置 ============
# 支持 OpenAI 兼容格式(OpenAI / DeepSeek / 通义千问 / 京东言犀等均可)
# 优先从环境变量读取,也可直接修改下方默认值

# API 基础地址(例如:https://api.openai.com/v1)
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# API 密钥
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

# 模型名称(例如:gpt-4o-mini / deepseek-chat / qwen-plus)
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 请求超时时间(秒)
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

# ============ 智能体行为配置 ============

# 每次分析时携带的历史对话轮数(上下文记忆)
MAX_HISTORY_ROUNDS: int = int(os.getenv("MAX_HISTORY_ROUNDS", "5"))

# 生成温度(0~1,越低越稳定,反诈场景建议偏低)
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# 最大生成 token 数
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))


def validate() -> list:
    """校验配置是否完整,返回缺失项列表。"""
    missing = []
    if not LLM_API_KEY:
        missing.append("LLM_API_KEY")
    if not LLM_BASE_URL:
        missing.append("LLM_BASE_URL")
    if not LLM_MODEL:
        missing.append("LLM_MODEL")
    return missing


def load_dotenv_if_exists():
    """若当前目录存在 .env 文件,则加载其中的环境变量(轻量实现,无需额外依赖)。"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    # 重新读取环境变量
    global LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT
    global MAX_HISTORY_ROUNDS, LLM_TEMPERATURE, LLM_MAX_TOKENS
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", LLM_BASE_URL)
    LLM_API_KEY = os.getenv("LLM_API_KEY", LLM_API_KEY)
    LLM_MODEL = os.getenv("LLM_MODEL", LLM_MODEL)
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", str(LLM_TIMEOUT)))
    MAX_HISTORY_ROUNDS = int(os.getenv("MAX_HISTORY_ROUNDS", str(MAX_HISTORY_ROUNDS)))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(LLM_TEMPERATURE)))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", str(LLM_MAX_TOKENS)))