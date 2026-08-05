# -*- coding: utf-8 -*-
"""
annotate_af.py — 从 ClinVar VCF 按 ALLELEID 匹配等位基因频率

用途：给时间盲法测试集补充 AF_ESP / AF_EXAC / AF_TGP 等位频率，
      供"有 AF vs 无 AF"对照实验（验证 Benign 弃权是否因信息缺失）。

输入：
    data/clinvar.vcf.gz          （用户迅雷下载的 ClinVar VCF，~190MB）
    data/clinvar_testset_temporal.csv（5000 变异时间盲法测试集）

输出：
    data/clinvar_testset_af.csv  （temporal 全部列 + AF_ESP/AF_EXAC/AF_TGP）

使用：
    python annotate_af.py
"""
import csv
import gzip
import re
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
VCF_GZ = DATA_DIR / "clinvar.vcf.gz"
TEST_CSV = DATA_DIR / "clinvar_testset_temporal.csv"
OUT_CSV = DATA_DIR / "clinvar_testset_af.csv"

AF_FIELDS = ["AF_ESP", "AF_EXAC", "AF_TGP"]


def parse_info(info: str):
    """INFO 字符串 → dict（key=value 对，注意带 ';' 的需转义处理）。"""
    d = {}
    for kv in info.split(";"):
        if "=" in kv:
            k, _, v = kv.partition("=")
            d[k] = v
        else:
            d[kv] = ""
    return d


def main():
    if not VCF_GZ.exists():
        sys.exit(f"✗ 找不到 {VCF_GZ}，请先下载 ClinVar VCF")
    if not TEST_CSV.exists():
        sys.exit(f"✗ 找不到 {TEST_CSV}")

    # 1. 扫描 VCF，收集 ALLELEID → AF
    print(f"扫描 {VCF_GZ} ...")
    af_map = {}  # ALLELEID -> {AF_ESP, AF_EXAC, AF_TGP}
    n_vcf = 0
    with gzip.open(VCF_GZ, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 8:
                continue
            info = parse_info(parts[7])
            aid = info.get("ALLELEID", "")
            if not aid:
                continue
            n_vcf += 1
            afs = {k: info.get(k, "") for k in AF_FIELDS}
            if any(afs.values()):  # 只保留有 AF 的行
                af_map[aid] = afs
            if n_vcf % 500000 == 0:
                print(f"  已扫 {n_vcf/1e6:.1f}M 行，AF 记录 {len(af_map):,}")
    print(f"VCF 扫描完成: {n_vcf:,} 行, 含 AF 的 {len(af_map):,}")

    # 2. 匹配测试集
    rows = []
    with TEST_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            aid = row.get("AlleleID", "").strip()
            afs = af_map.get(aid, {})
            row["AF_ESP"] = afs.get("AF_ESP", "")
            row["AF_EXAC"] = afs.get("AF_EXAC", "")
            row["AF_TGP"] = afs.get("AF_TGP", "")
            rows.append(row)

    n_hit = sum(1 for r in rows if r["AF_ESP"] or r["AF_EXAC"] or r["AF_TGP"])
    print(f"测试集 {len(rows)} 变异, 匹配到 AF 的 {n_hit}（覆盖率 {n_hit/len(rows)*100:.1f}%）")

    # 3. 写出
    fieldnames = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"✓ 已写出 {OUT_CSV}")

    # 4. AF 分布速览（匹配到的）
    esps = [float(r["AF_ESP"]) for r in rows if r["AF_ESP"]]
    if esps:
        esps.sort()
        print(f"AF_ESP 分布（n={len(esps)}）: min={esps[0]} p50={esps[len(esps)//2]} max={esps[-1]}")


if __name__ == "__main__":
    main()
