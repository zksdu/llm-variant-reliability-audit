# -*- coding: utf-8 -*-
"""
build_jgg.py — 生成 JGG 投稿格式正文（manuscript_JGG.md）

转换内容（对照 JGG Guide for Authors）：
1. 引用 [n] → 作者-年份制（JGG 要求）
2. 删除 first/novel/new 类措辞；new-generation → current-generation
3. 图表精简为 6 个 display items：Fig.1-4 + Table 1-2（Table 3/4/5 → S1/S2/S3）
4. 章节顺序：Abstract → Introduction → Results → Discussion → Materials and methods
5. 交叉引用 §x.y 去编号化
6. 后置声明区：Ethics/Data/Code availability/CRediT/COI/Acknowledgments
7. References 转 JGG 作者-年份格式
8. 图注独立成节（JGG 要求 legends 排在 tables 后）

使用：python build_jgg.py
"""
import re
from pathlib import Path

DOCS = Path(__file__).parent.parent / "docs"

CITE = {
    "[1]": "(Richards et al., 2015)",
    "[2]": "(Rehm et al., 2015)",
    "[3]": "(Landrum et al., 2020)",
    "[4]": "(Karczewski et al., 2020)",
    "[5]": "(Cheng et al., 2023)",
    "[6]": "(AI-CURA, 2026)",
    "[7]": "(Basharat et al., 2025)",
    "[8]": "(Saadat and Fellay, 2026)",
    "[9]": "(Sainz et al., 2023)",
    "[10]": "(Bordt et al., 2024)",
    "[11]": "(Golchin and Surdeanu, 2023)",
    "[12]": "(Esposito et al., 2019)",
    "[13]": "(Wu et al., 2013)",
    "[14]": "(DeepSeek-AI, 2024)",
    "[15]": "(Moonshot AI, 2025)",
    "[16]": "(Qwen Team, 2025)",
    "[17]": "(Xiaomi, 2026)",
    "[1,2]": "(Richards et al., 2015; Rehm et al., 2015)",
    "[3\u20135]": "(Landrum et al., 2020; Karczewski et al., 2020; Cheng et al., 2023)",
    "[9,10]": "(Sainz et al., 2023; Bordt et al., 2024)",
}

PHRASE = [
    # first/novel 清除（JGG factual style）
    ("Here we report the first such audit:", "Here we report an audit that combines all three controls:"),
    ("We provide the first multi-vendor, temporally controlled reliability audit of this capability",
     "We provide a multi-vendor, temporally controlled reliability audit of this capability"),
    ("We provide the first multi-vendor, temporally controlled, independently validated reliability audit",
     "We provide a multi-vendor, temporally controlled, independently validated reliability audit"),
    ("is, to our knowledge, new to this literature and reconciles the",
     "reconciles the"),
    ("New-generation models", "Current-generation models"),
    ("New-generation LLMs", "Current-generation LLMs"),
    ("new-generation", "current-generation"),
    ("(Generation gap)", "(Generation gap)"),  # 保留（描述性）
]

XREF = [
    ("Materials and methods \u00a72.4", "Materials and methods"),
    ("(see Methods \u00a72.4)", "(see Materials and methods)"),
    ("Methods \u00a72.4", "Materials and methods"),
    ("(\u00a72.4 and Limitations)", "(see Materials and methods and Declarations)"),
    ("(\u00a73.2b)", "(see the surface-cue analysis below)"),
    ("(\u00a73.5b)", "(see the five-class analysis below)"),
    ("(\u00a73.8)", "(see the international extension below)"),
    ("(\u00a73.8b)", "(see the robustness check below)"),
    ("reported in \u00a73.8b", "reported below"),
    ("(\u00a73.2b)", "(see below)"),
    ("(see Discussion \u00a74)", "(see Discussion)"),
    ("(gitee mirror provided in Data Availability)", "(see Data availability)"),
    ("(see Discussion)", "(see Discussion)"),
    ("Table 2.", "Table S3."),
    ("Table 2 reports", "Table S3 reports"),
    ("Table 3.", "Table S1."),
    ("Table 5.", "Table S2."),
]

TBL_RENUM = [
    ("**Table S1. Re-run consistency", "**Table S1. Re-run consistency"),
    ("**Table S2. Per-variant token usage", "**Table S2. Per-variant token usage"),
    ("**Table S3. Nine-model comparison", "**Table S3. Nine-model comparison"),
]


