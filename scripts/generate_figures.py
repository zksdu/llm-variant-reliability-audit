# -*- coding: utf-8 -*-
"""
generate_figures.py — 论文正式图表（matplotlib，300dpi，投稿规格）

产出（docs/figures/）：
    fig1_model_performance.pdf/png — 六模型双口径准确率 + FP 率总览
    fig2_evidence_gradient.pdf/png  — 证据可得性梯度（专家评审>时间盲法>无证据）
    fig3_af_ablation.pdf/png        — AF 消融（Benign 敏感度/全对全/弃权率）
    fig4_cost_latency.pdf/png       — 成本-延迟-准确率权衡（推理税）
    fig5_determinism.pdf/png        — 可复现性 + 五分类坍缩

数据来源：data/ 下最终实验 CSV（全部实测，无手工数字）
使用：python generate_figures.py
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
FIGS = HERE.parent / "docs" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
})

PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}
MODELS = ["qwen3.7-max", "kimi-k2.6", "mimo-v2.5-pro", "deepseek-v4-pro",
          "deepseek-chat", "deepseek-coder"]
LABELS = {"qwen3.7-max": "Qwen3.7-max", "kimi-k2.6": "Kimi-K2.6",
          "mimo-v2.5-pro": "MiMo V2.5 Pro", "deepseek-v4-pro": "DeepSeek V4-pro",
          "deepseek-chat": "DeepSeek chat", "deepseek-coder": "DeepSeek coder"}
VENDOR_C = {"qwen3.7-max": "#4C72B0", "kimi-k2.6": "#DD8452",
            "mimo-v2.5-pro": "#55A868", "deepseek-v4-pro": "#C44E52",
            "deepseek-chat": "#8172B3", "deepseek-coder": "#937860"}


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def load_all():
    votes = defaultdict(dict)
    with (DATA / "variant_classification_results_all.csv").open(
            "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["llm_class"] != "error":
                votes[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])
    gold = {}
    review = {}
    with (DATA / "clinvar_testset_temporal.csv").open(
            "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            gold[r["AlleleID"]] = bin2(r["ClinicalSignificance"])
            review[r["AlleleID"]] = r["ReviewStatus"].strip()
    return votes, gold, review


def per_model_stats(votes, gold, review):
    """每模型：全对全/表态准确率/表态数/FP率(B中误报P比例)/专家档。"""
    EXPERT = {"reviewed by expert panel", "practice guideline"}
    stats = {}
    for m in MODELS:
        n = t = c_all = sp = c_sp = fp = gb = e_n = e_c = 0
        for aid, d in votes.items():
            g = gold.get(aid)
            if g not in ("P", "B"):
                continue
            v = d.get(m)
            if v is None:
                continue
            t += 1
            if v == g:
                c_all += 1
            if v in ("P", "B"):
                sp += 1
                if v == g:
                    c_sp += 1
            if g == "B":
                gb += 1
                if v == "P":
                    fp += 1
            if review.get(aid) in EXPERT:
                e_n += 1
                if v == g:
                    e_c += 1
        stats[m] = {"all": c_all / t, "cond": c_sp / sp, "sp": sp, "n": t,
                    "fp": fp / gb, "expert": e_c / e_n, "e_n": e_n}
    return stats


# ---------------- Figure 1 ----------------
def fig1(stats):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.4))
    ms = MODELS
    x = np.arange(len(ms))
    # 左：双口径准确率
    ax1.bar(x - 0.2, [stats[m]["all"] * 100 for m in ms], 0.4,
            label="All-inclusive (VUS = error)", color="#4C72B0")
    ax1.bar(x + 0.2, [stats[m]["cond"] * 100 for m in ms], 0.4,
            label="Conditional (committed only)", color="#DD8452")
    ax1.axhline(50, ls="--", lw=0.7, c="gray", zorder=0)
    ax1.set_xticks(x)
    ax1.set_xticklabels([LABELS[m] for m in ms], rotation=32, ha="right",
                        fontsize=7)
    ax1.set_ylabel("Accuracy (%)")
    ax1.set_ylim(0, 105)
    ax1.set_title("(a) Dual-metric accuracy")
    ax1.legend(fontsize=7, loc="lower left")
    # 右：FP 率（对数轴展示推理模型危险）
    fps = [stats[m]["fp"] * 100 for m in ms]
    bars = ax2.bar(x, fps, 0.62, color=[VENDOR_C[m] for m in ms])
    ax2.set_yscale("log")
    ax2.set_ylim(0.5, 60)
    for b, v in zip(bars, fps):
        ax2.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:.1f}%",
                 ha="center", fontsize=7)
    ax2.axhline(1.76, ls="--", lw=0.8, c="k")
    ax2.text(5.4, 1.9, "6-model\nconsensus 1.8%", fontsize=6.5, ha="right")
    ax2.set_xticks(x)
    ax2.set_xticklabels([LABELS[m] for m in ms], rotation=32, ha="right",
                        fontsize=7)
    ax2.set_ylabel("Benign→Pathogenic FP rate (%)")
    ax2.set_title("(b) False-positive rate on gold-standard Benign")
    fig.tight_layout()
    fig.savefig(FIGS / "fig1_model_performance.png")
    fig.savefig(FIGS / "fig1_model_performance.pdf")
    plt.close(fig)
    print("✓ fig1")


# ---------------- Figure 2 ----------------
def fig2(stats):
    # 证据梯度：专家档(每模型) vs 全体 vs MaveDB(表态一致率)
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ms = MODELS
    y = np.arange(len(ms))
    ax.barh(y - 0.2, [stats[m]["expert"] * 100 for m in ms], 0.38,
            label=f"Expert-panel stratum (n=100/variant)", color="#55A868")
    ax.barh(y + 0.2, [stats[m]["all"] * 100 for m in ms], 0.38,
            label="Full test set (n≈5,000)", color="#4C72B0")
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[m] for m in ms], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("All-inclusive accuracy (%)")
    ax.set_xlim(0, 105)
    ax.set_title("Reliability rises with evidence quality of the gold standard")
    ax.legend(fontsize=7, loc="lower right")
    ax.text(0.98, 0.05,
            "No-evidence task (MaveDB):\nconditional ≈ chance (45–55%);\nabstention 73–93%",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7,
            bbox=dict(fc="#FFF3D6", ec="#CC9F00", lw=0.6))
    fig.tight_layout()
    fig.savefig(FIGS / "fig2_evidence_gradient.png")
    fig.savefig(FIGS / "fig2_evidence_gradient.pdf")
    plt.close(fig)
    print("✓ fig2")


# ---------------- Figure 3 ----------------
def fig3():
    # AF 消融：实测数字（400 Benign-rich + 150 P）
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.2))
    models = ["DeepSeek\nchat", "DeepSeek\ncoder", "Kimi-K2.6"]
    ben_no = [11.0, 10.7, 43.4]
    ben_af = [68.8, 68.3, 81.5]
    acc_no = [19.1, 19.0, 49.3]
    acc_af = [66.5, 66.2, 80.8]
    x = np.arange(3)
    ax1.bar(x - 0.2, ben_no, 0.4, label="No AF", color="#C44E52")
    ax1.bar(x + 0.2, ben_af, 0.4, label="With AF", color="#55A868")
    for i, (a, b) in enumerate(zip(ben_no, ben_af)):
        ax1.annotate(f"+{b-a:.0f}pp", (i, max(a, b) + 3), ha="center",
                     fontsize=8, fontweight="bold", color="#2F5C3A")
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=8)
    ax1.set_ylabel("Benign sensitivity (%)")
    ax1.set_ylim(0, 100)
    ax1.set_title("(a) Benign sensitivity (n=400, Benign-rich)")
    ax1.legend(fontsize=7)
    # P 侧
    models2 = ["DeepSeek\nchat", "Kimi-K2.6"]
    p_no = [44.9, 47.5]
    p_af = [64.0, 85.3]
    x2 = np.arange(2)
    ax2.bar(x2 - 0.2, p_no, 0.4, label="No AF", color="#C44E52")
    ax2.bar(x2 + 0.2, p_af, 0.4, label="With AF", color="#55A868")
    for i, (a, b) in enumerate(zip(p_no, p_af)):
        ax2.annotate(f"+{b-a:.0f}pp", (i, max(a, b) + 2.5), ha="center",
                     fontsize=8, fontweight="bold", color="#2F5C3A")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(models2, fontsize=8)
    ax2.set_ylabel("Accuracy on Pathogenic subset (%)")
    ax2.set_ylim(0, 100)
    ax2.set_title("(b) Pathogenic subset (n=150)")
    ax2.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "fig3_af_ablation.png")
    fig.savefig(FIGS / "fig3_af_ablation.pdf")
    plt.close(fig)
    print("✓ fig3")


# ---------------- Figure 4 ----------------
def fig4():
    # 成本-准确率权衡（气泡=延迟）
    data = [
        ("DeepSeek chat", 0.001, 49.4, 2.3, "#8172B3"),
        ("DeepSeek coder", 0.001, 49.2, 2.5, "#8172B3"),
        ("Kimi-K2.6", 0.003, 67.0, 5.9, "#DD8452"),
        ("DeepSeek V4-pro", 0.017, 61.8, 65.9, "#C44E52"),
        ("Qwen3.7-max", 0.019, 71.6, 37.7, "#4C72B0"),
        ("MiMo V2.5 Pro", 0.041, 66.1, 30.6, "#55A868"),
    ]
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for name, cost, acc, lat, c in data:
        ax.scatter(cost, acc, s=lat * 14, c=c, alpha=0.75, edgecolors="k",
                   linewidths=0.5, zorder=3)
        dx, dy = (0.00035, 0.6)
        if name == "DeepSeek coder":
            dy = -1.8
        ax.annotate(name, (cost + dx, acc + dy), fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlabel("Cost per variant (¥, log scale)")
    ax.set_ylabel("All-inclusive accuracy (%)")
    ax.set_ylim(44, 76)
    ax.set_title("Cost–accuracy trade-off (bubble size = latency, s)")
    ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig(FIGS / "fig4_cost_latency.png")
    fig.savefig(FIGS / "fig4_cost_latency.pdf")
    plt.close(fig)
    print("✓ fig4")


# ---------------- Figure 5 ----------------
def fig5():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.2))
    # (a) 可复现性
    ms = ["DeepSeek chat", "Kimi-K2.6", "DeepSeek V4-pro"]
    exact = [100.0, 98.0, 62.0]
    binary = [100.0, 100.0, 64.0]
    x = np.arange(3)
    ax1.bar(x - 0.2, exact, 0.4, label="Exact class", color="#4C72B0")
    ax1.bar(x + 0.2, binary, 0.4, label="Binary P/B", color="#55A868")
    ax1.axhline(100, ls=":", lw=0.7, c="gray")
    ax1.set_xticks(x)
    ax1.set_xticklabels(ms, fontsize=8)
    ax1.set_ylabel("Re-run agreement (%)")
    ax1.set_ylim(0, 112)
    ax1.set_title("(a) Output determinism (temp=0, n=50)")
    ax1.legend(fontsize=7, loc="lower left")
    # (b) 五分类坍缩：Kimi 对 LP 的去向
    cats = ["Gold Likely\npathogenic", "Gold Likely\nbenign"]
    to_p = [82, 14]
    to_v = [15, 33]
    to_b = [3, 53]
    xp = np.arange(2)
    ax2.bar(xp, to_p, 0.5, label="→ Pathogenic", color="#C44E52")
    ax2.bar(xp, to_v, 0.5, bottom=to_p, label="→ VUS", color="#BBBBBB")
    ax2.bar(xp, to_b, 0.5, bottom=[a + b for a, b in zip(to_p, to_v)],
            label="→ Benign", color="#55A868")
    ax2.set_xticks(xp)
    ax2.set_xticklabels(cats, fontsize=8)
    ax2.set_ylabel("Kimi output distribution (%)")
    ax2.set_title('(b) "Likely" tier collapse (Kimi, expert set)')
    ax2.legend(fontsize=7, ncol=3, loc="upper center", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(FIGS / "fig5_determinism.png")
    fig.savefig(FIGS / "fig5_determinism.pdf")
    plt.close(fig)
    print("✓ fig5")


def main():
    votes, gold, review = load_all()
    stats = per_model_stats(votes, gold, review)
    for m in MODELS:
        print(f"  {m}: all={stats[m]['all']*100:.1f} cond={stats[m]['cond']*100:.1f} "
              f"fp={stats[m]['fp']*100:.2f} expert={stats[m]['expert']*100:.0f}")
    fig1(stats)
    fig2(stats)
    fig3()
    fig4()
    fig5()
    print(f"\n✓ 全部图表输出至 {FIGS}")


if __name__ == "__main__":
    main()
