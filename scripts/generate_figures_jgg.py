# -*- coding: utf-8 -*-
"""
generate_figures_jgg.py — JGG 投稿规格图表（4 张主图，合并原 6 张）

JGG 合规点：
- Arial 字体；字号 >= 6pt；面板标 A/B/C（10pt）
- 色盲安全配色（不并列红绿）
- 尺寸 175mm（双栏全宽）；线图矢量 PDF + TIFF 300dpi
- 无图内大标题（标题在图注）

数据全部来自已验证的实验结果（与论文正文一致）。
使用：python generate_figures_jgg.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

FIGS = Path(__file__).parent.parent / "docs" / "figures_jgg"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# 色盲安全（Okabe-Ito 子集，无红绿并列）
BLUE, ORANGE, PURPLE, SKY, BLACK, YELLOW = (
    "#0072B2", "#E69F00", "#CC79A7", "#56B4E9", "#000000", "#F0E442")

W = 6.89  # 175 mm


def panel_label(ax, s):
    ax.text(-0.13, 1.06, s, transform=ax.transAxes, fontsize=10,
            fontweight="regular", va="top", ha="left")


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf")
    fig.savefig(FIGS / f"{name}.png")
    try:
        fig.savefig(FIGS / f"{name}.tiff", pil_kwargs={"compression": "tiff_lzw"})
    except Exception:
        pass
    plt.close(fig)
    print(f"  {name}")


# ============ Fig 1 ============
def fig1():
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(W, 2.7))
    # A: 六国内模型（5000）
    ms1 = ["V4-pro", "chat", "coder", "Kimi", "MiMo", "Qwen"]
    all1 = [61.8, 49.4, 49.2, 67.0, 66.1, 71.6]
    cond1 = [81.2, 98.6, 98.7, 97.8, 85.2, 96.4]
    x = np.arange(6)
    a.bar(x - 0.2, all1, 0.4, color=BLUE, label="All-inclusive")
    a.bar(x + 0.2, cond1, 0.4, color=ORANGE, label="Conditional")
    a.axhline(50, ls=":", lw=0.6, c="gray")
    a.set_xticks(x); a.set_xticklabels(ms1, rotation=38, ha="right")
    a.set_ylabel("Accuracy (%)"); a.set_ylim(0, 106)
    a.legend(loc="lower right")
    panel_label(a, "A")
    # B: 九模型同 500 子集
    ms2 = ["Gemini", "Claude", "Qwen", "Kimi", "MiMo", "GPT", "V4-pro", "chat", "coder"]
    all2 = [80.2, 73.8, 73.4, 67.8, 66.6, 63.4, 63.0, 47.0, 47.4]
    cond2 = [89.7, 97.4, 96.1, 98.0, 86.9, 84.1, 84.0, 98.3, 98.3]
    intl = [1, 1, 0, 0, 0, 1, 0, 0, 0]
    x2 = np.arange(9)
    b.bar(x2 - 0.2, all2, 0.4, color=[SKY if i else BLUE for i in intl],
          label="All-inclusive")
    b.bar(x2 + 0.2, cond2, 0.4, color=[YELLOW if i else ORANGE for i in intl],
          label="Conditional")
    b.set_xticks(x2); b.set_xticklabels(ms2, rotation=42, ha="right")
    b.set_ylim(0, 106); b.set_ylabel("Accuracy (%)")
    b.legend(loc="lower right")
    panel_label(b, "B")
    # C: FP 率（log）
    fp = [17.4, 3.6, 5.7, 2.8, 19.4, 23.9, 24.3, 1.6, 1.6]
    bars = c.bar(x2, fp, 0.6, color=[PURPLE if i else BLUE for i in intl])
    c.set_yscale("log"); c.set_ylim(1, 60)
    for r, v in zip(bars, fp):
        c.text(r.get_x() + r.get_width() / 2, v * 1.15, f"{v:.1f}",
               ha="center", fontsize=6)
    c.axhline(1.76, ls="--", lw=0.7, c=BLACK)
    c.text(8.4, 2.0, "consensus 1.8%", fontsize=6, ha="right")
    c.set_xticks(x2); c.set_xticklabels(ms2, rotation=42, ha="right")
    c.set_ylabel("Benign\u2192Pathogenic FP (%)")
    panel_label(c, "C")
    fig.tight_layout()
    save(fig, "fig1_JGG")


# ============ Fig 2 ============
def fig2():
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(W, 2.5))
    # A: AF Benign 敏感度
    ms = ["chat", "coder", "Kimi"]
    no = [11.0, 10.7, 43.4]; yes = [68.8, 68.3, 81.5]
    x = np.arange(3)
    a.bar(x - 0.2, no, 0.4, color=BLUE, label="No AF")
    a.bar(x + 0.2, yes, 0.4, color=ORANGE, label="With AF")
    for i, (p, q) in enumerate(zip(no, yes)):
        a.text(i, max(p, q) + 3, f"+{q-p:.0f}", ha="center", fontsize=7, color=BLACK)
    a.set_xticks(x); a.set_xticklabels(ms)
    a.set_ylabel("Benign sensitivity (%)"); a.set_ylim(0, 100)
    a.legend(loc="lower right")
    panel_label(a, "A")
    # B: AF Pathogenic 子集
    ms2 = ["chat", "Kimi"]; no2 = [44.9, 47.5]; yes2 = [64.0, 85.3]
    x2 = np.arange(2)
    b.bar(x2 - 0.2, no2, 0.4, color=BLUE)
    b.bar(x2 + 0.2, yes2, 0.4, color=ORANGE)
    for i, (p, q) in enumerate(zip(no2, yes2)):
        b.text(i, max(p, q) + 2, f"+{q-p:.0f}", ha="center", fontsize=7, color=BLACK)
    b.set_xticks(x2); b.set_xticklabels(ms2)
    b.set_ylabel("Accuracy, Pathogenic subset (%)"); b.set_ylim(0, 100)
    b.legend(["No AF", "With AF"], loc="lower right")
    panel_label(b, "B")
    # C: 弃权率 × 证据情境
    ctx = ["Main", "+AF", "Conflict", "MaveDB\n(LoF)", "MaveDB\n(Norm)"]
    chat_v = [49.9, 33.2, 89.0, 93, 93]
    kimi_v = [31.5, 18.0, 54.0, 83, 73]
    x3 = np.arange(5)
    c.bar(x3 - 0.2, chat_v, 0.4, color=BLUE, label="chat")
    c.bar(x3 + 0.2, kimi_v, 0.4, color=ORANGE, label="Kimi")
    c.set_xticks(x3); c.set_xticklabels(ctx, fontsize=6.5)
    c.set_ylabel("Abstention rate (%)"); c.set_ylim(0, 104)
    c.legend(loc="upper left")
    panel_label(c, "C")
    fig.tight_layout()
    save(fig, "fig2_JGG")


# ============ Fig 3 ============
def fig3():
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6))
    # A: 确定性
    ms = ["chat", "Kimi", "V4-pro", "Gemini", "GPT", "Claude"]
    exact = [100, 98, 62, 80, 85, 75]
    binary = [100, 100, 64, 95, 85, 80]
    intl = [0, 0, 0, 1, 1, 1]
    x = np.arange(6)
    a.bar(x - 0.2, exact, 0.4, color=[SKY if i else BLUE for i in intl],
          label="Exact class")
    a.bar(x + 0.2, binary, 0.4, color=[YELLOW if i else ORANGE for i in intl],
          label="Binary P/B")
    a.axhline(100, ls=":", lw=0.6, c="gray")
    a.set_xticks(x); a.set_xticklabels(ms, rotation=30, ha="right")
    a.set_ylabel("Re-run agreement (%)"); a.set_ylim(0, 112)
    a.legend(loc="lower left", ncol=2)
    panel_label(a, "A")
    # B: Likely 档坍缩（Kimi）
    cats = ["Gold Likely\npathogenic", "Gold Likely\nbenign"]
    toP = [82, 14]; toV = [15, 33]; toB = [3, 53]
    x2 = np.arange(2)
    b.bar(x2, toP, 0.5, color=PURPLE, label="\u2192 Pathogenic")
    b.bar(x2, toV, 0.5, bottom=toP, color="#BBBBBB", label="\u2192 VUS")
    b.bar(x2, toB, 0.5, bottom=[p + v for p, v in zip(toP, toV)],
          color=SKY, label="\u2192 Benign")
    b.set_xticks(x2); b.set_xticklabels(cats)
    b.set_ylabel("Kimi output distribution (%)")
    b.legend(loc="upper center", ncol=3, framealpha=0.9)
    b.set_ylim(0, 118)
    panel_label(b, "B")
    fig.tight_layout()
    save(fig, "fig3_JGG")


# ============ Fig 4 ============
def fig4():
    data = [
        ("chat", 0.001, 49.4, 2.3, BLUE),
        ("coder", 0.001, 49.2, 2.5, BLUE),
        ("Kimi", 0.003, 67.0, 5.9, BLUE),
        ("V4-pro", 0.017, 61.8, 65.9, PURPLE),
        ("Qwen", 0.019, 71.6, 37.7, BLUE),
        ("MiMo", 0.041, 66.1, 30.6, PURPLE),
    ]
    fig, ax = plt.subplots(figsize=(4.3, 3.2))
    for name, cost, acc, lat, cc in data:
        ax.scatter(cost, acc, s=lat * 14, c=cc, alpha=0.75,
                   edgecolors=BLACK, linewidths=0.5, zorder=3)
        dy = 0.8 if name != "coder" else -1.6
        ax.annotate(name, (cost + 0.0006, acc + dy), fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("Cost per variant (\u00a5, log scale)")
    ax.set_ylabel("All-inclusive accuracy (%)")
    ax.set_ylim(44, 76)
    ax.grid(alpha=0.22)
    panel_label(ax, "")
    fig.tight_layout()
    save(fig, "fig4_JGG")


if __name__ == "__main__":
    print("生成 JGG 图表：")
    fig1(); fig2(); fig3(); fig4()
    print(f"\u2713 输出至 {FIGS}")
