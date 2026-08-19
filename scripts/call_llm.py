# -*- coding: utf-8 -*-
"""call_llm 自包含模块 —— 不依赖外部项目。"""
import os
import sys
import time
from pathlib import Path

_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            if k.strip() not in os.environ:
                os.environ[k.strip()] = v.strip()

# --- 常量 ---
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 2048
LLM_TIMEOUT = 120
LLM_MAX_RETRIES = 3
LLM_RETRY_BACKOFF = 4.0

PROVIDER_ENV = {
    "openai":    "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek":  "DEEPSEEK_API_KEY",
    "mimo":      "MIMO_API_KEY",
    "qwen":      "QWEN_API_KEY",
    # 国际模型中转（ai.flashapi.top，OpenAI 兼容；key 按模型作用域隔离）
    "flashapi-gemini":  "FLASHAPI_GEMINI_KEY",
    "flashapi-gpt":     "FLASHAPI_GPT_KEY",
    "flashapi-claude":  "FLASHAPI_CLAUDE_KEY",
}

PROVIDER_BASE_URL = {
    "openai":    "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",   # 兼容模式，实际可用性视网络
    "deepseek":  "https://api.deepseek.com/v1",     # 国内直连可用
    "mimo":      "https://token-plan-cn.xiaomimimo.com/v1",  # 小米 Token Plan 专属（OpenAI 兼容）
    "qwen":      "https://ws-5goqmabvbrl3rm2y.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",  # 阿里云百炼专属实例（OpenAI 兼容）
    "flashapi-gemini":  "https://ai.flashapi.top/v1",
    "flashapi-gpt":     "https://ai.flashapi.top/v1",
    "flashapi-claude":  "https://ai.flashapi.top/v1",
}

DEEPSEEK_MODEL_MAP = {
    "deepseek-coder":    "deepseek-coder",
    "deepseek-chat":     "deepseek-chat",
    "deepseek-reasoner": "deepseek-reasoner",
    "deepseek-v4-flash": "deepseek-v4-flash",
    "deepseek-v4-pro":   "deepseek-v4-pro",
}

def _provider_for_model(model: str) -> str:
    m = model.lower()
    if m.startswith("gemini"):   return "flashapi-gemini"
    if m.startswith("gpt-5"):    return "flashapi-gpt"
    if m.startswith("claude"):   return "flashapi-claude"
    if m.startswith("gpt") or m.startswith("openai/"): return "openai"
    if m.startswith("claude") or m.startswith("anthropic/"): return "anthropic"
    if m.startswith("deepseek"): return "deepseek"
    if m.startswith("mimo") or m.startswith("xiaomi"): return "mimo"
    if m.startswith("qwen") or m.startswith("dashscope"): return "qwen"
    if m.startswith("glm") or m.startswith("kimi") or m.startswith("minimax"): return "qwen"
    return "openai"


def _has_api_key(model: str) -> bool:
    return bool(os.environ.get(PROVIDER_ENV.get(_provider_for_model(model), ""), ""))

def call_llm(model: str, prompt: str, **kwargs) -> str:
    """
    统一 LLM 调用封装（原生 requests 直调 OpenAI 兼容 chat/completions 接口）。

    支持 deepseek / openai / 其他 OpenAI 兼容厂商。无需 litellm/tiktoken，
    避免国内网络下 tiktoken 编码文件下载失败的问题。

    返回 LLM 输出的纯文本。

    容错策略：
      - API key 缺失：抛出 RuntimeError，由上层捕获并降级为 dry-run；
      - 超时 / 限流：指数退避重试 LLM_MAX_RETRIES 次；
      - 其它异常：重试耗尽后向上抛出（记 errors.log，不中断整体流程）。
    """
    if not _has_api_key(model):
        env_var = PROVIDER_ENV.get(_provider_for_model(model), "API_KEY")
        raise RuntimeError(
            f"未配置 {env_var}，无法调用 {model}。请设置环境变量后重试，"
            f"或使用 --dry-run 仅打印 prompt。"
        )

    import requests  # 标准库生态，无 tiktoken 依赖

    provider = _provider_for_model(model)
    api_key = os.environ[PROVIDER_ENV[provider]]
    base_url = PROVIDER_BASE_URL.get(provider, PROVIDER_BASE_URL["openai"])
    # DeepSeek 模型名映射到厂商实际 model 字段
    api_model = DEEPSEEK_MODEL_MAP.get(model, model)

    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages = []
    sys_msg = kwargs.get("system")
    if sys_msg:
        messages.append({"role": "system", "content": sys_msg})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": api_model,
        "messages": messages,
        "temperature": kwargs.get("temperature", LLM_TEMPERATURE),
        "max_tokens": kwargs.get("max_tokens", LLM_MAX_TOKENS),
        "stream": False,
    }
    # DeepSeek 不支持 seed 字段，OpenAI 支持；按厂商条件加入
    if provider == "openai":
        payload["seed"] = kwargs.get("seed", LLM_SEED)

    last_err = None
    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers,
                                 timeout=LLM_TIMEOUT)
            # HTTP 错误码处理
            if resp.status_code == 429 or resp.status_code >= 500:
                # 限流/服务端错误，可重试
                raise requests.exceptions.HTTPError(
                    f"HTTP {resp.status_code}: {resp.text[:200]}", response=resp)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"] or ""
        except Exception as e:  # noqa: BLE001
            last_err = e
            name = type(e).__name__
            msg = str(e).lower()
            # 鉴权/参数错误立即失败；限流/超时/服务端错误才重试
            retriable = any(kw in msg for kw in (
                "rate", "timeout", "timed", "service", "unavailable",
                "429", "500", "502", "503", "connection"
            )) and "auth" not in msg and "401" not in msg and "invalid" not in msg
            if not retriable or attempt == LLM_MAX_RETRIES:
                raise
            backoff = LLM_RETRY_BACKOFF * (2 ** (attempt - 1))
            print(f"    ! 调用失败（{name}），{backoff:.1f}s 后重试 "
                  f"({attempt}/{LLM_MAX_RETRIES}): {str(e)[:120]}", file=sys.stderr)
            time.sleep(backoff)
    # 理论不可达，保险起见
    raise last_err  # type: ignore[misc]


# ============================================================
# fix_correct 判定（接口 + 占位）
# ============================================================