def strip_embedded_figs(src: str) -> str:
    """去掉正文内嵌图片、图注和概念文本块（JGG 图注独立成节）。"""
    src = re.sub(r"!\[Figure \d\]\(figures/[^)]+\)\n+\*[^\n]*Figure[^\n]*\*\n+", "", src)
    # 概念图文本块：删整个段落（含围栏）
    src = re.sub(r"\*\*Figure 1 \(concept\).*?```\r?\n", "", src, flags=re.S)
    # 兜底：删除残留的 "Evidence available" 围栏块（Windows 换行兼容）
    src = re.sub(r"Evidence available.*?abstention\r?\n```\r?\n", "", src, flags=re.S)
    return src


def strip_section_numbers(src: str) -> str:
    """### 3.2b Xxx → ### Xxx（JGG 小节不编号）。"""
    return re.sub(r"^###\s+\d+\.\d+[b]?\s+", "### ", src, flags=re.M)


def apply_all(src: str) -> str:
    for k, v in CITE.items():
        src = src.replace(k, v)
    for a, b in PHRASE:
        src = src.replace(a, b)
    for a, b in XREF:
        src = src.replace(a, b)
    src = strip_embedded_figs(src)
    src = strip_section_numbers(src)
    return src


def main():
    # 读三个分节文件
    abstract_methods = (DOCS / "Abstract_Methods_draft_EN.md").read_text(encoding="utf-8")
    id_src = (DOCS / "Intro_Discussion_draft_EN.md").read_text(encoding="utf-8")
    results = (DOCS / "Results_draft_EN.md").read_text(encoding="utf-8")

    # 拆分
    m_idx = abstract_methods.find("## Methods (draft)")
    abstract = abstract_methods[:m_idx]
    abstract = re.sub(r"^# Abstract & Methods.*?---\n", "", abstract, flags=re.S, count=1)
    methods = abstract_methods[m_idx:]
    methods = re.sub(r"^## Methods \(draft\)", "## Materials and methods", methods)

    d_idx = id_src.find("## 4. Discussion (draft)")
    intro = id_src[:d_idx]
    intro = re.sub(r"^# Introduction & Discussion.*?---\n", "", intro, flags=re.S, count=1).lstrip("\n")
    intro = re.sub(r"^## 1\. Introduction \(draft\)", "## Introduction", intro)
    ref_idx = id_src.find("## References")
    disc = id_src[d_idx:ref_idx] if ref_idx > d_idx else id_src[d_idx:]
    disc = re.sub(r"^## 4\. Discussion \(draft\)", "## Discussion", disc)

    results = re.sub(r"^# Results \(Draft\).*?---\n", "", results, flags=re.S, count=1).lstrip("\n")
    results = re.sub(r"^## 3\. Results", "## Results", results)

    # 应用转换
    intro, results, disc, methods = map(apply_all, (intro, results, disc, methods))

    # 图引用注入（语义+顺序：Fig1 总性能 / Fig2 证据 / Fig3A 确定性 3B Likely坍缩 /
    # Fig4 良性归宿 / Fig5 行为仪表盘）
    NL = "\n"
    results = results.replace("### Headline accuracy: models that speak are almost always right",
                              "### Headline accuracy: models that speak are almost always right" + NL + NL + "(Fig. 1)", 1)
    results = results.replace("### Triangulation: evidence availability drives reliability",
                              "### Triangulation: evidence availability drives reliability" + NL + NL + "(Fig. 2)", 1)
    results = results.replace("### Five-class analysis",
                              "### Five-class analysis" + NL + NL + "(Fig. 3B)", 1)
    results = results.replace("### Output determinism",
                              "### Output determinism" + NL + NL + "(Fig. 3A)", 1)
    results = results.replace("### International extension",
                              "### International extension" + NL + NL + "(Fig. 4)", 1)
    results = results.replace("### Prompt-asymmetry robustness check",
                              "### Prompt-asymmetry robustness check" + NL + NL + "(Fig. 5)", 1)

    # 转换表 3/4/5 标签（保内容，标记为补充表）
    for a, b in TBL_RENUM:
        results = results.replace(a, b)

    # 去掉 appendix
    ap = results.find("## Appendix (internal)")
    if ap > 0:
        results = results[:ap]

    back = """
## Ethics statement

This study used only publicly available database records (ClinVar, ClinGen-derived
review statuses, and MaveDB). No human participants, patient material, or personal
data were involved; institutional review board approval was not required.

## Data availability

All source data are publicly available: ClinVar variant_summary and VCF
(https://ftp.ncbi.nlm.nih.gov/pub/clinvar/), MaveDB Ensembl-mapped release
(https://ftp.ensembl.org/pub/current_variation/MaveDB/), and mygene.info. The
temporally blinded test sets, gold standards, all 45,000 raw model outputs (4 parse-failure rows excluded from analysis), and
analysis scripts are available at https://github.com/zksdu/llm-variant-reliability-audit
(archived on Zenodo, DOI: 10.5281/zenodo.21964620).

## Code availability

Custom analysis code is available at https://github.com/zksdu/llm-variant-reliability-audit
(archived on Zenodo, DOI: 10.5281/zenodo.21964620). The pipeline uses the Python 3 standard library only;
sampling is byte-reproducible at seed 42.

## CRediT authorship contribution statement

**Bing Song:** Conceptualization, Investigation, Data curation, Validation,
Writing \u2013 original draft.
**Kai Zhang:** Methodology, Software, Formal analysis, Visualization,
Supervision, Writing \u2013 review & editing. All authors read and approved the
final manuscript.

## Conflict of interest

The authors declare that they have no conflict of interest.

## Acknowledgments

Not applicable.

## References

AI-CURA, 2026. AI-CURA, an automated LLM workflow for high-accuracy genetic variant classification. Sci. Transl. Med.  doi:10.1126/scitranslmed.adz4172

Basharat, H., Plotkin, S., Le, C., Zhu, K., Pink, M., Alfaro, I., 2025. VariantBench: a framework for evaluating LLMs on justifications for genetic variant interpretation. In: Proceedings of IJCNLP-AACL 2025 (SRW), Mumbai, India.

Bordt, S., et al., 2024. How much can we forget about data contamination? OpenReview. https://openreview.net/forum?id=Pf0PaYS9KG

Cheng, J., Novati, G., Pan, M., et al., 2023. Accurate proteome-wide missense variant effect prediction with AlphaMissense. Science 381, eadg7492.

DeepSeek-AI, 2024. DeepSeek-V3 technical report. arXiv:2412.19437.

Esposito, D., Weile, J., Shrestha, R., et al., 2019. MaveDB: an open-source platform to distribute and query data from multiplexed assays of variant effect. bioRxiv. 

Golchin, S., Surdeanu, M., 2023. Time travel in LLMs: tracing data contamination in large language models. In: Findings of EMNLP 2023.

Lin, Y.-C., et al., 2025. Benchmarking large language models GPT-4o, Llama 3.1, and Qwen 2.5 for cancer genetic variant classification. npj Precis. Oncol. 9, 165. doi:10.1038/s41669-025-00583-8

Karczewski, K.J., Francioli, L.C., Tiao, G., et al., 2020. The mutational constraint spectrum quantified from variation in 141,456 humans. Nature 581, 434\u2013443.

Landrum, M.J., Lee, J.M., Benson, M., et al., 2020. ClinVar: improvements to integrating and interpreting data. Nucleic Acids Res. 48, D835\u2013D844.

Moonshot AI, 2025. Kimi K2: open agentic intelligence. arXiv:2507.20534.

Qwen Team, 2025. Qwen3 technical report. arXiv:2505.09388.

Rehm, H.L., Berg, J.S., Brooks, L.D., et al., 2015. ClinGen \u2014 the Clinical Genome Resource. N. Engl. J. Med. 372, 2235\u20132242.

Richards, S., Aziz, N., Bale, S., et al., 2015. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genet. Med. 17, 405\u2013424.

Saadat, A., Fellay, J., 2026. Large language models for variant-centric functional evidence mining. arXiv:2604.00075.

Sainz, O., Campos, J.A., Garc\u00eda-Ferrero, I., et al., 2023. NLP evaluation in trouble: on the need to measure LLM data contamination for each benchmark. In: Findings of EMNLP 2023.

Wu, C., MacLeod, I., Su, A.I., 2013. BioGPS and MyGene.info: organizing online, gene-centric information. Nucleic Acids Res. 41, D561\u2013D565.

Xiaomi, 2026. MiMo API documentation. https://mimo.mi.com

## Tables



## Figure legends

**Fig. 1. Multi-model performance on the temporally blinded test set.**
A: Dual-metric accuracy for all nine models on the complete test set (n ~ 4,999 evaluable per model); all-inclusive (VUS counted as error) and conditional (committed calls only) accuracy with Wilson 95% CI error bars. International models shown with white fill and outline.
B: Benign-to-Pathogenic false-positive rates (log scale) with 95% CI; the 6-model consensus value is indicated.

**Fig. 2. Evidence availability governs reliability.**
A: Allele-frequency ablation on a Benign-rich subset (n = 400 \u00d7 3 models):
Benign sensitivity without vs. with population AF. B: The ablation on a
Pathogenic-enriched subset (n = 150 \u00d7 2). C: Abstention across evidence contexts:
with vs. without AF, main set vs. conflicting-interpretation variants, and the
no-evidence MaveDB task.

**Fig. 5. Behavioral dashboard of the nine models.**
Six audited dimensions per model (all-inclusive, conditional, expert-panel, abstention, Benign-to-Pathogenic FP, spoken rate), color-coded 0-100; the dashboard summarizes the audit and supports model selection.

**Fig. 4. Fate of gold-standard Benign variants across the nine models.**
For each model, the share of the 2,500 gold-standard Benign variants that is
correctly called Benign (blue), abstained as VUS (grey), or misclassified as
Pathogenic (magenta) — the clinically dangerous direction. Conservative and
aggressive camps separate sharply on the magenta segment.

**Fig. 3. Output determinism and the collapse of the "Likely" tier.**
A: Re-run agreement at temperature 0 (n = 50 per model, plus the international
extension). B: Output distribution for gold-standard Likely pathogenic and Likely
benign variants (Kimi, expert set): strength information polarizes to Pathogenic or
Benign; cross-ecosystem counts in text.

### Supplementary material

- **Table S1.** Re-run consistency (n = 50 \u00d7 3 models).
- **Table S2.** Nine-model comparison on the complete test set (n = 5,000 per model).
- **Table S3.** Expert-panel validation (n = 797 exclusive variants; 3 models).
- **Fig. S1\u2013S5.** Extended figures from the audit (optional, from docs/figures/).
"""

    title_block = """# Multi-vendor evaluation of large language models for ACMG/AMP variant classification with controlled data contamination

> JGG submission version. Keywords: variant classification; ACMG/AMP; large language models; data leakage; ClinVar; reliability audit; temporal blinding.

---

## Abstract

**Background.** Large language models (LLMs) are increasingly proposed for ACMG/AMP variant classification, but training corpora include ClinVar and ClinGen, so reported accuracy may reflect label memorization rather than reasoning.

**Objective.** To audit LLM variant-classification reliability under controlled label leakage, across vendors and evidence conditions.

**Methods.** On a temporally blinded test set of 5,000 ClinVar variants (all assessed after January 2026), we evaluated six Chinese LLMs (30,000 evaluations) and three international flagships at full scale (15,000 additional evaluations), with independent validation on 900 expert-panel variants.

**Results.** Current-generation models achieved 61.8–71.6% all-inclusive accuracy under temporal blinding, rising to 86–93% on expert-panel variants. Conservative models reached 97.8–98.7% conditional accuracy with FP rates under 4.7%, while reasoning models reached 81.2–85.2% with FP rates up to 28.4%. Providing allele-frequency evidence raised Benign sensitivity by up to 57.8 pp. Gemini 3 Flash led internationally (76.5%); Claude paired 97.0% conditional accuracy with 3.9% FP.

**Conclusions.** LLM variant interpretation is reliable only under blinded model selection, complete evidence (allele frequency mandatory), and abstention-as-human-review policies.

"""

    out = title_block + intro.strip() + "\n\n" + results.strip() + "\n\n" + \
        disc.strip() + "\n\n" + methods.strip() + "\n" + back
    out_path = DOCS / "manuscript_JGG.md"
    out_path.write_text(out, encoding="utf-8")

    # 校验
    n_words = len(re.sub(r"[#|>\-*`]", " ", intro + results + disc).split())
    leftovers = re.findall(r"\[\d+[,\u2013]?\d*\]", out)
    novelty = [w for w in ["the first ", "novel", "first such"] if w in out]
    print(f"\u2713 manuscript_JGG.md \u751f\u6210: {len(out.splitlines())} \u884c")
    print(f"  \u6b63\u6587\u8bcd\u6570\uff08Intro+Results+Discussion\uff0c\u4e0d\u542b Methods/Refs\uff09\u2248 {n_words:,}\uff08\u9650\u5236 <10,000\uff09")
    print(f"  \u6b8b\u7559\u7f16\u53f7\u5f15\u7528: {leftovers if leftovers else '\u65e0'}")
    print(f"  \u65b0\u9896\u6027\u63aa\u8f9e\u6b8b\u7559: {novelty if novelty else '\u65e0'}")
    figs = re.findall(r"\(Fig\. \d\)", out)
    print(f"  \u56fe\u5f15\u7528: {sorted(set(figs))}")


if __name__ == "__main__":
    main()
