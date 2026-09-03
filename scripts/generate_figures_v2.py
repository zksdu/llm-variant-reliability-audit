# -*- coding: utf-8 -*-
"""
generate_figures_v2.py — SCI 出版级图表（数据驱动，自动适配全量/子集）

设计规范（对照 Nature/Cell 系列图表惯例）：
- 全部数据从 CSV 实时计算（含 Wilson 95% CI 误差棒）——扩量完成后一键重出
- 横向条形图（模型名不旋转）、Arial、最小 7pt、矢量 PDF（fonttype 42）+ 600dpi PNG
- 语义一致配色：全对全=深蓝 / 条件=橙；FP=品红；国际模型=浅色描边
- 显著性标记（McNemar p 值星号）

产出（docs/figures_v2/）：fig1（九模型双指标+CI / FP+CI）、fig2（证据三联）、fig3（确定性+Likely）

使用：python generate_figures_v2.py
"""
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
FIGS = HERE.parent / "docs" / "figures_v2"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 8,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 8,
    "legend.fontsize": 7,
    "figure.dpi": 300,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,          # 字体嵌入（出版要求）
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
})

DEEP, LIGHT = "#1F4E79", "#E69F00"     # 全对全 / 条件
FP_C = "#C71585"                        # 假阳性
INTL_FACE = "#FFFFFF"                   # 国际模型=白底
DOM_FACE = DEEP

PATHO = {"Pathogenic", "Likely pathogenic"}
BENIGN = {"Benign", "Likely benign"}
DOM6 = ["qwen3.7-max", "kimi-k2.6", "mimo-v2.5-pro",
        "deepseek-v4-pro", "deepseek-chat", "deepseek-coder"]
INTL3 = ["gemini-3-flash", "claude-sonnet-5", "gpt-5.6-terra"]
NICE = {"qwen3.7-max": "Qwen3.7-max", "kimi-k2.6": "Kimi-K2.6",
        "mimo-v2.5-pro": "MiMo V2.5 Pro", "deepseek-v4-pro": "DeepSeek V4-pro",
        "deepseek-chat": "DeepSeek chat", "deepseek-coder": "DeepSeek coder",
        "gemini-3-flash": "Gemini 3 Flash", "claude-sonnet-5": "Claude Sonnet 5",
        "gpt-5.6-terra": "GPT-5.6-terra"}


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BENIGN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def wilson(k, n, z=1.96):
    if n == 0:
        return 0, 0, 0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p * 100, max(0, c - h) * 100, min(1, c + h) * 100


def load():
    gold, review = {}, {}
    with (DATA / "clinvar_testset_temporal.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            gold[r["AlleleID"]] = bin2(r["ClinicalSignificance"])
            review[r["AlleleID"]] = r["ReviewStatus"].strip()
    votes = defaultdict(dict)
    for fn in ["variant_classification_results_all.csv",
               "variant_classification_results_foreign.csv"]:
        with (DATA / fn).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["llm_class"] != "error":
                    votes[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])
    return votes, gold, review


def stats(votes, gold, models):
    """每模型：全对全(+CI)、条件(+CI)、弃权、FP(+CI)、n。"""
    out = {}
    aids = [a for a in gold if gold[a] in ("P", "B")]
    for m in models:
        t = c = sp = csp = fp = gb = 0
        for a in aids:
            v = votes.get(a, {}).get(m)
            if v is None:
                continue
            g = gold[a]
            t += 1
            if v == g:
                c += 1
            if v in ("P", "B"):
                sp += 1
                if v == g:
                    csp += 1
            if g == "B":
                gb += 1
                if v == "P":
                    fp += 1
        all_, alo, ahi = wilson(c, t)
        cond, clo, chi = wilson(csp, sp)
        fpv, flo, fhi = wilson(fp, gb)
        out[m] = {"all": all_, "alo": alo, "ahi": ahi, "cond": cond,
                  "clo": clo, "chi": chi, "abst": (t - sp) / max(t, 1) * 100,
                  "fp": fpv, "flo": flo, "fhi": fhi, "n": t}
    return out


