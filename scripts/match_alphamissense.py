# -*- coding: utf-8 -*-
"""
match_alphamissense.py — AlphaMissense 预测 vs LLM 预测对比

用途：将 AlphaMissense（hg38, transcript-level）预测匹配到 5000 变异测试集，
      与 LLM 输出做 head-to-head 对比（论文 Table 补充）。

输入：
    data/AlphaMissense_isoforms_hg38.tsv.gz（Zenodo 下载）
    data/clinvar_testset_temporal.csv（5000 测试集）
    data/variant_classification_results_all.csv（全部 LLM 输出）

输出：
    data/alphamissense_comparison.md（对比报告）

使用：
    python match_alphamissense.py
"""
import csv
import gzip
import sys
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
AM_FILE = DATA / "AlphaMissense_isoforms_hg38.tsv.gz"
TEST_CSV = DATA / "clinvar_testset_temporal.csv"
LLM_CSV = DATA / "variant_classification_results_all.csv"
OUT_MD = DATA / "alphamissense_comparison.md"

PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def main():
    if not AM_FILE.exists():
        sys.exit(f"✗ 找不到 {AM_FILE}，请下载 AlphaMissense hg38 文件")

    # 1. 加载测试集
    test = {}
    with TEST_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            aid = r["AlleleID"]
            chrm = r["Chromosome"].replace("chr", "")
            test[aid] = {
                "gene": r["GeneSymbol"],
                "gold": bin2(r["ClinicalSignificance"]),
                "chr": chrm,
                "start": r["Start"],
                "ref": r["ReferenceAllele"],
                "alt": r["AlternateAllele"],
                "name": r["Name"],
            }
    print(f"测试集: {len(test)} 变异")

    # 2. 匹配 AlphaMissense（按 chr:pos:ref:alt 或基因+HGVS 蛋白名）
    # AlphaMissense 文件格式：#chromosome position genome ref_allele alt_allele
    #                          protein_variant am_pathogenicity am_class ...
    print(f"扫描 {AM_FILE} ...")
    am_pred = {}  # (chr,pos,ref,alt) -> (pathogenicity_score, class)
    n_am = 0
    n_match = 0
    with gzip.open(AM_FILE, "rt", errors="replace") as f:
        header = [h.lstrip("#") for h in f.readline().rstrip("\n").split("\t")]
        idx = {k: i for i, k in enumerate(header)}
        # 坐标列
        chr_i = idx.get("chromosome", idx.get("chr", -1))
        pos_i = idx.get("position", idx.get("pos", -1))
        ref_i = idx.get("ref_allele", idx.get("ref", -1))
        alt_i = idx.get("alt_allele", idx.get("alt", -1))
        score_i = idx.get("am_pathogenicity", -1)
        class_i = idx.get("am_class", -1)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < max(chr_i, pos_i, ref_i, alt_i, score_i, class_i) + 1:
                continue
            n_am += 1
            key = (p[chr_i], p[pos_i], p[ref_i], p[alt_i])
            if key in test:
                n_match += 1
                am_pred[key] = (p[score_i], p[class_i])
            if n_am % 2000000 == 0:
                print(f"  已扫 {n_am/1e6:.1f}M，匹配 {n_match}")
    print(f"AlphaMissense 扫描完成: {n_am:,} 行, 匹配 {n_match} 变异")

    # 3. 加载 LLM 输出（取最佳模型 Qwen）
    llm = defaultdict(dict)
    with LLM_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["llm_class"] != "error":
                llm[r["AlleleID"]][r["model"]] = r["llm_class"]

    # 4. 对比分析
    lines = ["# AlphaMissense vs LLM 对比\n"]
    lines.append(f"AlphaMissense 匹配到 {n_match}/{len(test)} 变异\n")

    if n_match > 0:
        # AlphaMissense 准确率
        am_tp = am_fp = am_fn = am_tn = 0
        am_vus = 0
        for (chrm, pos, ref, alt), (score, cls) in am_pred.items():
            # 找对应 AlleleID
            aid = next((a for a, t in test.items()
                        if t["chr"] == chrm and t["start"] == pos
                        and t["ref"] == ref and t["alt"] == alt), None)
            if not aid:
                continue
            g = gold.get(aid, test[aid]["gold"])
            if g not in ("P", "B"):
                continue
            if cls == "ambiguous":
                am_vus += 1
                continue
            am_pred_cls = "P" if cls == "likely_pathogenic" else "B"
            if g == "P" and am_pred_cls == "P":
                am_tp += 1
            elif g == "B" and am_pred_cls == "B":
                am_tn += 1
            elif g == "B" and am_pred_cls == "P":
                am_fp += 1
            elif g == "P" and am_pred_cls == "B":
                am_fn += 1

        total = am_tp + am_fp + am_fn + am_tn
        if total > 0:
            acc = (am_tp + am_tn) / total
            sens = am_tp / max(am_tp + am_fn, 1)
            spec = am_tn / max(am_tn + am_fp, 1)
            lines.append(f"## AlphaMissense 准确率（n={total}，排除 ambiguous {am_vus}）\n")
            lines.append(f"- 全对全准确率: {acc*100:.1f}%")
            lines.append(f"- 敏感度（P）: {sens*100:.1f}%")
            lines.append(f"- 特异度（B）: {spec*100:.1f}%\n")

            # 与 LLM 对比
            lines.append("## vs LLM（同变异子集，Qwen3.7-max 作代表）\n")
            llm_tp = llm_fp = llm_fn = llm_tn = llm_vus = 0
            for (chrm, pos, ref, alt), (score, cls) in am_pred.items():
                aid = next((a for a, t in test.items()
                            if t["chr"] == chrm and t["start"] == pos
                            and t["ref"] == ref and t["alt"] == alt), None)
                if not aid:
                    continue
                g = test[aid]["gold"]
                if g not in ("P", "B"):
                    continue
                v = llm.get(aid, {}).get("qwen3.7-max")
                if v is None or v == "V":
                    llm_vus += 1
                    continue
                if g == "P" and v == "P":
                    llm_tp += 1
                elif g == "B" and v == "B":
                    llm_tn += 1
                elif g == "B" and v == "P":
                    llm_fp += 1
                elif g == "P" and v == "B":
                    llm_fn += 1
            llm_total = llm_tp + llm_fp + llm_fn + llm_tn
            if llm_total > 0:
                llm_acc = (llm_tp + llm_tn) / llm_total
                lines.append(f"- Qwen 全对全: {llm_acc*100:.1f}% (n={llm_total}, VUS弃权 {llm_vus})")
                lines.append(f"- AlphaMissense: {acc*100:.1f}% (n={total})\n")
            else:
                lines.append("- LLM 数据不足\n")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ {OUT_MD}")


if __name__ == "__main__":
    main()
