# -*- coding: utf-8 -*-
"""
extract_expert_panel.py — 统计时间盲法候选的 ReviewStatus 分布 + 导出专家评审候选

背景：ClinGen 专家精审通过 ClinVar 发布（ReviewStatus = "reviewed by expert panel"
      或 "practice guideline"）。统计时间盲法（LastEvaluated >= 2026-01）候选池里
      的专家评审变异数量，评估能否建"专家评审富集测试集"（金标准 A 独立验证）。

输出：
    data/expert_panel_candidates.csv（时间盲法 + 专家评审候选，含全部 43 列）
    （stdout）ReviewStatus 分布统计

使用：
    python extract_expert_panel.py
"""
import csv
import gzip
import re
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_GZ = DATA_DIR / "variant_summary.txt.gz"
OUT_CSV = DATA_DIR / "expert_panel_candidates.csv"
CUTOFF = "2026-01"

FIELDS = [
    "AlleleID", "Type", "Name", "GeneID", "GeneSymbol", "HGNC_ID",
    "ClinicalSignificance", "ClinSigSimple", "LastEvaluated", "RS# (dbSNP)",
    "nsv/esv (dbVar)", "RCVaccession", "PhenotypeIDS", "PhenotypeList",
    "Origin", "OriginSimple", "Assembly", "ChromosomeAccession",
    "Chromosome", "Start", "Stop", "ReferenceAllele", "AlternateAllele",
    "Cytogenetic", "ReviewStatus", "NumberSubmitters", "Guidelines",
    "TestedInGTR", "OtherIDs", "SubmitterCategories", "VariationID",
    "PositionVCF", "ReferenceAlleleVCF", "AlternateAlleleVCF",
    "SomaticClinicalImpact", "SomaticClinicalImpactLastEvaluated",
    "ReviewStatusClinicalImpact", "Oncogenicity",
    "OncogenicityLastEvaluated", "ReviewStatusOncogenicity",
    "SCVsForAggregateGermlineClassification",
    "SCVsForAggregateSomaticClinicalImpact",
    "SCVsForAggregateOncogenicityClassification",
]
EXPERT = {"reviewed by expert panel", "practice guideline"}


def parse_date(d: str):
    m = re.match(r"([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})", d.strip())
    if not m:
        return None
    mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    return (int(m.group(3)), mon.get(m.group(1), 0))


def main():
    if not RAW_GZ.exists():
        sys.exit(f"✗ 找不到 {RAW_GZ}")
    print(f"流式解析 {RAW_GZ}（时间盲法 cutoff={CUTOFF}）...")
    rs_counter = Counter()       # 时间盲法候选的 ReviewStatus 分布
    temporal_counter = Counter()  # 时间盲法候选的 ClinicalSignificance
    n_total = 0
    n_after = 0
    expert_rows = []
    seen = set()
    with gzip.open(RAW_GZ, "rt", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        header = [h.lstrip("#").strip() for h in next(reader)]
        col_idx = {name: i for i, name in enumerate(header)}
        for raw in reader:
            n_total += 1
            if len(raw) < len(header):
                continue
            r = {name: (raw[col_idx[name]] if name in col_idx else "")
                 for name in FIELDS}
            d = parse_date(r.get("LastEvaluated", ""))
            if not d or (d[0], d[1]) < (int(CUTOFF[:4]), int(CUTOFF[5:7])):
                continue
            sig = r.get("ClinicalSignificance", "").strip()
            if not sig or "Conflicting" in sig or "Uncertain" in sig:
                continue
            n_after += 1
            rs_counter[r.get("ReviewStatus", "").strip() or "(空)"] += 1
            temporal_counter[sig] += 1
            if r.get("ReviewStatus", "").strip() in EXPERT:
                aid = r["AlleleID"]
                if aid not in seen:
                    seen.add(aid)
                    expert_rows.append(r)

    print(f"\n总行数: {n_total:,} | 时间盲法+明确分类候选: {n_after:,}")
    print("\n时间盲法候选 ReviewStatus 分布:")
    for k, v in rs_counter.most_common():
        print(f"  {v:6d}  {k}")
    print("\n时间盲法候选 ClinicalSignificance（前5）:")
    for k, v in temporal_counter.most_common(5):
        print(f"  {v:6d}  {k}")
    print(f"\n专家评审（expert panel + practice guideline）候选: {len(expert_rows):,}")

    if expert_rows:
        with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for r in expert_rows:
                w.writerow(r)
        print(f"✓ 已导出: {OUT_CSV}")


if __name__ == "__main__":
    main()
