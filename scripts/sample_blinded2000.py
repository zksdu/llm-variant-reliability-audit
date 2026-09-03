# -*- coding: utf-8 -*-
"""
sample_blinded2000.py — 完全盲专用测试集抽样（更强方案）

从 ClinVar variant_summary 抽取 LastEvaluated ≥ 2026-04 的合格变异
（P/B、无冲突、有 HGVS、AlleleID 去重），seed=42 平衡抽样 1,000 P + 1,000 B，
输出 43 列标准格式（run_variant_classification.py 可直接读取）。

设计依据：六个国内模型截止 ≤2025、国际模型截止最晚 2026-03，
故 ≥2026-04 的标签对所有九个模型都严格晚于训练截止——完全盲。

使用：python sample_blinded2000.py
"""
import csv
import gzip
import random
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
RAW = DATA / "variant_summary.txt.gz"
OUT = DATA / "blinded2000_set.csv"

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

MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def main():
    seen = {}
    with gzip.open(RAW, "rt", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        reader.fieldnames = [(h or "").lstrip("#").strip() for h in reader.fieldnames]
        for row in reader:
            sig = (row.get("ClinicalSignificance") or "").strip()
            if sig not in ("Pathogenic", "Benign"):
                continue
            le = (row.get("LastEvaluated") or "").strip()
            if not le:
                continue
            parts = le.replace(",", "").split()
            if len(parts) < 3 or MONTHS.get(parts[0], 0) < 4 or parts[2] < "2026":
                continue
            if not (row.get("Name") or "").strip():
                continue
            aid = row.get("AlleleID") or ""
            if not aid or aid in seen:
                continue
            seen[aid] = {k: (row.get(k) or "") for k in FIELDS}

    by_side = defaultdict(list)
    for aid, r in seen.items():
        by_side[r["ClinicalSignificance"]].append(aid)
    rng = random.Random(42)
    sample = []
    for side, n in (("Pathogenic", 1000), ("Benign", 1000)):
        ids = sorted(by_side[side])
        rng.shuffle(ids)
        take = ids[:n]
        print(f"{side}: 池 {len(ids)} → 抽 {len(take)}")
        sample.extend(take)

    # 主测试集重叠统计（分析用）
    main_ids = set()
    with (DATA / "clinvar_testset_temporal.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            main_ids.add(r["AlleleID"])
    overlap = sum(1 for a in sample if a in main_ids)
    print(f"与主 5,000 测试集重叠: {overlap}/{len(sample)}")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for aid in sample:
            w.writerow(seen[aid])
    print(f"✓ {OUT} ({len(sample)} 行)")


if __name__ == "__main__":
    main()
