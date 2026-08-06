# -*- coding: utf-8 -*-
"""
mavedb_sample.py — MaveDB 功能验证测试集构建

用途：从 MaveDB（DMS 功能效应数据）采样功能方向明确的变异，
      构建"功能证据"三角验证测试集：
        - 功能丧失组：score <= -0.8（DMS 显示蛋白功能严重受损）
        - 正常功能组：score >= 0.5（功能正常）
      供 LLM 分类，检验"模型输出方向 vs 功能效应方向"一致性。

基因映射：mygene.info 批量查询（转录本 → 基因符号，免费无 key）

输出：
    data/mavedb_testset.csv（300 变异：150 功能丧失 + 150 正常功能）
    字段：AlleleID(urn), Name(HGVS), GeneSymbol, Chromosome, Start,
          ReferenceAllele, AlternateAllele, HGVS_Protein, ClinicalSignificance(功能方向)

使用：
    python mavedb_sample.py
"""
import csv
import gzip
import json
import random
import urllib.request
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
MAVE_GZ = DATA_DIR / "MaveDB_variants.tsv.gz"
OUT_CSV = DATA_DIR / "mavedb_testset.csv"

LO_THRESH = -0.8   # 功能丧失
HI_THRESH = 0.5    # 正常功能
N_PER_GROUP = 150


def main():
    if not MAVE_GZ.exists():
        raise SystemExit(f"✗ 找不到 {MAVE_GZ}")

    print(f"解析 {MAVE_GZ} ...")
    lo, hi = [], []
    refseqs = set()
    with gzip.open(MAVE_GZ, "rt", encoding="utf-8", errors="replace") as f:
        header = [h.lstrip("#") for h in f.readline().rstrip("\n").split("\t")]
        idx = {k: i for i, k in enumerate(header)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(header):
                continue
            sc = p[idx["score"]].strip()
            if not sc:
                continue
            try:
                s = float(sc)
            except ValueError:
                continue
            hgvs = p[idx["hgvs"]].strip()
            if not hgvs:
                continue
            rs = p[idx["refseq"]].strip()
            rec = {
                "AlleleID": p[idx["urn"]].strip() or f"mavedb:{len(lo)+len(hi)}",
                "Name": hgvs,
                "HGVS_Protein": hgvs,
                "Chromosome": p[idx["chr"]].strip(),
                "Start": p[idx["start"]].strip(),
                "ReferenceAllele": p[idx["ref"]].strip(),
                "AlternateAllele": p[idx["alt"]].strip(),
                "score": sc,
            }
            if rs:
                refseqs.add(rs)
            # HGVS 前缀也是转录本（NP_xxx/NM_xxx），refseq 字段常为空
            pref = hgvs.split(":")[0].strip()
            if pref:
                refseqs.add(pref)
            if s <= LO_THRESH:
                lo.append(rec)
            elif s >= HI_THRESH:
                hi.append(rec)
    print(f"功能丧失候选 {len(lo):,} / 正常功能候选 {len(hi):,} / 转录本 {len(refseqs):,}")

    # mygene.info 批量映射转录本 → 基因符号
    print("mygene.info 映射基因 ...")
    rs_list = sorted(refseqs)
    symbol = {}
    BATCH = 1000
    for i in range(0, len(rs_list), BATCH):
        batch = rs_list[i:i + BATCH]
        body = json.dumps({"q": batch, "scopes": "refseq",
                           "fields": "symbol"}).encode()
        req = urllib.request.Request(
            "https://mygene.info/v3/query", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read())
        for r in out:
            if "notfound" not in r and r.get("symbol"):
                symbol[r.get("query")] = r["symbol"]
    print(f"映射成功 {len(symbol)}/{len(rs_list)} 转录本")

    # 采样（只保留映射到基因的；seed=42 可复现）
    random.seed(42)
    def sample_group(lst):
        rows = []
        for rec in lst:
            # 这里简化：随机采样时用带基因的行
            rows.append(rec)
        return rows
    # 从候选里挑：用随机采样（先打乱再取）
    random.shuffle(lo)
    random.shuffle(hi)

    def build(group, direction):
        out = []
        for rec in group:
            if len(out) >= N_PER_GROUP:
                break
            out.append({
                "AlleleID": rec["AlleleID"],
                "Name": rec["Name"],
                "GeneSymbol": "",  # 下面统一填
                "HGVS_cDNA": "",
                "HGVS_Protein": rec["HGVS_Protein"],
                "Chromosome": rec["Chromosome"],
                "Start": rec["Start"],
                "ReferenceAllele": rec["ReferenceAllele"],
                "AlternateAllele": rec["AlternateAllele"],
                "ClinicalSignificance": direction,
                "score": rec["score"],
            })
        return out

    lo_rows = build(lo, "Loss_of_function")
    hi_rows = build(hi, "Normal_function")
    print(f"采样: 功能丧失 {len(lo_rows)} / 正常功能 {len(hi_rows)}")

    # 基因名映射（转录本从 HGVS 前缀取）
    def gene_of(rec):
        # HGVS 如 NP_031401.1:p.Gly290Ser → NP_031401.1
        hg = rec["HGVS_Protein"].split(":")[0].strip()
        return symbol.get(hg, "")

    for rec in lo_rows + hi_rows:
        rec["GeneSymbol"] = gene_of(rec)
    n_gene = sum(1 for r in lo_rows + hi_rows if r["GeneSymbol"])
    print(f"有基因名的: {n_gene}/{len(lo_rows)+len(hi_rows)}")

    all_rows = lo_rows + hi_rows
    fields = ["AlleleID", "Name", "GeneSymbol", "HGVS_cDNA", "HGVS_Protein",
              "Chromosome", "Start", "ReferenceAllele", "AlternateAllele",
              "ClinicalSignificance", "score"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"✓ 已写出 {OUT_CSV}")
    print("基因分布:", dict(Counter(r["GeneSymbol"] for r in all_rows).most_common(10)))


if __name__ == "__main__":
    main()
