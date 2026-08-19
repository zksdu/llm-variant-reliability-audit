# Submission Package — Title Page, Declarations, Cover Letter

> 期刊决策（2026-08-16 核实）：**已选定 JGG**（Journal of Genetics and Genomics）
> - 中科院 1 区、IF 7.1、收原创研究（Research Article）
> - 费用：订阅模式**免版面费**；⚠️ **印刷版彩图费 $1,000 首图 + $300/后续图**——校样阶段可选"仅在线彩色"规避（建议届时询问编辑部）
> - OA 可选 $3,640（不选即免费）
> - ~~BIB~~ 已排除（只收综述）；GPB 备选（强制 OA $3,500）
>
> ⚠️ 需用户填写：【作者名单】【单位】【通讯作者】【基金号】
> ⚠️ JGG 要求代码放 **DOI-minting 仓库**（GitHub/GitLab/Zenodo）——gitee 不满足，
>    需将代码镜像到 GitHub（或直接上传 Zenodo 档案获 DOI）。需外网，用户侧操作。

---

## Title Page

**Title:** When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification

**Running title (≤50 chars):** Multi-vendor LLM Variant Classification

**Authors:** Bing Song¹, Kai Zhang²,*

**Affiliations:**
¹ The Third Affiliated Hospital of Guangzhou Medical University, Guangzhou, Guangdong, China
² Guangdong Communication Polytechnic, Guangzhou, Guangdong, China

**Corresponding author:** Kai Zhang
E-mail: zhangkai@gdcp.edu.cn
（第一作者：Bing Song，__FIRST_AUTHOR_EMAIL__）

**Keywords:** variant classification; ACMG/AMP; large language models; data leakage; ClinVar; controlled data contamination; temporal blinding

---

## Abstract (182 words — meets GPB <200 & JGG limits)

**Background.** Large language models (LLMs) are increasingly proposed for ACMG/AMP variant classification, but training corpora include ClinVar and ClinGen, so reported accuracy may reflect label memorization rather than reasoning.

**Objective.** To audit LLM variant-classification reliability under controlled label leakage, across vendors and evidence conditions.

**Methods.** On a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026), we evaluated six Chinese LLMs (30,000 evaluations) and three international flagships (Gemini 3 Flash, GPT-5.6-terra, Claude Sonnet 5) at full scale (15,000 additional evaluations), with independent validation on 900 expert-panel variants and ablations for allele-frequency (AF) evidence, conflicting classifications, and MaveDB functional variants.

**Results.** New-generation models achieved 61.8–71.6% all-inclusive accuracy and 86–93% on expert-panel variants. Conditional accuracy when committing was 97.8–98.7% for conservative models versus 81.2–85.2% for reasoning models, whose Benign→Pathogenic false-positive rates reached 22–28%. Providing AF raised Benign sensitivity by up to 57.8 pp. Gemini led internationally (80.2%); Claude paired 97.4% conditional accuracy with 3.6% false positives. Majority voting underperformed the best single model.

**Conclusions.** LLM variant interpretation is reliable only under blinded model selection, complete evidence (AF mandatory), and abstention-as-human-review policies.

---

## Declarations

**Ethics approval and consent to participate.**
Not applicable. This study uses only publicly available database records (ClinVar, ClinGen-derived review statuses, MaveDB); no human participants, patient material, or personal data were involved.

**Consent for publication.** Not applicable.

**Availability of data and materials.**
All data are publicly available: ClinVar variant_summary and VCF (ftp.ncbi.nlm.nih.gov/pub/clinvar/), MaveDB Ensembl-mapped release (ftp.ensembl.org/pub/current_variation/MaveDB/), and mygene.info. The temporally blinded test sets, gold standards, all 31,500 raw model outputs, analysis scripts (Python 3 standard library, seed 42, byte-reproducible sampling), and figures are available at 【gitee 仓库公开地址】.

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Authors' contributions.** Bing Song: Conceptualization, Investigation, Data curation, Validation, Writing – original draft. Kai Zhang: Methodology, Software, Formal analysis, Visualization, Supervision, Writing – review & editing. All authors read and approved the final manuscript.

**Competing interests.** The authors declare that they have no competing interests.

**Acknowledgements.** Not applicable.

---

## Cover Letter (JGG)

Dear Editor-in-Chief,

We are pleased to submit our manuscript, "When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification," for consideration as a Research Article in the Journal of Genetics and Genomics.

LLMs are increasingly proposed for clinical variant interpretation, with recent reports of near-expert agreement. However, training corpora include public variant databases, so these scores may partly reflect memorization of gold-standard labels. We provide the first large-scale audit that combines three controls absent from prior work: temporal label blinding (5,000 ClinVar variants assessed strictly after every model's training cutoff), multi-vendor coverage (nine models across seven vendors, including Gemini, GPT, and Claude), and independent ClinGen expert-panel validation.

Our central findings are actionable: model choice dominates ensemble strategies (majority voting can reduce accuracy below the best single model); error direction differs sharply by model style (reasoning models mislabel 22–28% of Benign variants as Pathogenic); evidence completeness governs reliability (allele-frequency provision raises Benign sensitivity by up to 57.8 pp); and abstention behaves as a calibrated, trustworthy triage signal for human review. All results, scripts, and sampling are fully reproducible from public data.

This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission and declare no competing interests.

Thank you for your consideration.

Sincerely,
Kai Zhang (corresponding author), on behalf of all authors
Guangdong Communication Polytechnic, Guangzhou, Guangdong, China
E-mail: zhangkai@gdcp.edu.cn


---

## JGG 投稿合规清单（已完成项 ✅ / 待办 ⬜）

| 项目 | 状态 |
|---|---|
| 标题 ≤150 字符、冒号后小写 | ✅（manuscript_JGG.md 首行）|
| 摘要 <200 词（无引用）| ✅ 182 词 |
| 关键词 5-7 个 | ✅ 7 个 |
| 正文 <10,000 词（不含 Methods/Refs）| ✅ ≈4,542 词 |
| display items ≤6（主文）| ✅ 4 图 + 2 表（原 Table 3/4/5 → S1/S2/S3）|
| 引用作者-年份制 | ✅（[n] 全部转换）|
| 无 first/novel/new 措辞 | ✅ |
| 图：Arial、色盲安全、300dpi TIFF+PDF、A/B/C 标注 | ✅ figures_jgg/ |
| CRediT 声明 | ⬜ 待填作者 |
| 代码 DOI 仓库（GitHub/Zenodo 镜像）| ⬜ 用户侧（需外网）|
| 作者/单位/基金 | ⬜ 用户填写 |
| 投稿系统 | ScholarOne/Editorial Manager（投稿时在线注册）|

## JGG 投稿文件清单

1. `docs/manuscript_JGG.md` → 转入 Word/LaTeX 排版后上传（含正文+声明+References+图注）
2. `docs/submission_package.md` 的标题页 + 摘要 + 投稿信
3. `docs/figures_jgg/fig1-4_JGG.pdf/.tiff`（4 张主图）
4. 补充材料：Table S1-S3（正文 manuscript_JGG.md 内）+ 可选 Fig S1-S5（docs/figures/）
5. Cover letter（本文件内）