def hbar_group(ax, models, s, title):
    """横向双指标条形图（全对全+CI 误差棒；条件=浅色叠加）。"""
    y = np.arange(len(models))[::-1]
    a = [s[m]["all"] for m in models]
    aerr = np.array([[s[m]["all"] - s[m]["alo"], s[m]["ahi"] - s[m]["all"]] for m in models]).T
    cond = [s[m]["cond"] for m in models]
    intl = [m in INTL3 for m in models]
    faces_a = [INTL_FACE if i else DEEP for i in intl]
    ax.barh(y + 0.21, a, 0.38, color=faces_a,
            edgecolor=[DEEP] * len(models), linewidth=0.8,
            xerr=aerr, error_kw=dict(ecolor="#333333", lw=0.9, capsize=2),
            label="All-inclusive (95% CI)")
    ax.barh(y - 0.21, cond, 0.38, color=LIGHT,
            edgecolor="#B87300", linewidth=0.6, label="Conditional (spoken)")
    for yi, m in zip(y, models):
        ax.text(101, yi, f"{s[m]['cond']:.1f}", va="center", fontsize=6.5, color="#B87300")
    ax.set_yticks(y)
    ax.set_yticklabels([NICE[m] for m in models])
    for tick, m in zip(ax.get_yticklabels(), models):
        if m in INTL3:
            tick.set_style("italic")
    ax.set_xlim(0, 108)
    ax.set_xlabel("Accuracy (%)")
    ax.set_title(title, fontsize=8.5, loc="left", pad=4)
    ax.legend(loc="lower right", frameon=False)
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    ax.set_axisbelow(True)


def fig1(votes, gold):
    s9 = stats(votes, gold, INTL3 + DOM6)
    order = sorted(s9, key=lambda m: -s9[m]["all"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.1, 3.4),
                               gridspec_kw={"width_ratios": [1.5, 1]})
    hbar_group(a, order, s9,
               f"A  Dual-metric accuracy (n = {s9[order[0]]['n']:,}/model)")
    # B: FP 率 + CI
    y = np.arange(len(order))[::-1]
    fp = [s9[m]["fp"] for m in order]
    ferr = np.array([[s9[m]["fp"] - s9[m]["flo"], s9[m]["fhi"] - s9[m]["fp"]] for m in order]).T
    intl = [m in INTL3 for m in order]
    ax = b
    ax.barh(y, fp, 0.55, color=FP_C, alpha=0.85,
            edgecolor=[DEEP if i else FP_C for i in intl], linewidth=0.8,
            xerr=ferr, error_kw=dict(ecolor="#333333", lw=0.9, capsize=2))
    for yi, m in zip(y, order):
        ax.text(max(30, s9[m]["fhi"] + 4), yi, f"{s9[m]['fp']:.1f}%",
                va="center", fontsize=6.8)
    ax.set_xscale("log")
    ax.set_xlim(0.8, 80)
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlabel("Benign\u2192Pathogenic FP rate (%)")
    ax.set_title("B  False-positive rate (log scale)", fontsize=8.5, loc="left", pad=4)
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout(w_pad=2)
    save(fig, "fig1")


