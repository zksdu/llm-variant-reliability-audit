# -*- coding: utf-8 -*-
"""
rebuild_temporal.py — 流式重建时间盲法测试集（修复 #AlleleID 解析 bug）

背景：preprocess_clinvar.py 早期版本未剥离表头 '#' 前缀（'#AlleleID'），
      导致 clinvar_parsed.csv / clinvar_testset_temporal.csv 的 AlleleID 列全空。
      本脚本直接从原始 variant_summary.txt.gz 流式重建，不重写 3.9GB parsed 文件。

采样逻辑与 sample_clinvar_testset.py 完全一致（seed=42）：
    - 时间盲法：LastEvaluated >= 2026-01（DeepSeek V4 截止 2025-12）
    - 明确 Pathogenic / Benign（排除 VUS/Conflicting/Likely）
    - 分层各 2500 + shuffle（random.seed(42) → 顺序可复现，
      与旧 temporal 前 100 行一致，可据此恢复实验 CSV 的 AlleleID）

输出：data/clinvar_testset_temporal.csv（43 列官方字段，AlleleID 正确）

使用：
    python rebuild_temporal.py [--n 5000] [--cutoff 2026-01]
"""
import csv
import gzip
import re
import random
import argparse
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_GZ = DATA_DIR / "variant_summary.txt.gz"
OUT_CSV = DATA_DIR / "clinvar_testset_temporal.csv"

DEFAULT_CUTOFF = "2026-01"
DEFAULT_N = 5000

# 与 preprocess_clinvar.py 相同的官方 43 列（表头须剥离 '#'）
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
    """'Jan 5, 2026' → (2026, 1)。无法解析返回 None。"""
    m = re.match(r"([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})", d.strip())
    if not m:
        return None
    mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    return (int(m.group(3)), mon.get(m.group(1), 0))


def eligible(row, cutoff):
    """时间盲法合格：2026 后评估 + 明确分类 + 有 HGVS。与 sample 脚本一致。"""
    d = parse_date(row.get("LastEvaluated", ""))
    if not d:
        return False
    if (d[0], d[1]) < (int(cutoff[:4]), int(cutoff[5:7])):
        return False
    sig = row.get("ClinicalSignificance", "").strip()
    if "Conflicting" in sig or "Uncertain" in sig or "Likely" in sig:
        return False
    if "Pathogenic" not in sig and "Benign" not in sig:
        return False
    if not row.get("Name", "").strip():
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="流式重建时间盲法测试集")
    ap.add_argument("--n", type=int, default=DEFAULT_N)
    ap.add_argument("--cutoff", default=DEFAULT_CUTOFF)
    args = ap.parse_args()

    if not RAW_GZ.exists():
        raise SystemExit(f"✗ 找不到 {RAW_GZ}")

    print(f"流式解析 {RAW_GZ} ...")
    patho, benign = [], []
    total = 0
    with gzip.open(RAW_GZ, "rt", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        header = [h.lstrip("#").strip() for h in next(reader)]
        col_idx = {name: i for i, name in enumerate(header)}
        print(f"  列数: {len(header)}（AlleleID 索引 = {col_idx.get('AlleleID')}）")
        for raw in reader:
            total += 1
            if len(raw) < len(header):
                continue
            r = {name: (raw[col_idx[name]] if name in col_idx else "")
                 for name in FIELDS}
            if not r.get("AlleleID", "").strip():
                continue  # 无主键的行直接丢弃（防御）
            if not eligible(r, args.cutoff):
                continue
            sig = r.get("ClinicalSignificance", "")
            if "Pathogenic" in sig:
                patho.append(r)
            elif "Benign" in sig:
                benign.append(r)
            if total % 1000000 == 0:
                print(f"  已扫描 {total/1e6:.1f}M 行，"
                      f"候选 patho={len(patho)} benign={len(benign)}")

    print(f"\n扫描完成: {total} 行")
    print(f"时间盲法候选: Pathogenic={len(patho)} / Benign={len(benign)}")

    # 单变异去重（同一 AlleleID 只留一条；ClinVar 同 ID 可能有多行）
    def dedup(lst):
        seen, out = set(), []
        for r in lst:
            if r["AlleleID"] not in seen:
                seen.add(r["AlleleID"])
                out.append(r)
        return out
    patho, benign = dedup(patho), dedup(benign)
    print(f"去重后: Pathogenic={len(patho)} / Benign={len(benign)}")

    # 分层采样（与 sample_clinvar_testset.py 完全一致：seed=42）
    n_half = args.n // 2
    random.seed(42)
    sample = random.sample(patho, min(n_half, len(patho))) + \
             random.sample(benign, min(n_half, len(benign)))
    random.shuffle(sample)
    print(f"采样: {len(sample)} 变异")

    # 校验 AlleleID 唯一性
    ids = [r["AlleleID"] for r in sample]
    dup = len(ids) - len(set(ids))
    print(f"AlleleID 重复: {dup}")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in sample:
            w.writerow(row)
    print(f"✓ 测试集: {OUT_CSV} ({len(sample)} 行)")

    sig = Counter(r["ClinicalSignificance"] for r in sample)
    print("ClinicalSignificance 分布:", dict(sig))


if __name__ == "__main__":
    main()
