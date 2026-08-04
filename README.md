# Bioinformatics_Paper_Project — 生信论文研究目录

> 创建日期：2026-08-04
> 目的：独立于软件工程论文（`../SCI_Paper_Project`）的生信方向 SCI 论文研究空间

## 目录结构

```
Bioinformatics_Paper_Project/
├── README.md          ← 本文件（项目说明）
├── docs/              ← 论文大纲、期刊调研、写作规划
├── data/              ← 生信数据集（公开数据，注意体积与版权）
├── scripts/           ← 分析脚本（可复现）
├── results/           ← 分析结果
└── figures/           ← 论文图表
```

## 目标约束（与用户确认）

- 目标期刊：**中科院 1 区**（用户明确要求）
- SCIE 收录必须（职称有效）
- 费用/录用率：1 区无"容易中"选项，需接受高门槛或付费（见 docs/生信期刊调研.md）

## 生信 1 区期刊候选（2026-08 核实）

| 期刊 | 分区(2026) | IF | 费用 | 难度 | 备注 |
|------|-----------|-----|------|------|------|
| Genome Research | 1 区 Top | 6.3 | 免费(hybrid) | 极难 | 年发文~150 |
| Nucleic Acids Research | 1 区 Top | 15.0 | $4,192 | 极难 | 完全不免费 |
| **GPB（国产）** | **1 区** | 7.9 | $3,650 | 难(16%) | 国内友好、审稿快(18天) |

⚠️ **避坑**：Computers in Biology and Medicine（CIBM）已被 WoS 除名（2025-11），勿投。

## 待办（下一步）

- [ ] 确定生信研究方向（单细胞 / 基因组 / 转录组 / 多组学整合 / 疾病关联等）
- [ ] 调研可用的公开数据集（TCGA / GEO / 1000 Genomes 等）
- [ ] 明确是否复用 DeepSeek API（生信分析中的 LLM 应用？）或纯生信方法
- [ ] 撰写论文大纲

## 与软件工程论文的关系

- 两篇论文相互独立，各有目录
- 生信论文若涉及 LLM 应用（如基因组注释、变异解读、文献挖掘），可复用 `../SCI_Paper_Project` 的 DeepSeek 调用基建（.env / call_llm / RAG）
- 投稿节奏可并行推进

## 数据下载规则（重要）

> **用户明确要求**：凡是需要下载数据，直接给用户下载地址，用户用迅雷一次性完整下载。
> 不要用脚本/分段/curl 等方式下载大数据文件（慢且易损坏）。

**ClinVar 数据**（已由用户下载完成，2026-08-04）：
- 地址：https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
- 文件：`data/variant_summary.txt.gz`（441,573,728 字节，gzip 完整 ✓）
