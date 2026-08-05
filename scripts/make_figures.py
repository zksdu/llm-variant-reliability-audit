# -*- coding: utf-8 -*-
"""
make_figures.py — 生信论文终版图表

输入：data/experiment_results_all6.csv（6 模型 × 5000 变异）
      data/clinvar_testset_temporal.csv（金标准）
输出：data/figures/fig1_acc.png（全对全 vs 表态时，双维度散点+柱状）
      data/figures/fig2_goldstrat.png（金标准分层柱状图）
      data/figures/fig3_cm.png（共识混淆矩阵热力图）
"""
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
FIG_DIR = DATA_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

RESULTS = DATA_DIR / "experiment_results_all6.csv"
GOLD = DATA_DIR / "clinvar_testset_temporal.csv"

MODELS = ["qwen3.7-max", "kimi-k2.6", "mimo-v2.5-pro",
          "deepseek-v4-pro", "deepseek-chat", "deepseek-coder"]
MODEL_LABEL = {
    "qwen3.7-max": "Qwen3.7-Max", "kimi-k2.6": "Kimi-K2.6",
    "mimo-v2.5-pro": "MiMo V2.5 Pro", "deepseek-v4-pro": "DeepSeek V4-Pro",
    "deepseek-chat": "DeepSeek V3-Chat", "deepseek-coder": "DeepSeek V3-Coder",
}
PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}
GOLD_A_STRICT = {"reviewed by expert panel", "practice guideline"}
GOLD_A_BROAD = GOLD_A_STRICT | {"criteria provided, multiple submitters, no conflicts"}


