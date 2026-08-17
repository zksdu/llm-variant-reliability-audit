# -*- coding: utf-8 -*-
"""
merge_results.py — 合并多个模型的实验结果 CSV 为单文件

用途：run_variant_classification.py 每个模型/任务产出独立 CSV，
      analyze_consensus.py 需要读取合并后的单文件。

使用：
    python merge_results.py data/variant_classification_results_all.csv
"""
import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# 参与合并的文件（顺序无影响，模型名是主键）
SOURCES = [
    "variant_classification_results_v4.csv",
    "variant_classification_results_cc.csv",
    "variant_classification_results_kimi.csv",
    "variant_classification_results_mimo.csv",
    "variant_classification_results_qwen.csv",
    "variant_classification_results_foreign.csv",  # 3 个国际模型（全量 5000）
]


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else \
        "variant_classification_results_all.csv"
    out_path = DATA_DIR / out_name

    fieldnames = None
    n = 0
    with out_path.open("w", encoding="utf-8", newline="") as fo:
        writer = None
        for fn in SOURCES:
            p = DATA_DIR / fn
            if not p.exists():
                print(f"  （跳过，不存在）{fn}")
                continue
            with p.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if fieldnames is None:
                    fieldnames = reader.fieldnames
                    writer = csv.DictWriter(fo, fieldnames=fieldnames)
                    writer.writeheader()
                for row in reader:
                    writer.writerow(row)
                    n += 1
        print(f"✓ 合并 {n} 行 → {out_path}")


if __name__ == "__main__":
    main()
