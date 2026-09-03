# -*- coding: utf-8 -*-
"""
bootstrap_gene_ci.py — 基因层聚类自助 95% CI（Methods 统计节声明的存档计算）

方法：按基因（变异聚集单位）有放回重采样 1,000 次，每次重算全对全准确率，
取 2.5/97.5 百分位。与 Wilson 95% CI 宽度比较；同时检验模型间结论是否保持
（配对差的自助 CI 是否不含 0）。

使用：python bootstrap_gene_ci.py
"""
import csv
import math
import random
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent.parent / "data" / "bootstrap_gene_analysis.md"

PATHO = {"Pathogenic", "Likely pathogenic"}
BEN = {"Benign", "Likely benign"}


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BEN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    gold, gene = {}, {}
    with (DATA / "clinvar_testset_temporal.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            g = bin2(r["ClinicalSignificance"])
            if g in ("P", "B"):
                gold[r["AlleleID"]] = g
                gene[r["AlleleID"]] = (r["GeneSymbol"] or "NA")

    votes = defaultdict(dict)
    with (DATA / "variant_classification_results_all.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["llm_class"] and r["llm_class"].lower() != "error":
                votes[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])

    # 基因 -> 变异列表
    genes = defaultdict(list)
    for aid, g in gene.items():
        genes[g].append(aid)
    gene_names = sorted(genes)

    models = ["gemini-3-flash", "qwen3.7-max", "claude-sonnet-5", "kimi-k2.6",
              "mimo-v2.5-pro", "deepseek-v4-pro", "gpt-5.6-terra",
              "deepseek-chat", "deepseek-coder"]
    rng = random.Random(42)
    B = 1000

    lines = ["# 基因层聚类自助 95% CI（存档计算，seed=42, B=1,000）", "",
             "| 模型 | 全对全 | Wilson CI | 基因自助 CI | 宽度比(自助/Wilson) |",
             "|---|---|---|---|---|"]
    ratios, accs = {}, {}
    for m in models:
        correct = {a: 1 if votes.get(a, {}).get(m) == gold[a] else 0 for a in gold}
        n = len(gold)
        k = sum(correct.values())
        acc = k / n * 100
        wl, wh = wilson(k, n)
        boots = []
        for _ in range(B):
            tot = hit = 0
            for _ in range(len(gene_names)):
                gname = gene_names[rng.randrange(len(gene_names))]
                for aid in genes[gname]:
                    tot += 1
                    hit += correct[aid]
            boots.append(hit / max(tot, 1) * 100)
        boots.sort()
        bl, bh = boots[int(0.025 * B)], boots[int(0.975 * B)]
        ratio = (bh - bl) / ((wh - wl) * 100)
        ratios[m] = ratio
        accs[m] = acc
        lines.append(f"| {m} | {acc:.1f}% | [{wl*100:.1f}, {wh*100:.1f}] | "
                     f"[{bl:.1f}, {bh:.1f}] | {ratio:.2f}x |")

    mean_ratio = sum(ratios.values()) / len(ratios)
    lines += ["", "平均宽度比：%.2fx" % mean_ratio, ""]

    # 模型间结论保持性：Qwen vs Kimi / Kimi vs chat / Gemini vs Qwen（配对差自助 CI）
    lines += ["## 模型间结论保持性（配对差 × 基因自助）", "",
              "| 对比 | 点差(pp) | 自助 95% CI | 结论保持 |", "|---|---|---|---|"]
    for m1, m2 in [("qwen3.7-max", "kimi-k2.6"), ("kimi-k2.6", "deepseek-chat"),
                   ("gemini-3-flash", "qwen3.7-max")]:
        diff = {a: (1 if votes.get(a, {}).get(m1) == gold[a] else 0) -
                   (1 if votes.get(a, {}).get(m2) == gold[a] else 0) for a in gold}
        boots = []
        for _ in range(B):
            tot = 0
            s = 0.0
            for _ in range(len(gene_names)):
                gname = gene_names[rng.randrange(len(gene_names))]
                for aid in genes[gname]:
                    tot += 1
                    s += diff[aid]
            boots.append(s / max(tot, 1) * 100)
        boots.sort()
        bl, bh = boots[int(0.025 * B)], boots[int(0.975 * B)]
        point = sum(diff.values()) / len(diff) * 100
        keep = "是" if (bl > 0 or bh < 0) else "否"
        lines.append(f"| {m1} vs {m2} | {point:+.2f} | [{bl:+.2f}, {bh:+.2f}] | {keep} |")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\n✓ {OUT}")


if __name__ == "__main__":
    main()
