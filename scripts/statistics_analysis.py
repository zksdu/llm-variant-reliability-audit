# -*- coding: utf-8 -*-
"""
statistics_analysis.py — 论文统计检验

1. Wilson 95% CI：每个模型的准确率（全对全 / 表态时）
2. McNemar 配对检验：模型两两比较（同一批变异上的不一致对）
3. 共识 vs 最佳单模型比较

输出：data/statistics_analysis.md

使用：
    python statistics_analysis.py
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RESULTS = DATA_DIR / "variant_classification_results_all.csv"
GOLD_CSV = DATA_DIR / "clinvar_testset_temporal.csv"
OUT_MD = DATA_DIR / "statistics_analysis.md"

PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}
MODELS = ["deepseek-v4-pro", "deepseek-chat", "deepseek-coder",
          "kimi-k2.6", "mimo-v2.5-pro", "qwen3.7-max"]
MODELS_INTL = ["gemini-3-flash", "claude-sonnet-5", "gpt-5.6-terra"]


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def wilson_ci(k, n, z=1.96):
    """Wilson score interval。"""
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def mcnemar(a, b):
    """McNemar 配对检验。
    a: 模型A对模型B错；b: 模型B对模型A错。
    n>30 用正态近似（含连续性校正，与精确检验等价）；否则精确二项。"""
    n = a + b
    if n == 0:
        return None
    if n <= 30:
        p = 0.0
        k = min(a, b)
        for i in range(k + 1):
            p += math.comb(n, i) * (0.5 ** n)
        return min(1.0, 2 * p)
    # 大样本近似：z = (|a-b| - 1) / sqrt(a+b)，双侧
    z = (abs(a - b) - 1) / math.sqrt(n)
    # 标准正态尾部概率（erfc 近似）
    return min(1.0, math.erfc(z / math.sqrt(2)))


def main():
    # 加载结果（每变异每模型一票）与金标准
    votes = defaultdict(dict)
    with RESULTS.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            aid, m = r["AlleleID"], r["model"]
            if aid and m and r["llm_class"] != "error":
                votes[aid][m] = bin2(r["llm_class"])
    gold = {}
    with GOLD_CSV.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            gold[r["AlleleID"]] = bin2(r["ClinicalSignificance"])

    # 只统计金标准 P/B 的变异
    aids = [a for a in votes if gold.get(a) in ("P", "B")]
    print(f"可评定变异: {len(aids)}")

    lines = []
    lines.append("# 统计检验结果\n")
    lines.append(f"可评定变异（金标准 P/B）: {len(aids)}\n")

    # 1. Wilson CI（全对全准确率：VUS 计错）
    lines.append("## 1. 全对全准确率（VUS=错）+ Wilson 95% CI\n")
    lines.append("| 模型 | 准确率 | 95% CI |")
    lines.append("|---|---|---|")
    accs = {}
    for m in MODELS + MODELS_INTL:
        k = sum(1 for a in aids if votes[a].get(m) == gold[a])
        n = len(aids)
        p, lo, hi = wilson_ci(k, n)
        accs[m] = p
        lines.append(f"| {m} | {p*100:.1f}% | [{lo*100:.1f}%, {hi*100:.1f}%] |")

    # 2. McNemar 配对检验
    lines.append("\n## 2. McNemar 配对检验（行模型 vs 列模型，p 值）\n")
    lines.append("| 对比 | p 值 | 显著 |")
    lines.append("|---|---|---|")
    pairs = [("qwen3.7-max", "deepseek-chat"), ("qwen3.7-max", "kimi-k2.6"),
             ("kimi-k2.6", "deepseek-chat"), ("deepseek-v4-pro", "deepseek-chat"),
             ("mimo-v2.5-pro", "deepseek-chat"), ("kimi-k2.6", "mimo-v2.5-pro"),
             ("gemini-3-flash", "qwen3.7-max"), ("claude-sonnet-5", "qwen3.7-max"),
             ("gpt-5.6-terra", "qwen3.7-max"), ("claude-sonnet-5", "kimi-k2.6"),
             ("gpt-5.6-terra", "deepseek-v4-pro")]
    for m1, m2 in pairs:
        a = b = 0
        for aid in aids:
            v1, v2 = votes[aid].get(m1), votes[aid].get(m2)
            if v1 is None or v2 is None:
                continue
            g = gold[aid]
            c1 = (v1 == g)
            c2 = (v2 == g)
            if c1 and not c2:
                a += 1
            elif c2 and not c1:
                b += 1
        pv = mcnemar(a, b)
        sig = "是" if pv is not None and pv < 0.001 else \
              ("是(<0.05)" if pv is not None and pv < 0.05 else "否")
        lines.append(f"| {m1} vs {m2} | {pv:.2e}" if pv else
                     f"| {m1} vs {m2} | n/a |")

    # 3. 共识 vs 最佳单模型（6 模型多数投票，VUS 也是一票；平票排除）
    lines.append("\n## 3. 共识 vs 最佳单模型（6 模型多数投票）\n")
    cons_all_k = cons_all_n = 0   # 全对全口径（共识=VUS 计错）
    cons_sp_k = cons_sp_n = 0     # 表态口径（共识非 VUS 时）
    for aid in aids:
        vs = [votes[aid].get(m) for m in MODELS]
        vs = [v for v in vs if v is not None]
        if not vs:
            continue
        cnt = defaultdict(int)
        for v in vs:
            cnt[v] += 1
        top = sorted(cnt.items(), key=lambda x: -x[1])
        if len(top) > 1 and top[0][1] == top[1][1]:
            continue  # 平票弃权
        cons_all_n += 1
        if top[0][0] == gold[aid]:
            cons_all_k += 1
        if top[0][0] in ("P", "B"):
            cons_sp_n += 1
            if top[0][0] == gold[aid]:
                cons_sp_k += 1
    p, lo, hi = wilson_ci(cons_all_k, cons_all_n)
    lines.append(f"| 6 模型共识（全对全口径）| {p*100:.1f}% | "
                 f"[{lo*100:.1f}%, {hi*100:.1f}%] (n={cons_all_n}) |")
    p2, lo2, hi2 = wilson_ci(cons_sp_k, cons_sp_n)
    lines.append(f"| 6 模型共识（表态口径）| {p2*100:.1f}% | "
                 f"[{lo2*100:.1f}%, {hi2*100:.1f}%] (n={cons_sp_n}) |")
    best = max(accs, key=accs.get)
    lines.append(f"| 最佳单模型（{best}）| {accs[best]*100:.1f}% | — |")
    lines.append("\n> McNemar：n>30 正态近似（含连续性校正）；共识平票不计入。\n")

    content = "\n".join(lines)
    OUT_MD.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