def bin_class(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def load():
    gold = {}
    review = {}
    with GOLD.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            aid = r.get("AlleleID", "").strip()
            if aid:
                gold[aid] = r.get("ClinicalSignificance", "").strip()
                review[aid] = r.get("ReviewStatus", "").strip()
    res = defaultdict(dict)
    with RESULTS.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            aid = r.get("AlleleID", "").strip()
            m = r.get("model", "").strip()
            if aid and m:
                res[aid][m] = r.get("llm_class", "").strip()
    return res, gold, review


def metrics(preds, gold, review, rset=None):
    """全对全 + 表态时准确率。"""
    all_c = all_t = 0
    spoke_c = spoke_t = 0
    fp = fn = 0
    for aid, cls in preds.items():
        if aid not in gold:
            continue
        if rset is not None and review.get(aid, "") not in rset:
            continue
        gc = bin_class(gold[aid])
        if gc not in ("P", "B"):
            continue
        pc = bin_class(cls)
        all_t += 1
        if pc == gc:
            all_c += 1
        if pc in ("P", "B"):
            spoke_t += 1
            if pc == gc:
                spoke_c += 1
            if pc == "P" and gc == "B":
                fp += 1
            if pc == "B" and gc == "P":
                fn += 1
    return {
        "all": all_c / all_t if all_t else None,
        "spoke": spoke_c / spoke_t if spoke_t else None,
        "spoke_n": spoke_t,
        "fp": fp, "fn": fn,
    }


def main():
    res, gold, review = load()
    full = {a: d for a, d in res.items() if all(m in d for m in MODELS)}
    print(f"6 模型齐全: {len(full)} 变异")

    # ---- 图 1：全对全 vs 表态时（散点，气泡=表态率）----
    fig, ax = plt.subplots(figsize=(9, 6.5))
    colors = {"qwen3.7-max": "#d62728", "kimi-k2.6": "#2ca02c",
              "mimo-v2.5-pro": "#ff7f0e", "deepseek-v4-pro": "#9467bd",
              "deepseek-chat": "#1f77b4", "deepseek-coder": "#8c564b"}
    for m in MODELS:
        preds = {a: d[m] for a, d in full.items()}
        met = metrics(preds, gold, review)
        if met["all"] is None or met["spoke"] is None:
            continue
        spoke_rate = met["spoke_n"] / len(full)
        ax.scatter(met["all"] * 100, met["spoke"] * 100,
                   s=spoke_rate * 3000, color=colors[m], alpha=0.75,
                   edgecolors="black", linewidths=1, zorder=3)
        ax.annotate(MODEL_LABEL[m], (met["all"] * 100, met["spoke"] * 100),
                    textcoords="offset points", xytext=(10, 6),
                    fontsize=10, fontweight="bold")
    ax.axhline(98.5, color="gray", ls="--", lw=1, alpha=0.6)
    ax.text(51, 99.3, "Kimi/chat/coder 表态即正确 (~98%)", fontsize=9, color="gray")
    ax.set_xlabel("Overall accuracy (VUS=error) %", fontsize=12)
    ax.set_ylabel("Accuracy when decisive %", fontsize=12)
    ax.set_title("6 模型 × 5000 变异（时间盲法）：全对全 vs 表态时准确率\n"
                 "气泡大小 = 表态率（敢下结论的比例）", fontsize=12)
    ax.set_xlim(45, 75)
    ax.set_ylim(70, 105)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_acc.png", dpi=200)
    plt.close(fig)
    print("✓ fig1_acc.png")

    # ---- 图 2：金标准分层柱状图 ----
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(MODELS))
    width = 0.26
    for i, (rset, label) in enumerate([(None, "All (n=5,000)"),
                                       (GOLD_A_BROAD, "Gold-A broad (n=3,131)"),
                                       (GOLD_A_STRICT, "Gold-A strict (n=100)")]):
        vals = []
        for m in MODELS:
            preds = {a: d[m] for a, d in full.items()}
            met = metrics(preds, gold, review, rset)
            vals.append(met["all"] * 100 if met["all"] else 0)
        ax.bar(x + (i - 1) * width, vals, width, label=label,
               color=["#8ecae6", "#219ebc", "#023047"][i])
        for j, v in enumerate(vals):
            ax.text(x[j] + (i - 1) * width, v + 1, f"{v:.0f}",
                    ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS], rotation=20, fontsize=9)
    ax.set_ylabel("全对全准确率 %", fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_title("Accuracy by gold-standard tier (ClinVar all / multi-submitter / expert panel)", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_goldstrat.png", dpi=200)
    plt.close(fig)
    print("✓ fig2_goldstrat.png")

    # ---- 图 3：6 模型共识混淆矩阵 ----
    cons_preds = {}
    for aid, d in full.items():
        cnt = Counter(d[m] for m in MODELS)
        top = cnt.most_common(2)
        if len(top) == 1:
            cls = top[0][0]
        elif top[0][1] == top[1][1]:
            continue  # tie 弃权
        else:
            cls = top[0][0]
        if bin_class(cls) in ("P", "B"):
            cons_preds[aid] = cls
    cm = np.zeros((3, 2), dtype=int)
    for aid, cls in cons_preds.items():
        if aid not in gold or bin_class(gold[aid]) not in ("P", "B"):
            continue
        pc = {"P": 0, "B": 1, "V": 2, "O": 2}[bin_class(cls)]
        gc = {"P": 0, "B": 1}[bin_class(gold[aid])]
        cm[pc, gc] += 1
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=max(cm.max() * 1.2, 1))
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Gold: Pathogenic", "Gold: Benign"], fontsize=11)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Model: Pathogenic", "Model: Benign", "Model: VUS"], fontsize=11)
    for i in range(3):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    fontsize=14, color="white" if cm[i, j] > cm.max() * 0.5 else "black")
    ax.set_title("6 模型共识混淆矩阵（n=%d）\nP 敏感度 %.1f%% | B 敏感度 %.1f%%" % (
        cm.sum(), 100 * cm[0, 0] / max(cm[0, 0] + cm[1, 0] + cm[2, 0], 1),
        100 * cm[1, 1] / max(cm[0, 1] + cm[1, 1] + cm[2, 1], 1)), fontsize=12)
    fig.colorbar(im, shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_cm.png", dpi=200)
    plt.close(fig)
    print("✓ fig3_cm.png")
    print(f"  共识: 假阳性(P→B)={cm[0,1]} 假阴性(B→P)={cm[1,0]}")


if __name__ == "__main__":
    main()
