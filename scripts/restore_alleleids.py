# -*- coding: utf-8 -*-
"""
restore_alleleids.py — 恢复实验 CSV 的 AlleleID 主键

背景：run_variant_classification.py 的输入 temporal 文件因解析 bug 导致
      AlleleID 列全空，300 行实验结果（100 变异 × 3 模型）丢失主键。
      实验按输入顺序运行（每变异 3 行：v4-pro, chat, coder），
      重建后的 temporal（seed=42）顺序与旧文件完全一致，
      故可按顺序恢复，并以 (GeneSymbol, ClinicalSignificance) 双重校验。

使用：
    python restore_alleleids.py
"""
import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
EXPERIMENT_CSV = DATA_DIR / "experiment_results_variant.csv"
TEMPORAL_CSV = DATA_DIR / "clinvar_testset_temporal.csv"
N_MODELS = 3


def main():
    if not TEMPORAL_CSV.exists():
        sys.exit(f"✗ 先运行 rebuild_temporal.py（{TEMPORAL_CSV} 不存在）")

    with TEMPORAL_CSV.open("r", encoding="utf-8", newline="") as f:
        temporal = list(csv.DictReader(f))
    with EXPERIMENT_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    n_var = len(rows) // N_MODELS
    if len(rows) % N_MODELS != 0:
        sys.exit(f"✗ 实验行数 {len(rows)} 不是 3 的倍数，无法按变异分组")
    print(f"实验 {len(rows)} 行 = {n_var} 变异 × {N_MODELS} 模型")
    print(f"temporal 共 {len(temporal)} 变异")

    # 逐变异恢复
    n_match = 0
    for i in range(n_var):
        ref = temporal[i]
        ref_key = (ref["GeneSymbol"], ref["ClinicalSignificance"])
        aid = ref["AlleleID"].strip()
        if not aid:
            sys.exit(f"✗ temporal[{i}] AlleleID 为空（重建脚本输出异常）")
        for k in range(N_MODELS):
            r = rows[i * N_MODELS + k]
            got_key = (r["GeneSymbol"], r["prompt_class"])
            if got_key != ref_key:
                sys.exit(
                    f"✗ 变异 {i} 校验失败：实验 {got_key} ≠ temporal {ref_key}\n"
                    f"  说明顺序不一致，禁止盲目恢复主键。")
        for k in range(N_MODELS):
            rows[i * N_MODELS + k]["AlleleID"] = aid
        n_match += 1

    print(f"✓ 全部 {n_match} 个变异校验通过，AlleleID 已恢复")

    # 校验恢复结果
    nonempty = sum(1 for r in rows if r["AlleleID"].strip())
    if nonempty != len(rows):
        sys.exit(f"✗ 恢复后仍有 {len(rows) - nonempty} 行 AlleleID 为空")
    ids = [r["AlleleID"] for r in rows]
    if len(set(ids)) != n_var:
        sys.exit(f"✗ AlleleID 去重后 {len(set(ids))} ≠ {n_var}，可能未唯一")

    with EXPERIMENT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"✓ 已写回 {EXPERIMENT_CSV}（{len(rows)} 行）")
    print(f"  覆盖 {n_var} 个唯一 AlleleID")


if __name__ == "__main__":
    main()
