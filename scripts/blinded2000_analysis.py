# -*- coding: utf-8 -*-
"""
blinded2000_analysis.py — 专用完全盲集（n=2,000）分析归档

数据：data/blinded2000_results.csv（3 国际模型 × 2,000 变异，2026-09 运行）
金标准：结果内联 prompt_class 列（运行器原样写入输入的金标准）。
      注：本次运行输出的 AlleleID 列为空（输入文件当时带 # 表头 bug），
      故只做聚合统计与无配对检验；样本文件已用同 seed 修复再生成
      （data/blinded2000_set.csv，确定性同样本，带 AlleleID）。

使用：python blinded2000_analysis.py
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = DATA / "blinded2000_analysis.md"
PATHO = {"Pathogenic", "Likely pathogenic"}
BEN = {"Benign", "Likely benign"}
MODELS = ["gemini-3-flash", "claude-sonnet-5", "gpt-5.6-terra"]


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return "P"
    if c in BEN:
        return "B"
    if "Uncertain" in c:
        return "V"
    return "O"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def two_prop(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return z, pv


def main():
    rows = list(csv.DictReader((DATA / "blinded2000_results.csv").open(encoding="utf-8")))
    S = {}
    for m in MODELS:
        t = c = sp = csp = fp = gb = pn = pc = bn = bc = 0
        for r in rows:
            if r["model"] != m:
                continue
            g, v = bin2(r["prompt_class"]), bin2(r["llm_class"])
            t += 1
            if v == g:
                c += 1
            if v in "PB":
                sp += 1
                if v == g:
                    csp += 1
            if g == "B":
                gb += 1
                bn += 1
                if v == "P":
                    fp += 1
                if v == "B":
                    bc += 1
            if g == "P":
                pn += 1
                if v == "P":
                    pc += 1
        lo, hi = wilson(c, t)
        S[m] = dict(t=t, c=c, sp=sp, csp=csp, fp=fp, gb=gb,
                    acc=c / t * 100, lo=lo * 100, hi=hi * 100,
                    cond=csp / sp * 100, abst=(t - sp) / t * 100,
                    fpr=fp / gb * 100, psens=pc / pn * 100, bsens=bc / bn * 100)

    lines = ["# 专用完全盲集分析（n=2,000；LastEvaluated ≥ 2026-04；seed 42）", "",
             "运行：2026-09，3 国际模型 × 2,000（P 1,000 / B 1,000），AF 关闭，研究语境 system prompt。",
             "金标准来自结果内联 prompt_class 列（AlleleID 空值说明见文件头）。", "",
             "| 模型 | 全对全 (95%CI) | 条件 | 弃权 | FP(B→P) | P敏感 | B敏感 | 解析失败 |",
             "|---|---|---|---|---|---|---|---|"]
    errs = defaultdict(int)
    for r in rows:
        if r["llm_class"].strip().lower() in ("", "error"):
            errs[r["model"]] += 1
    for m in MODELS:
        s = S[m]
        lines.append(f"| {m} | {s['acc']:.1f}% [{s['lo']:.1f},{s['hi']:.1f}] | "
                     f"{s['cond']:.1f}% | {s['abst']:.1f}% | {s['fpr']:.1f}% | "
                     f"{s['psens']:.1f}% | {s['bsens']:.1f}% | {errs[m]} |")

    lines += ["", "## 无配对双比例检验（z，双侧）", ""]
    for a, b in [("gemini-3-flash", "claude-sonnet-5"),
                 ("gemini-3-flash", "gpt-5.6-terra"),
                 ("claude-sonnet-5", "gpt-5.6-terra")]:
        z1, p1_ = two_prop(S[a]["c"], S[a]["t"], S[b]["c"], S[b]["t"])
        z2, p2_ = two_prop(S[a]["fp"], S[a]["gb"], S[b]["fp"], S[b]["gb"])
        lines.append(f"- 全对全 {a} vs {b}: z={z1:.2f}, p={p1_:.4g}")
        lines.append(f"- FP {a} vs {b}: z={z2:.2f}, p={p2_:.4g}")

    lines += ["", "## 结论要点", "",
              "1. Gemini 与 Claude 统计不可区分（全对全与 FP 均 n.s.）——Gemini 的全集领先在完全盲下不复存在。",
              "2. GPT-5.6-terra 显著落后（p<1e-30）且为激进异常值（FP 25.0%、B 敏感 32.8%）。",
              "3. Gemini 的 FP 行为跨运行不稳定：8 月主运行 ≥2026-04 分层 22.1% vs 本次专用集 5.2%"
              "（同为完全盲、同为中转端点）——与其已记录的非确定性及中转版本漂移一致；Claude 保守画像跨所有估计稳定（3.9–4.5%）。"]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\n✓ {OUT}")


if __name__ == "__main__":
    main()