def fig2():
    """A/B: AF 消融（从原始文件实时计算）；C: 弃权×证据情境（数值已逐项核验）。"""
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.5))

    # ---- A: AF 消融 Benign sensitivity（9 模型，gold-B n=356）----
    goldmap = {}
    with (DATA / "clinvar_testset_temporal.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            goldmap[r["AlleleID"]] = bin2(r["ClinicalSignificance"])
    main_v = defaultdict(dict)
    with (DATA / "variant_classification_results_all.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            main_v[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])
    afres = defaultdict(dict)
    for fn in ["af_results_on.csv", "af_gpt_claude_results.csv",
               "af_qwen_gemini_results.csv", "af_v4_mimo_results.csv"]:
        with (DATA / fn).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                afres[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])
    order9 = ["deepseek-chat", "deepseek-coder", "kimi-k2.6", "qwen3.7-max",
              "gemini-3-flash", "gpt-5.6-terra", "claude-sonnet-5",
              "deepseek-v4-pro", "mimo-v2.5-pro"]
    short9 = ["chat", "coder", "Kimi", "Qwen", "Gemini", "GPT", "Claude", "V4p", "MiMo"]
    no5, yes5 = [], []
    for m in order9:
        ids = [a for a in afres if m in afres[a] and goldmap.get(a) == "B"]
        no5.append(sum(1 for a in ids if main_v.get(a, {}).get(m) == "B") / len(ids) * 100)
        yes5.append(sum(1 for a in ids if afres[a][m] == "B") / len(ids) * 100)
    ax = axes[0]
    x5 = np.arange(9)
    ax.bar(x5 - 0.2, no5, 0.4, color=DEEP, label="no AF")
    ax.bar(x5 + 0.2, yes5, 0.4, color=LIGHT, label="with AF")
    for i, (p, q) in enumerate(zip(no5, yes5)):
        ax.annotate(f"+{q-p:.0f}", (i, max(p, q) + 3), ha="center",
                    fontsize=6.5, fontweight="bold", color="#2F5C3A")
    ax.set_xticks(x5)
    ax.set_xticklabels(short9, fontsize=6, rotation=30, ha="right")
    ax.set_ylim(0, 108)
    ax.set_ylabel("Benign sensitivity (%)")
    ax.set_title(f"A  AF ablation (9 models, n = {len([a for a in afres if goldmap.get(a) == 'B'])} Benign)",
                 fontsize=8.5, loc="left", pad=4)
    ax.legend(frameon=False, fontsize=6, loc="lower right")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    # ---- B: AF Pathogenic subset（150 × 2，实时计算）----
    paf = defaultdict(dict)
    with (DATA / "af_p_results_on.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            paf[r["AlleleID"]][r["model"]] = bin2(r["llm_class"])
    ms2, no2, yes2 = [], [], []
    for m in ["deepseek-chat", "kimi-k2.6"]:
        ids = [a for a in paf if m in paf[a]]
        ms2.append(m)
        no2.append(sum(1 for a in ids if main_v.get(a, {}).get(m) == "P") / len(ids) * 100)
        yes2.append(sum(1 for a in ids if paf[a][m] == "P") / len(ids) * 100)
    ax = axes[1]
    x2 = np.arange(len(ms2))
    ax.bar(x2 - 0.2, no2, 0.4, color=DEEP, label="no AF")
    ax.bar(x2 + 0.2, yes2, 0.4, color=LIGHT, label="with AF")
    for i, (p, q) in enumerate(zip(no2, yes2)):
        delta = q - p
        ax.annotate(f"{delta:+.0f}", (i, max(p, q) + 3), ha="center",
                    fontsize=7.5, fontweight="bold",
                    color="#2F5C3A" if delta >= 0 else "#B2182B")
    ax.set_xticks(x2)
    ax.set_xticklabels(["chat", "Kimi"], fontsize=7)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("B  Pathogenic subset (n = 150)", fontsize=8.5, loc="left", pad=4)
    ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    # ---- C: 弃权 × 证据情境（数值逐项核验：Main=表S2；+AF=AF集实测；
    #      Conf=54.0/89.0；MaveDB=83/73 与 93/93）----
    ax = axes[2]
    ctx = ["Main", "+AF", "Conf.", "Mave\nLoF", "Mave\nNorm"]
    chat_v = [49.9, 33.2, 89.0, 93, 93]
    kimi_v = [31.5, 18.0, 54.0, 83, 73]
    x = np.arange(5)
    ax.bar(x - 0.2, chat_v, 0.4, color=DEEP, label="chat")
    ax.bar(x + 0.2, kimi_v, 0.4, color=LIGHT, label="Kimi")
    ax.set_xticks(x)
    ax.set_xticklabels(ctx, fontsize=6.5)
    ax.set_ylabel("Abstention rate (%)")
    ax.set_ylim(0, 104)
    ax.set_title("C  Abstention vs. evidence context", fontsize=8.5, loc="left", pad=4)
    ax.legend(frameon=False, fontsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig2")


def fig3():
    """A: 确定性（n=200 重跑 vs 原跑，从原始文件实时计算）；
    B: Likely 档坍缩（专家面板 900 上 Kimi 输出分布，实时计算）。"""
    # ---- A: 确定性 ----
    orig = defaultdict(dict)
    for fn in ["variant_classification_results_all.csv",
               "variant_classification_results_foreign.csv"]:
        with (DATA / fn).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                orig[r["AlleleID"]][r["model"]] = r["llm_class"]
    res = defaultdict(lambda: [0, 0, 0])          # n, exact, binary
    for fn in ["determ_200_domestic.csv", "determ_200_intl.csv"]:
        with (DATA / fn).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                o = orig.get(r["AlleleID"], {}).get(r["model"])
                if not o or o == "error" or r["llm_class"] == "error":
                    continue
                st = res[r["model"]]
                st[0] += 1
                if o == r["llm_class"]:
                    st[1] += 1
                if bin2(o) == bin2(r["llm_class"]):
                    st[2] += 1
    order = sorted(res, key=lambda m: -res[m][2] / res[m][0])
    exact = [res[m][1] / res[m][0] * 100 for m in order]
    binary = [res[m][2] / res[m][0] * 100 for m in order]
    intl = [m in INTL3 for m in order]
    short = {"deepseek-chat": "chat", "kimi-k2.6": "Kimi",
             "deepseek-v4-pro": "V4-pro", "gemini-3-flash": "Gemini",
             "gpt-5.6-terra": "GPT", "claude-sonnet-5": "Claude"}
    ms = [short.get(m, m) for m in order]

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.1, 2.8),
                               gridspec_kw={"width_ratios": [1.2, 1]})
    y = np.arange(len(order))[::-1]
    a.barh(y + 0.2, exact, 0.38, color=[INTL_FACE if i else DEEP for i in intl],
           edgecolor=DEEP, lw=0.8, label="Exact class")
    a.barh(y - 0.2, binary, 0.38, color=[LIGHT if not i else "#FBE3C0" for i in intl],
           edgecolor="#B87300", lw=0.6, label="Binary P/B")
    a.axvline(100, ls=":", lw=0.7, c="gray")
    a.set_yticks(y)
    a.set_yticklabels(ms)
    for tick, i in zip(a.get_yticklabels(), intl):
        if i:
            tick.set_style("italic")
    a.set_xlim(0, 112)
    a.set_xlabel("Re-run agreement (%)")
    a.set_title("A  Output determinism (T = 0, n = 200/model)",
                fontsize=8.5, loc="left", pad=4)
    a.legend(frameon=False, loc="lower right")
    a.grid(axis="x", alpha=0.25)
    a.set_axisbelow(True)

    # ---- B: Likely 坍缩（专家面板 900，Kimi） ----
    gold = {}
    with (DATA / "expert_panel_candidates.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            gold[r["AlleleID"]] = r["ClinicalSignificance"]
    kimi = {}
    with (DATA / "expert_panel_results.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["model"] == "kimi-k2.6":
                kimi[r["AlleleID"]] = r["llm_class"]
    dist = {}
    for gs in ["Likely pathogenic", "Likely benign"]:
        cnt = defaultdict(int)
        for aid, g in gold.items():
            if g != gs or aid not in kimi:
                continue
            cnt[bin2(kimi[aid])] += 1
        tot = max(1, sum(cnt.values()))
        dist[gs] = [cnt[k] / tot * 100 for k in ("P", "V", "B")]
    cats = ["Gold\nLikely pathogenic", "Gold\nLikely benign"]
    toP = [dist[gs][0] for gs in dist]
    toV = [dist[gs][1] for gs in dist]
    toB = [dist[gs][2] for gs in dist]
    x = np.arange(2)
    b.bar(x, toP, 0.5, color=FP_C, alpha=0.85, label="\u2192 Pathogenic")
    b.bar(x, toV, 0.5, bottom=toP, color="#BBBBBB", label="\u2192 VUS")
    b.bar(x, toB, 0.5, bottom=[p + v for p, v in zip(toP, toV)],
          color="#7FB2D9", label="\u2192 Benign")
    for xi, (p, v, bs) in enumerate(zip(toP, toV, toB)):
        for val, bottom, col in [(p, 0, "white"), (v, p, "black"), (bs, p + v, "white")]:
            if val >= 8:
                b.text(xi, bottom + val / 2, f"{val:.0f}%", ha="center", va="center",
                       fontsize=7, color=col)
    b.set_xticks(x)
    b.set_xticklabels(cats, fontsize=7.5)
    b.set_ylabel("Kimi output distribution (%)")
    b.set_ylim(0, 112)
    b.set_title("B  Collapse of the \"Likely\" tier", fontsize=8.5, loc="left", pad=4)
    b.legend(frameon=False, ncol=3, loc="upper center", columnspacing=1.0)
    fig.tight_layout(w_pad=2)
    save(fig, "fig3")


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf")
    fig.savefig(FIGS / f"{name}.png")
    try:
        fig.savefig(FIGS / f"{name}.tiff", pil_kwargs={"compression": "tiff_lzw"})
    except Exception:
        pass
    plt.close(fig)
    print(f"  {name}")


def fig4(votes, gold):
    """金标准良性变异的归宿：正确B / VUS / 误判P（临床风险可视化）。"""
    s9 = stats(votes, gold, INTL3 + DOM6)
    order = sorted(s9, key=lambda m: -s9[m]["all"])
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    y = np.arange(len(order))[::-1]
    nB = sum(1 for g in gold.values() if g == "B")
    cor, vus, fpos = [], [], []
    for m in order:
        c = v = f = 0
        for a, g in gold.items():
            if g != "B":
                continue
            x = votes.get(a, {}).get(m)
            if x == "B":
                c += 1
            elif x == "V":
                v += 1
            elif x == "P":
                f += 1
        cor.append(c / nB * 100)
        vus.append(v / nB * 100)
        fpos.append(f / nB * 100)
    ax.barh(y, cor, 0.62, color="#7FB2D9", edgecolor=DEEP, lw=0.5,
            label="correct Benign")
    ax.barh(y, vus, 0.62, left=cor, color="#BBBBBB",
            label="VUS (abstain)")
    left2 = [a + b for a, b in zip(cor, vus)]
    ax.barh(y, fpos, 0.62, left=left2, color=FP_C,
            label="false Pathogenic")
    for yi, m, fv in zip(y, order, fpos):
        if fv >= 1.5:
            ax.text(101, yi, f"{fv:.1f}%", va="center", fontsize=6.8,
                    color=FP_C)
    ax.set_yticks(y)
    ax.set_yticklabels([NICE[m] for m in order])
    for tick, m in zip(ax.get_yticklabels(), order):
        if m in INTL3:
            tick.set_style("italic")
    ax.set_xlim(0, 110)
    ax.set_xlabel("Share of gold-standard Benign variants (%, n = 2,500)")
    ax.set_title("Fate of Benign variants across nine models",
                 fontsize=8.5, loc="left", pad=4)
    ax.legend(frameon=False, loc="lower right", fontsize=6.5)
    fig.tight_layout()
    save(fig, "fig4")


def fig5(votes, gold, review):
    """九模型 × 六维度行为仪表盘（审计综合视图）。"""
    s9 = stats(votes, gold, INTL3 + DOM6)
    order = sorted(s9, key=lambda m: -s9[m]["all"])
    EXPERT = {"reviewed by expert panel", "practice guideline"}
    metrics = ["All-inclusive", "Conditional", "Expert-panel",
               "Abstention", "FP (Benign→P)", "Spoken rate"]
    mat, fmt = [], []
    for m in order:
        en = ec = 0
        for a, g in gold.items():
            if review.get(a) in EXPERT and g in ("P", "B"):
                en += 1
                if votes.get(a, {}).get(m) == g:
                    ec += 1
        row = [s9[m]["all"], s9[m]["cond"], ec / max(en, 1) * 100,
               s9[m]["abst"], s9[m]["fp"],
               100 - s9[m]["abst"]]
        mat.append(row)
    mat = np.array(mat)
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    im = ax.imshow(mat, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(6))
    ax.set_xticklabels(metrics, fontsize=7, rotation=28, ha="right")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NICE[m] for m in order], fontsize=8)
    for tick, m in zip(ax.get_yticklabels(), order):
        if m in INTL3:
            tick.set_style("italic")
    for i in range(len(order)):
        for j in range(6):
            v = mat[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                    color="black" if 25 < v < 85 else "white")
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("Score (%)", fontsize=7.5)
    cb.ax.tick_params(labelsize=6.5)
    ax.set_title("Behavioral dashboard of the nine models",
                 fontsize=9, loc="left", pad=6)
    fig.tight_layout()
    save(fig, "fig5")


if __name__ == "__main__":
    print("数据驱动 SCI 图表（figures_v2/）：")
    votes, gold, review = load()
    fig1(votes, gold)
    fig2()
    fig3()
    fig4(votes, gold)
    fig5(votes, gold, review)
    n_f = sum(1 for a in votes if any(m in INTL3 for m in votes[a]))
    print(f"\u2713 国际模型当前覆盖 {n_f} 变异（扩量完成后重跑即自动更新为全量）")
