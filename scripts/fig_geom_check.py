# -*- coding: utf-8 -*-
"""fig_geom_check.py — 投稿图表几何质检（图例遮挡 / 跨面板文字溢出）。

用真实数据重建 fig1–fig5，并在渲染坐标（display px）下检测：
  1. 图例 bbox 与任何柱形/文本相交      -> 遮挡缺陷
  2. 任一 Text 艺术家 extent 落入其它面板 -> 跨面板文字溢出
不写 docs 目录（仅绘制到临时画布）。
savefig 使用 bbox_inches='tight'，导出前会并入所有艺术家范围，
因此不存在画布边缘裁切问题，不做边缘检查。

用法：python scripts/fig_geom_check.py   （在仓库根目录）
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import generate_figures_v2 as G  # noqa: E402


def overlap(a, b):
    """两个 Bbox 的交集面积；不相交为 0。"""
    x0 = max(a.x0, b.x0); x1 = min(a.x1, b.x1)
    y0 = max(a.y0, b.y0); y1 = min(a.y1, b.y1)
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def texts_of(ax):
    out = list(ax.texts)
    out += ax.get_xticklabels() + ax.get_yticklabels()
    if ax.title.get_text():
        out.append(ax.title)
    out += [t for t in (ax.xaxis.label, ax.yaxis.label) if t.get_text()]
    return out


def check(fig, name):
    problems = []
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()

    for ai, ax in enumerate(fig.axes):
        label = f"{name}.ax{ai}"
        leg = ax.get_legend()
        if leg is not None:
            lb = leg.get_window_extent(ren)
            for other in fig.axes:
                if other is ax:
                    continue
                a = overlap(lb, other.get_window_extent(ren))
                if a > 1:
                    problems.append(
                        f"{label}: legend overlaps {other.get_title()[:30]!r} "
                        f"axes area ({a:.0f} px^2)")
            for patch in ax.patches:
                pb = patch.get_window_extent(ren)
                a = overlap(lb, pb)
                if a > 4:
                    w, h = pb.x1 - pb.x0, pb.y1 - pb.y0
                    if w > 2 and h > 2:
                        problems.append(
                            f"{label}: legend overlaps a bar "
                            f"({a:.0f} px^2 of a {w:.0f}x{h:.0f} bar)")
            leg_texts = set(map(id, leg.get_texts()))
            for t in texts_of(ax):
                if not t.get_text() or id(t) in leg_texts:
                    continue
                tb2 = t.get_window_extent(ren)
                a = overlap(lb, tb2)
                if a > 1:
                    problems.append(
                        f"{label}: legend overlaps text {t.get_text()!r} "
                        f"(legend x[{lb.x0:.0f},{lb.x1:.0f}] "
                        f"y[{lb.y0:.0f},{lb.y1:.0f}] vs text "
                        f"x[{tb2.x0:.0f},{tb2.x1:.0f}] "
                        f"y[{tb2.y0:.0f},{tb2.y1:.0f}])")
        for t in texts_of(ax):
            if not t.get_text():
                continue
            tb = t.get_window_extent(ren)
            for other in fig.axes:
                if other is ax:
                    continue
                a = overlap(tb, other.get_window_extent(ren))
                if a > 1:
                    problems.append(
                        f"{label}: text {t.get_text()!r} spills into "
                        f"{other.get_title()[:30]!r} panel ({a:.0f} px^2)")
    return problems


def main():
    votes, gold, review = G.load()
    fig_registry = {}

    def spy_save(fig, name):
        fig_registry[name] = fig
        fig.canvas.draw()

    G.save = spy_save
    G.fig1(votes, gold)
    G.fig2()
    G.fig3()
    G.fig4(votes, gold)
    G.fig5(votes, gold, review)

    n_bad = 0
    for name, fig in fig_registry.items():
        probs = check(fig, name)
        if probs:
            n_bad += len(probs)
            print(f"[{name}]")
            for p in probs:
                print("   " + p)
        else:
            print(f"[{name}] clean")
    print(f"\n{len(fig_registry)} figures checked, {n_bad} geometric problems")
    plt.close("all")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
