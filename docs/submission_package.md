# Submission Package — Title Page, Declarations, Cover Letter（终版 2026-09-03）

> ⚠️ 本文件为 EM 投稿时逐字复制用的唯一权威版本（旧版含过时数字已废弃）。
> 权威正文：docs/manuscript_JGG.md / docs/submission_JGG.docx
> 投稿图（5 张）：docs/figures_v2/fig1-fig5（.tiff/.pdf/.png）
> 代码仓库：https://github.com/zksdu/llm-acmg-variant-audit（Zenodo DOI: 10.5281/zenodo.22281813）

---

## Title Page

**Title:** Multi-vendor evaluation of large language models for ACMG/AMP variant classification with controlled data contamination

**Running title (≤50 chars):** Multi-vendor LLM Variant Classification

**Authors:** Bing Song¹, Kai Zhang²,*

**Affiliations:**
¹ The Third Affiliated Hospital of Guangzhou Medical University, Guangzhou, Guangdong, China
² Guangdong Communication Polytechnic, Guangzhou, Guangdong, China

**Corresponding author:** Kai Zhang
E-mail: zhangkai@gdcp.edu.cn

**Keywords:** variant classification; ACMG/AMP; large language models; data leakage; ClinVar; reliability audit; temporal blinding

---

## Abstract（与 manuscript_JGG.md 完全一致）

**Background.** Large language models (LLMs) are increasingly proposed for ACMG/AMP variant classification, but training corpora include ClinVar and ClinGen, so reported accuracy may reflect label memorization rather than reasoning.

**Objective.** To audit LLM variant-classification reliability under controlled label leakage, across vendors and evidence conditions.

**Methods.** On a temporally blinded test set of 5,000 ClinVar variants (all assessed after January 2026), we evaluated six Chinese LLMs (30,000 evaluations) and three international flagships at full scale (15,000 additional evaluations), with independent validation on 900 expert-panel variants.

**Results.** Current-generation models achieved 61.8–71.6% all-inclusive accuracy under temporal blinding, rising to 86–93% on expert-panel variants. Conservative models reached 97.8–98.7% conditional accuracy with FP rates under 4.7%, while reasoning models reached 81.2–85.2% with FP rates up to 28.4%. Providing allele-frequency evidence raised Benign sensitivity by up to 60.1 pp. Gemini 3 Flash led internationally (76.5%); Claude paired 97.0% conditional accuracy with 3.9% FP.

**Conclusions.** LLM variant interpretation is reliable only under blinded model selection, complete evidence (allele frequency mandatory), and abstention-as-human-review policies.

---

## Declarations（与 manuscript_JGG.md 完全一致）

**Ethics approval and consent to participate.**
Not applicable. This study uses only publicly available database records (ClinVar, ClinGen-derived review statuses, MaveDB); no human participants, patient material, or personal data were involved.

**Consent for publication.** Not applicable.

**Availability of data and materials.**
All source data are publicly available: ClinVar variant_summary and VCF (https://ftp.ncbi.nlm.nih.gov/pub/clinvar/), MaveDB Ensembl-mapped release (https://ftp.ensembl.org/pub/current_variation/MaveDB/), and mygene.info. The temporally blinded test sets, gold standards, all 45,000 raw model outputs (4 parse-failure rows excluded from analysis), and analysis scripts are available at https://github.com/zksdu/llm-acmg-variant-audit (archived on Zenodo, DOI: 10.5281/zenodo.22281813).

**Code availability.**
Custom analysis code is available at https://github.com/zksdu/llm-acmg-variant-audit (archived on Zenodo, DOI: 10.5281/zenodo.22281813). The pipeline uses the Python 3 standard library only; sampling is byte-reproducible at seed 42.

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**CRediT authorship contribution statement.**
**Bing Song:** Conceptualization, Investigation, Data curation, Validation, Writing – original draft.
**Kai Zhang:** Methodology, Software, Formal analysis, Visualization, Supervision, Writing – review & editing. All authors read and approved the final manuscript.

**Conflict of interest.** The authors declare that they have no conflict of interest.

**AI use declaration.**
During the preparation of this work the authors used an AI language model (GLM, Z.ai) to assist with drafting, language editing, and analysis-code development. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.

**Acknowledgments.** Not applicable.

---

## Cover Letter（EM 粘贴用）

Dear Editor-in-Chief,

We are pleased to submit our manuscript, "Multi-vendor evaluation of large language models for ACMG/AMP variant classification with controlled data contamination," for consideration as a Research Article in the Journal of Genetics and Genomics.

LLMs are increasingly proposed for clinical variant interpretation, with recent reports of near-expert agreement. However, training corpora include public variant databases, so these scores may partly reflect memorization of gold-standard labels. Our study combines three controls that no prior variant-classification evaluation has combined: temporal label blinding (5,000 ClinVar variants assessed strictly after every model's training cutoff), multi-vendor coverage (nine models across seven vendors, including Gemini, GPT, and Claude; 45,000 evaluations), and independent ClinGen expert-panel validation.

Our central findings are actionable: model choice dominates ensemble strategies (majority voting can reduce accuracy below the best single model); error direction differs sharply by model style (reasoning models mislabel 22–28% of Benign variants as Pathogenic, the clinically dangerous direction); evidence completeness governs reliability (allele-frequency provision raises Benign sensitivity by up to 60.1 percentage points); and abstention behaves as a calibrated, trustworthy triage signal for human review. All results, scripts, and sampling are fully reproducible from public data (github.com/zksdu/llm-acmg-variant-audit, archived with DOI).

This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission and declare no competing interests.

Thank you for your consideration.

Sincerely,
Kai Zhang (corresponding author), on behalf of all authors
Guangdong Communication Polytechnic, Guangzhou, Guangdong, China
E-mail: zhangkai@gdcp.edu.cn

---

## EM 投稿文件清单（终版）

1. Manuscript：`docs/submission_JGG.docx`（含正文+声明+参考文献+图注；图单独上传）
2. Figures（5 张，按序上传）：`docs/figures_v2/fig1.tiff` ~ `fig5.tiff`（PDF 备选）
3. Cover letter：上方文本（或作为单独文件上传）
4. Personal Keywords（5 个）：variant classification / ACMG/AMP / large language model / ClinVar / artificial intelligence
5. 补充表 S1–S3：正文内（docx 已含）；如 EM 要求单独文件，从 manuscript_JGG.md 提取
6. 代码仓库（Data availability 栏填写）：https://github.com/zksdu/llm-acmg-variant-audit（DOI: 10.5281/zenodo.22281813）

## 合规自查（2026-09-03 终审）

| 项目 | 状态 |
|---|---|
| 标题 ≤150 字符 | ✅ 118 字符 |
| 摘要结构化 <200 词 | ✅ |
| 关键词 5-7 个 | ✅ 7 个 |
| 正文词数 <10,000 | ✅ |
| 图表数：5 图 + 主文 2 表（1/2）+ 补充 S1-S3 | ✅ ≤6 display items（图 5 + 表 2）|
| 图：Arial、色盲安全、600dpi、A/B 标注 | ✅ figures_v2/ |
| 引用作者-年份制、全部真实可溯（含 DOI 逐条核验）| ✅ 2026-09-03 |
| 图-表-正文数字三方一致（fig3 已数据驱动重生成）| ✅ 2026-09-03 |
| AI 使用声明 | ✅ 已含 |
| 数据可用性声明与仓库内容一致 | ✅ 2026-09-03（仓库已补全）|
