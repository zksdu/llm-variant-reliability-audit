# -*- coding: utf-8 -*-
"""
preprocess_clinvar.py — ClinVar variant_summary 解析与时间盲法采样

用途：把 ClinVar 的 variant_summary.txt.gz（421MB）解析成实验可用的变异记录，
      并按"时间盲法"策略采样测试集——只保留模型训练截止日期之后提交的变异。

为什么需要日期（核心设计）：
    数据泄漏控制是本文的关键创新。LLM 训练语料包含 ClinVar 历史数据，
    必须用"提交日期晚于模型训练截止"的变异做测试，才能测出真实泛化能力。
    variant_summary 有 Submitters/LastUpdated 等字段，但精确提交日期在
    variant_summary 里较粗；本脚本先解析基础字段，日期细化留待 ClinGen XML。

输出：
    data/clinvar_parsed.csv     （全量解析，字段见下）
    data/clinvar_testset.csv    （时间盲法测试集，按模型截止日期过滤）

依赖：标准库（gzip/csv/datetime）

使用：
    python preprocess_clinvar.py            # 解析全量
    python preprocess_clinvar.py --limit 1000   # 调试（只读前 N 行）
    python preprocess_clinvar.py --cutoff 2025-01-01   # 只保留此后提交的
"""
import sys
import csv
import gzip
import argparse
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_GZ = DATA_DIR / "variant_summary.txt.gz"
OUT_CSV = DATA_DIR / "clinvar_parsed.csv"
TEST_CSV = DATA_DIR / "clinvar_testset.csv"

# 关键字段（variant_summary 实际列名，2026-08 实测 43 列）
# 注意：该文件**无 gnomAD AF / DateLastUpdated 列**；人群频率需另查 gnomAD API，
#       日期盲法需用 ClinGen XML 或 RCV 提交日期（见注释）。
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

# 时间盲法：模型训练截止日期（估计值，论文中须声明）
# 参考：主流模型训练截止在 2025 年初~年中（GPT-4o ~2024-04, Claude 3.5 ~2024-11,
#        DeepSeek-V3 ~2024-12, DeepSeek-V4 ~2025 中）
# ⚠️ variant_summary 无 DateLastUpdated 列，时间盲法需换数据源：
#    （a）ClinGen 专家精审 XML（含提交日期）→ 最可靠
#    （b）ClinVar VCV XML（含 RCV 提交日期）
#    本脚本当前先按 ClinSigSimple 过滤 + 采样，日期过滤在 ClinGen 数据到位后补。
DEFAULT_CUTOFF = "2025-01-01"


def parse_row(raw_row: list) -> dict:
    """一行 tab 分隔 → 字段 dict（用官方列名）。"""
    return dict(zip(FIELDS, raw_row))


def main():
    ap = argparse.ArgumentParser(description="ClinVar 解析与时间盲法采样")
    ap.add_argument("--limit", type=int, default=None, help="调试：只读前 N 行")
    ap.add_argument("--cutoff", default=DEFAULT_CUTOFF,
                    help="时间盲法截止：只保留 DateLastUpdated 晚于此日期的变异")
    args = ap.parse_args()

    if not RAW_GZ.exists():
        sys.exit(f"✗ 找不到 {RAW_GZ}，请先下载 ClinVar variant_summary")

    print(f"解析 {RAW_GZ} ...")
    rows = []
    n_total = 0
    n_passed = 0
    cutoff = args.cutoff

    with gzip.open(RAW_GZ, "rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)  # 表头
        # 建列名索引（容忍列顺序变化）
        # ⚠️ ClinVar 表头第一列带 '#' 注释符（'#AlleleID'），须剥离才能匹配 FIELDS
        header = [h.lstrip("#").strip() for h in header]
        col_idx = {name: i for i, name in enumerate(header)}
        print(f"  列数: {len(header)}")
        for i, raw in enumerate(reader):
            if args.limit and i >= args.limit:
                break
            n_total += 1
            if len(raw) < len(header):
                continue
            r = {name: (raw[col_idx[name]] if name in col_idx else "")
                 for name in FIELDS}
            rows.append(r)

    print(f"  读取 {n_total} 行")

    # 过滤策略（variant_summary 无日期列，故不按时间过滤；只保留有临床分类的）
    # 时间盲法：后续用 ClinGen XML 的提交日期实现（见文件头注释）
    if args.limit:
        print(f"  （调试模式：不按时间过滤）")
        testset = rows
    else:
        testset = []
        for r in rows:
            # 只保留有明确临床分类的（去掉空/Conflicting）
            sig = r.get("ClinicalSignificance", "").strip()
            if sig and "Conflicting" not in sig and sig not in ("", "not provided"):
                testset.append(r)
        n_passed = len(testset)
        print(f"  有临床分类的变异: {n_passed} 行"
              f"（时间盲法待 ClinGen XML 日期）")

    # 写解析结果
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  ✓ 全量解析: {OUT_CSV} ({len(rows)} 行)")

    # 写测试集
    if testset:
        with TEST_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            for r in testset:
                w.writerow(r)
        print(f"  ✓ 测试集: {TEST_CSV} ({len(testset)} 行)")

    # 快速统计（验证数据质量）
    sig = Counter(r.get("ClinicalSignificance", "") for r in rows)
    print(f"\n  ClinicalSignificance 分布（前5）:")
    for k, v in sig.most_common(5):
        print(f"    {k or '(空)':40s} {v}")


if __name__ == "__main__":
    main()
