# -*- coding: utf-8 -*-
"""
surface_cue_analysis.py — 表面线索分层（Finding 4 / "读名"分析）的存档计算

方法：金标准 Pathogenic 变异按 HGVS 蛋白名是否携带功能丧失（LoF）表面线索
分层（无义突变 Ter 终止符号 / 移码 fs），分别计算各模型 P 敏感度。

使用：python surface_cue_analysis.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent.parent / "data" / "surface_cue_analysis.md"

PATHO = {"Pathogenic", "Likely pathogenic"}
BEN = {"Benign", "Likely benign"}

# LoF 表面线索：HGVS 蛋白名中的无义（p.Xxx123Ter，含 * 与 Ter 变体写法）或移码（fs）
LOF_RE = re.compile(r"p\.[A-Za-z]{2,3}\d+(Ter|\*|fs)", re.IGNORECASE)

MODELS = ["deepseek-chat", "kimi-k2.6", "qwen3.7-max"]


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BEN:
        return "B"
    return "V"


def main():
    gold, name = {}, {}
    with (DATA / "clinvar_testset_temporal.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            g = bin2(r["ClinicalSignificance"])
            gold[r["AlleleID"]] = g
            name[r["AlleleID"]] = r["Name"]
    votes = defaultdict(dict)
    with (DATA / "variant_classification_results_all.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            votes[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])

    cued = [a for a, g in gold.items() if g == "P" and LOF_RE.search(name[a])]
    uncued = [a for a, g in gold.items() if g == "P" and not LOF_RE.search(name[a])]

    lines = [f"# 表面线索分层（存档计算；正则 {LOF_RE.pattern}）", "",
             f"cued n = {len(cued)}; uncued n = {len(uncued)}", "",
             "| 模型 | P 敏感度 cued | P 敏感度 uncued | 差距 |", "|---|---|---|---|"]
    for m in MODELS:
        cs = sum(1 for a in cued if votes.get(a, {}).get(m) == "P") / len(cued) * 100
        us = sum(1 for a in uncued if votes.get(a, {}).get(m) == "P") / len(uncued) * 100
        lines.append(f"| {m} | {cs:.1f}% | {us:.1f}% | {cs-us:.1f} pp |")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\n✓ {OUT}")


if __name__ == "__main__":
    main()
