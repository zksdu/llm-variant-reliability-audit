# -*- coding: utf-8 -*-
"""
cost_profiling.py — 每变异 token 用量与成本审计

用途：主实验未记录 token usage；本脚本抽样 30 变异 × 6 模型，
      从 API 响应提取 usage（prompt/completion tokens），结合官方定价
      估算每变异成本，支持论文成本科学（RQ5）。

输出：data/cost_profiling.md（token 用量 + 成本表）

使用：
    python cost_profiling.py
"""
import csv
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
DATA_DIR = HERE.parent / "data"
sys.path.insert(0, str(HERE))

from run_experiment import (call_llm, _provider_for_model, PROVIDER_ENV,  # noqa: E402
                            PROVIDER_BASE_URL, DEEPSEEK_MODEL_MAP)
from run_variant_classification import build_variant_prompt  # noqa: E402

MODELS = ["deepseek-v4-pro", "deepseek-chat", "deepseek-coder",
          "kimi-k2.6", "mimo-v2.5-pro", "qwen3.7-max"]
N_VAR = 30

# 官方定价（¥/百万 tokens，2026-08；高峰时段 ×2 未计入，标注来源）
# 来源：DeepSeek API pricing / 小米 Token Plan 定价 / 百炼计费 / 各厂商定价页
PRICE = {
    "deepseek-v4-pro": (3.0, 6.0),
    "deepseek-chat":   (2.0, 8.0),
    "deepseek-coder":  (2.0, 8.0),
    "kimi-k2.6":       (4.0, 16.0),
    "mimo-v2.5-pro":   (7.2, 21.6),   # $1.0/$3.0 @ 7.2
    "qwen3.7-max":     (2.4, 9.6),
}
PRICE_NOTE = ("价格为 2026-08 官方定价估算（Kimi/MiMo/Qwen 以官方页面为准）；"
              "论文报告以 token 用量（实测）为主、成本为参考")


def main():
    rows = list(csv.DictReader((DATA_DIR / "clinvar_testset_temporal.csv").open(
        "r", encoding="utf-8", newline="")))
    random.seed(123)
    sample = random.sample(rows, N_VAR)
    print(f"抽样 {N_VAR} 变异 × {len(MODELS)} 模型\n")

    results = []
    for m in MODELS:
        t_in = t_out = 0
        n_ok = 0
        t0 = time.time()
        for var in sample:
            try:
                usage = _call_with_usage(m, build_variant_prompt(var))
                t_in += usage.get("prompt_tokens", 0)
                t_out += usage.get("completion_tokens", 0)
                n_ok += 1
            except Exception as e:  # noqa: BLE001
                print(f"  {m}: {var['AlleleID']} 失败 {str(e)[:60]}")
        dt = time.time() - t0
        pin, pout = PRICE.get(m, (0, 0))
        cost = (t_in * pin + t_out * pout) / 1e6
        results.append((m, n_ok, t_in, t_out, cost, dt))
        print(f"  {m}: {n_ok}/{N_VAR} | 输入 {t_in:,} | 输出 {t_out:,} "
              f"| 每变异 {cost/max(n_ok,1):.3f} 元 | {dt/max(n_ok,1):.1f}s/变异")

    lines = ["# 成本审计（30 变异 × 6 模型抽样）\n",
             f"> {PRICE_NOTE}\n",
             "| 模型 | 每变异输入tok | 每变异输出tok | 每变异成本(¥) | 延迟(秒) |",
             "|---|---|---|---|---|"]
    for m, n_ok, t_in, t_out, cost, dt in results:
        n = max(n_ok, 1)
        lines.append(f"| {m} | {t_in/n:.0f} | {t_out/n:.0f} | "
                     f"{cost/n:.3f} | {dt/n:.1f} |")
    (DATA_DIR / "cost_profiling.md").write_text("\n".join(lines) + "\n",
                                               encoding="utf-8")
    print(f"\n✓ 已写出 {DATA_DIR / 'cost_profiling.md'}")


def _call_with_usage(model: str, prompt: str, max_tokens: int = 8192):
    """调 API 并返回 usage dict（复用 call_llm 的 provider 配置）。"""
    import os
    import requests
    provider = _provider_for_model(model)
    api_key = os.environ[PROVIDER_ENV[provider]]
    url = f"{PROVIDER_BASE_URL[provider]}/chat/completions"
    api_model = DEEPSEEK_MODEL_MAP.get(model, model)
    mt = max_tokens if (model.startswith("deepseek-v4") or model.startswith("mimo")
                        or model.startswith("qwen") or model.startswith("kimi")) else 1024
    resp = requests.post(url, json={
        "model": api_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": mt,
        "stream": False,
    }, headers={"Authorization": f"Bearer {api_key}"}, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    return data.get("usage", {})


if __name__ == "__main__":
    main()
