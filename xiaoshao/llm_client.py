# -*- coding: utf-8 -*-
"""大模型 API 客户端:封装 OpenAI 兼容格式的对话接口。

优先使用 requests 库;若未安装则自动回退到标准库 urllib,零依赖也能运行。
"""

import json

from . import config

try:
    import requests  # type: ignore

    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
    import urllib.request
    import urllib.error


class LLMError(Exception):
    """大模型调用异常。"""

    pass


class LLMClient:
    """OpenAI 兼容格式的大模型客户端。"""

    def __init__(self):
        self.base_url = config.LLM_BASE_URL.rstrip("/")
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
        self.timeout = config.LLM_TIMEOUT

    def chat(self, messages: list) -> str:
        """发送对话请求并返回模型回复文本。

        Args:
            messages: OpenAI 格式的消息列表,如
                [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

        Returns:
            模型回复的文本内容。

        Raises:
            LLMError: 当请求失败或响应异常时抛出。
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": config.LLM_TEMPERATURE,
            "max_tokens": config.LLM_MAX_TOKENS,
        }
        if _HAS_REQUESTS:
            return self._chat_with_requests(payload)
        return self._chat_with_urllib(payload)

    # ---------- requests 实现 ----------
    def _chat_with_requests(self, payload: dict) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            resp = requests.post(
                url, headers=headers, json=payload, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            raise LLMError(f"请求超时({self.timeout}s),请检查网络或增大 LLM_TIMEOUT。")
        except requests.exceptions.ConnectionError:
            raise LLMError("网络连接失败,请检查网络或 LLM_BASE_URL 是否正确。")
        except requests.exceptions.HTTPError as e:
            raise LLMError(f"API 返回错误 {resp.status_code}: {resp.text[:300]}")
        except json.JSONDecodeError:
            raise LLMError("API 返回内容不是合法 JSON,请检查 LLM_BASE_URL。")
        return self._extract_content(data)

    # ---------- urllib 回退实现 ----------
    def _chat_with_urllib(self, payload: dict) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode("utf-8")[:300]
            except Exception:
                pass
            raise LLMError(f"API 返回错误 {e.code}: {detail}")
        except urllib.error.URLError as e:
            raise LLMError(f"网络请求失败: {e.reason}")
        except json.JSONDecodeError:
            raise LLMError("API 返回内容不是合法 JSON,请检查 LLM_BASE_URL。")
        return self._extract_content(data)

    @staticmethod
    def _extract_content(data: dict) -> str:
        """从 OpenAI 格式响应中提取回复文本。"""
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise LLMError(f"无法解析 API 响应结构: {json.dumps(data, ensure_ascii=False)[:300]}")