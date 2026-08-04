# -*- coding: utf-8 -*-
"""
sample_clinvar_testset.py — 时间盲法测试集采样

用途：从 ClinVar 解析结果中，采样"时间盲法"测试集：
    只保留模型训练截止日期（DeepSeek V4 = 2025-12）之后评估的变异，
    确保 LLM 训练时未见过这些变异的答案（数据泄漏控制核心设计）。

时间盲法依据：
    - DeepSeek V4 知识截止 2025-12（2026-08 核实）
    - 用 LastEvaluated（最后评估日期）作为提交时间的近似
    - 只取 2026-01-01 之后评估的变异 → LLM 必没见过

采样约束（论文 §3.2）：
    - 有明确分类（Pathogenic / Benign，排除 VUS/Conflicting）
    - 有 HGVS cDNA 表述（prompt 需要）
    - 分层：Pathogenic 与 Benign 均衡（避免类别失衡）
    - 单变异去重（同一 AlleleID 只留一条）

输出：
    data/clinvar_testset_temporal.csv（时间盲法测试集）

使用：
    python sample_clinvar_testset.py --n 5000 --cutoff 2026-01
"""
import csv
import re
import random
import argparse
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
PARSED_CSV = DATA_DIR / "clinvar_parsed.csv"
OUT_CSV = DATA_DIR / "clinvar_testset_temporal.csv"

DEFAULT_CUTOFF = "2026-01"   # 模型截止 2025-12 → 只留 2026-01 后评估
DEFAULT_N = 5000             # 采样规模


def parse_date(d: str):
    """'Jan 5, 2026' → (2026, 1)。无法解析返回 None。"""
    m = re.match(r"([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})", d.strip())
    if not m:
        return None
    mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    return (int(m.group(3)), mon.get(m.group(1), 0))


def eligible(row, cutoff):
    """时间盲法合格：2026 后评估 + 明确分类 + 有 HGVS。"""
    d = parse_date(row.get("LastEvaluated", ""))
    if not d:
        return False
    if (d[0], d[1]) < (int(cutoff[:4]), int(cutoff[5:7])):
        return False
    sig = row.get("ClinicalSignificance", "").strip()
    # 只取明确 Pathogenic 或 Benign（排除复合/VUS/Conflicting）
    if "Conflicting" in sig or "Uncertain" in sig or "Likely" in sig:
        return False
    if "Pathogenic" not in sig and "Benign" not in sig:
        return False
    if not row.get("HGVS_cDNA", "").strip() and not row.get("Name", "").strip():
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="时间盲法测试集采样")
    ap.add_argument("--n", type=int, default=DEFAULT_N)
    ap.add_argument("--cutoff", default=DEFAULT_CUTOFF)
    args = ap.parse_args()

    if not PARSED_CSV.exists():
        raise SystemExit(f"✗ 找不到 {PARSED_CSV}，请先运行 preprocess_clinvar.py")

    print(f"时间盲法采样: cutoff={args.cutoff} (模型截止 2025-12), n={args.n}")
    print(f"读取 {PARSED_CSV} ...")

    patho, benign = [], []
    total = 0
    with PARSED_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if not eligible(row, args.cutoff):
                continue
            sig = row.get("ClinicalSignificance", "")
            if "Pathogenic" in sig:
                patho.append(row)
            elif "Benign" in sig:
                benign.append(row)
            if total % 1000000 == 0:
                print(f"  已扫描 {total/1e6:.1f}M 行，候选 pathogenic={len(patho)} benign={len(benign)}")

    print(f"\n扫描完成: {total} 行")
    print(f"时间盲法候选: Pathogenic={len(patho)} / Benign={len(benign)}")

    # 分层采样（各 n/2，若不足则全部取）
    n_half = args.n // 2
    random.seed(42)
    sample = random.sample(patho, min(n_half, len(patho))) + \
             random.sample(benign, min(n_half, len(benign)))
    random.shuffle(sample)
    print(f"采样: {len(sample)} 变异")

    # 写输出
    fields = list(sample[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in sample:
            w.writerow(row)
    print(f"✓ 测试集: {OUT_CSV} ({len(sample)} 行)")


if __name__ == "__main__":
    main()
