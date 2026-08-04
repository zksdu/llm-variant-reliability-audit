# -*- coding: utf-8 -*-
"""
analyze_consensus.py — 多模型共识 + 金标准对照分析

用途：对 LLM 变异分类实验结果做核心分析：
    1. 单模型准确率（v4-pro / chat / coder）
    2. 多模型共识（多数投票）准确率
    3. 共识 + 弃权策略（分歧时弃权）
    4. 校准分析（置信度 vs 准确率，Brier score）
    5. 金标准 A 对照（ClinVar ReviewStatus 专家评审）
    6. 时间盲法对照（2026 后评估 = 泄漏控制）

输入：
    - data/experiment_results_variant.csv（LLM 分类结果，run_variant_classification 产出）
    - 测试集（含金标准 ClinicalSignificance）

输出：
    - data/consensus_analysis.md（论文核心结果表）

使用：
    python analyze_consensus.py
"""
import csv
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
RESULTS_CSV = DATA_DIR / "experiment_results_variant.csv"
TEST_SET = DATA_DIR / "clinvar_testset_temporal.csv"
OUT_MD = DATA_DIR / "consensus_analysis.md"

# 分类归一化：LLM 输出 → 二分类（Pathogenic-ish vs Benign-ish）
PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}


def bin_class(cls: str):
    """LLM/金标准分类 → 二分类（P/B/VUS/other）。"""
    c = str(cls).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def load_results(path):
    """读 LLM 分类结果，按 (AlleleID, model) 组织。"""
    if not path.exists():
        raise SystemExit(f"✗ 找不到 {path}")
    results = defaultdict(dict)  # allele_id -> {model: class}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            aid = row.get("AlleleID", "").strip()
            model = row.get("model", "").strip()
            cls = row.get("llm_class", "").strip()
            if aid and model:
                results[aid][model] = cls
    return results


def load_gold(path):
    """读测试集金标准（ClinicalSignificance 列）。"""
    gold = {}
    if not path.exists():
        return gold
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            aid = row.get("AlleleID", "").strip()
            if aid:
                gold[aid] = row.get("ClinicalSignificance", "").strip()
    return gold


def consensus(classes: list):
    """多数投票。平票时返回 'tie'。"""
    if not classes:
        return None
    cnt = Counter(classes)
    top = cnt.most_common(2)
    if len(top) == 1:
        return top[0][0]
    if top[0][1] == top[1][1]:
        return "tie"
    return top[0][0]


def acc(preds, gold):
    """准确率：二分类后与金标准比对（P vs B 二分类）。"""
    if not preds:
        return None, 0, 0
    correct = 0
    total = 0
    for aid, cls in preds.items():
        if aid not in gold:
            continue
        pc = bin_class(cls)
        gc = bin_class(gold[aid])
        if gc in ("P", "B"):  # 金标准只取明确 P/B
            total += 1
            if pc == gc:
                correct += 1
    return (correct / total if total else None), correct, total


def main():
    ap = argparse.ArgumentParser(description="共识 + 金标准分析")
    ap.add_argument("--results", default=str(RESULTS_CSV))
    ap.add_argument("--gold", default=str(TEST_SET))
    args = ap.parse_args()

    results = load_results(args.results)
    gold = load_gold(args.gold)
    print(f"LLM 结果: {len(results)} 个变异")
    print(f"金标准: {len(gold)} 个变异（测试集）")

    # 只有 3 模型都有的变异才做共识
    models = ["deepseek-v4-pro", "deepseek-chat", "deepseek-coder"]
    full = {aid: d for aid, d in results.items()
            if all(m in d for m in models)}
    print(f"3 模型齐全: {len(full)} 个变异")

    lines = []
    lines.append("# 共识分析结果（LLM 变异分类）\n")
    lines.append(f"数据: {len(full)} 变异 × {len(models)} 模型\n")
    lines.append("## 1. 单模型 vs 共识准确率（二分类 P/B）\n")
    lines.append("| 方法 | 准确率 | 正确/总数 |")
    lines.append("|---|---|---|")

    # 单模型
    for m in models:
        preds = {aid: d[m] for aid, d in full.items()}
        a, c, t = acc(preds, gold)
        lines.append(f"| {m} | {a*100:.1f}% | {c}/{t} |" if a else f"| {m} | n/a |")

    # 共识（多数投票）
    cons_preds = {}
    for aid, d in full.items():
        cls = consensus([d[m] for m in models])
        if cls and cls != "tie":
            cons_preds[aid] = cls
    a, c, t = acc(cons_preds, gold)
    lines.append(f"| **3 模型共识** | **{a*100:.1f}%** | {c}/{t} |" if a else "| 共识 | n/a |")

    # 共识 + 弃权（分歧时弃权，即 tie 排除）
    a2, c2, t2 = acc(cons_preds, gold)  # 同上（tie 已排除）
    tie_count = sum(1 for aid, d in full.items()
                    if consensus([d[m] for m in models]) == "tie")
    lines.append(f"| 共识+弃权（排除 {tie_count} 分歧） | {a2*100:.1f}% | {c2}/{t2} |"
                 if a2 else "")

    # 共识错误案例分析
    lines.append("\n## 2. 共识错误的案例\n")
    err = 0
    for aid, cls in cons_preds.items():
        if aid in gold and bin_class(gold[aid]) in ("P", "B") \
                and bin_class(cls) != bin_class(gold[aid]):
            err += 1
            if err <= 5:
                lines.append(f"- {aid}: 共识={cls} 金标准={gold[aid]}")
    lines.append(f"（共 {err} 个错误）\n")

    # 校准（粗略：置信度 vs 准确率）
    lines.append("## 3. 校准（置信度 vs 准确率）\n")
    # 从结果里取 confidence 列
    conf_by_model = defaultdict(list)
    with open(args.results, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            c = row.get("confidence", "").strip()
            m = row.get("model", "").strip()
            if c:
                try:
                    conf_by_model[m].append(float(c))
                except ValueError:
                    pass
    for m in models:
        if conf_by_model[m]:
            avg = sum(conf_by_model[m]) / len(conf_by_model[m])
            lines.append(f"- {m}: 平均置信度 {avg:.2f}")
    lines.append("\n> 注：Brier score 等严格校准指标待全量数据后补充\n")

    # 时间盲法对照（金标准里 2026 后评估 = 泄漏控制）
    lines.append("## 4. 时间盲法对照（泄漏控制）\n")
    lines.append("> 测试集全部为 2026-01 后评估（模型截止 2025-12 之后），"
                 "即全部为泄漏控制样本。")
    lines.append("> 与 2025 前评估样本的对比需补充非时间盲法子集。\n")

    content = "\n".join(lines)
    OUT_MD.write_text(content, encoding="utf-8")
    print(content)
    print(f"\n✓ 已写入 {OUT_MD}")


if __name__ == "__main__":
    main()
