# Submission Package — Title Page, Declarations, Cover Letter

> 期刊决策（2026-08-16 核实）：
> - **首选 JGG**（Journal of Genetics and Genomics）：中科院 1 区、IF 7.1、**订阅模式免费发表**（hybrid，OA 可选 $3,640）、收原创研究
> - 备选 GPB：中科院 1 区、强制 OA **$3,500**、章节顺序特殊（Results 在 Methods 前）
> - ~~BIB~~：**只收综述，不收纯原创研究**（官方页明示）——已排除
>
> ⚠️ 需用户填写：【作者名单】【单位】【通讯作者】【基金号】

---

## Title Page

**Title:** When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification

**Running title (≤50 chars):** Reliability Audit of LLM Variant Classification

**Authors:** 【请填写：First A. Author¹, Second B. Author², ...】

**Affiliations:**
1. 【单位全称，城市，邮编，国家】
2. 【...】

**Corresponding author:** 【姓名】
E-mail: 【邮箱】
Tel: 【电话（可选）】

**Keywords:** variant classification; ACMG/AMP; large language models; data leakage; ClinVar; reliability audit; temporal blinding

---

## Abstract (182 words — meets GPB <200 & JGG limits)

**Background.** Large language models (LLMs) are increasingly proposed for ACMG/AMP variant classification, but training corpora include ClinVar and ClinGen, so reported accuracy may reflect label memorization rather than reasoning.

**Objective.** To audit LLM variant-classification reliability under controlled label leakage, across vendors and evidence conditions.

**Methods.** On a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026), we evaluated six Chinese LLMs (30,000 evaluations) and three international flagships (Gemini 3 Flash, GPT-5.6-terra, Claude Sonnet 5) on an identical 500-variant subset, with independent validation on 900 expert-panel variants and ablations for allele-frequency (AF) evidence, conflicting classifications, and MaveDB functional variants.

**Results.** New-generation models achieved 61.8–71.6% all-inclusive accuracy and 86–93% on expert-panel variants. Conditional accuracy when committing was 97.8–98.7% for conservative models versus 81.2–85.2% for reasoning models, whose Benign→Pathogenic false-positive rates reached 22–28%. Providing AF raised Benign sensitivity by up to 57.8 pp. Gemini led internationally (80.2%); Claude paired 97.4% conditional accuracy with 3.6% false positives. Majority voting underperformed the best single model.

**Conclusions.** LLM variant interpretation is reliable only under blinded model selection, complete evidence (AF mandatory), and abstention-as-human-review policies.

---

## Declarations

**Ethics approval and consent to participate.**
Not applicable. This study uses only publicly available database records (ClinVar, ClinGen-derived review statuses, MaveDB); no human participants, patient material, or personal data were involved.

**Consent for publication.** Not applicable.

**Availability of data and materials.**
All data are publicly available: ClinVar variant_summary and VCF (ftp.ncbi.nlm.nih.gov/pub/clinvar/), MaveDB Ensembl-mapped release (ftp.ensembl.org/pub/current_variation/MaveDB/), and mygene.info. The temporally blinded test sets, gold standards, all 31,500 raw model outputs, analysis scripts (Python 3 standard library, seed 42, byte-reproducible sampling), and figures are available at 【gitee 仓库公开地址】.

**Funding.** 【请填写：基金名 + 编号；若无写 "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."】

**Authors' contributions.** 【请填写，例如：】Conceptualization: X.X.; Methodology: X.X. and X.X.; Software and experiments: X.X.; Formal analysis: X.X.; Writing—original draft: X.X.; Writing—review and editing: all authors. All authors read and approved the final manuscript.

**Competing interests.** The authors declare that they have no competing interests.

**Acknowledgements.** 【可选：感谢计算资源/资助方等】

---

## Cover Letter (JGG)

Dear Editor-in-Chief,

We are pleased to submit our manuscript, "When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification," for consideration as a Research Article in the Journal of Genetics and Genomics.

LLMs are increasingly proposed for clinical variant interpretation, with recent reports of near-expert agreement. However, training corpora include public variant databases, so these scores may partly reflect memorization of gold-standard labels. We provide the first large-scale audit that combines three controls absent from prior work: temporal label blinding (5,000 ClinVar variants assessed strictly after every model's training cutoff), multi-vendor coverage (nine models across seven vendors, including Gemini, GPT, and Claude), and independent ClinGen expert-panel validation.

Our central findings are actionable: model choice dominates ensemble strategies (majority voting can reduce accuracy below the best single model); error direction differs sharply by model style (reasoning models mislabel 22–28% of Benign variants as Pathogenic); evidence completeness governs reliability (allele-frequency provision raises Benign sensitivity by up to 57.8 pp); and abstention behaves as a calibrated, trustworthy triage signal for human review. All results, scripts, and sampling are fully reproducible from public data.

This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission and declare no competing interests.

Thank you for your consideration.

Sincerely,
【通讯作者姓名】
【单位】
【联系方式】
