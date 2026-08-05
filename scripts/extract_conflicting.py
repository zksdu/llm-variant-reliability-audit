# -*- coding: utf-8 -*-
"""
extract_conflicting.py — 提取 ClinVar 冲突解释变异（三角验证数据源 B）

用途：专家对同一变异给出相反分类（Pathogenic vs Benign 并存）的变异，
      用于分析"LLM 在专家分歧变异上的行为"——模型输出倾向于哪方、
      与多数提交者一致性如何（审稿人关心的"模型 vs 专家分歧"维度）。

输出：
    data/conflicting_candidates.csv（时间盲法 + 明确冲突的变异）

使用：
    python extract_conflicting.py
"""
import csv
import gzip
import re
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_GZ = DATA_DIR / "variant_summary.txt.gz"
OUT_CSV = DATA_DIR / "conflicting_candidates.csv"
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
    print(f"流式解析 {RAW_GZ}（cutoff={CUTOFF}）...")
    n_total = 0
    n_conflict = 0
    rows_out = []
    seen = set()
    sig_counter = Counter()
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
            sig = r.get("ClinicalSignificance", "").strip()
            if "Conflicting" not in sig:
                continue
            d = parse_date(r.get("LastEvaluated", ""))
            if not d or (d[0], d[1]) < (int(CUTOFF[:4]), int(CUTOFF[5:7])):
                continue
            n_conflict += 1
            sig_counter[sig] += 1
            aid = r["AlleleID"]
            if aid not in seen:
                seen.add(aid)
                rows_out.append(r)

    print(f"总行数: {n_total:,} | 时间盲法+Conflicting 行: {n_conflict:,}")
    print(f"去重后变异数: {len(rows_out):,}")
    print("\nClinicalSignificance 形式（前6）:")
    for k, v in sig_counter.most_common(6):
        print(f"  {v:6d}  {k[:90]}")

    if rows_out:
        with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows_out)
        print(f"✓ 已导出: {OUT_CSV}")


if __name__ == "__main__":
    main()
