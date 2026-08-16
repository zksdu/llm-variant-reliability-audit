# Introduction & Discussion (Draft) — English Manuscript Section

> Companion to Results_draft_EN.md and Abstract_Methods_draft_EN.md. Draft for internal review (2026-08-06).

---

## 1. Introduction (draft)

Clinical variant interpretation — classifying a germline variant as Pathogenic, Benign, or Uncertain per ACMG/AMP guidelines — is a bottleneck in genomic medicine: manual curation is expert-hours per variant and inconsistent across laboratories [1,2]. Large language models (LLMs) have been proposed as scalable interpreters [3–5], with recent work reporting near-expert agreement (e.g., AI-CURA reports expert-level consistency on curated variants [6]).

Two problems undermine these numbers. First, **training-data leakage**: LLM corpora contain public variant databases, so a model asked to classify a variant may reproduce a label it has memorized rather than reason about evidence. Published evaluations rarely control for this. Second, **vendor dependence**: results are typically reported for a single model family, leaving open whether any observed capability is a property of LLMs in general or of one training pipeline.

Existing variant-interpretation benchmarks do not resolve these concerns. VariantBench [7] evaluates ACMG classifications and criterion-level justifications but without leakage control; VarLitBench [8] anchors on ClinGen-curated functional evidence whose public availability makes memorization possible; AI-CURA [6] demonstrated clinical-grade performance on curated variants, again without controlling what the model saw during training. In the broader LLM literature, benchmark contamination is well documented [9,10], and temporally split evaluation has been proposed as a decontamination strategy [11]. No study to date has combined temporal blinding, multi-vendor coverage, and independent expert-panel validation at scale for variant classification.

Here we report the first such audit: 6 LLMs from 4 vendors, 30,000 variant-model evaluations on a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026), with an independent 900-variant expert-panel validation set and three triangulation sub-experiments (allele-frequency ablation, conflicting-interpretation variants, and functional-effect variants). We address three questions: (RQ1) How reliable is LLM variant classification under label-leakage control? (RQ2) Do multi-model consensus and model choice improve reliability? (RQ3) How does reliability depend on the evidence available to the model?

We find that label-leakage control reveals a large vendor gap (up to +22 pp), that the "when the model speaks it is right" property holds only for conservative models, that majority voting can reduce accuracy, and that model reliability tracks evidence availability — abstention is a calibrated, trustworthy signal rather than noise. We frame this work as a **reliability audit** rather than a generalization study: temporal blinding removes the label-memorization channel, but prior *evidence* (literature, submissions) may remain in training data; our goal is therefore to establish under which operational conditions an LLM's output can be trusted, not to claim de novo generalization from sequence alone.

## 4. Discussion (draft)

### 4.1 Principal findings

Under label-leakage control (temporal blinding of the gold-standard label), new-generation LLMs classify 62–72% of variants correctly (all-inclusive), rising to 86–93% on expert-panel-reviewed variants. When conservative models commit to a call, they are right 97.8–98.7% of the time, mislabeling only 1.3–2.5% of Benign variants as Pathogenic; reasoning models, by contrast, mislabel 22–28% of Benign variants as Pathogenic — the clinically dangerous direction. These are substantially lower than unblinded reports of expert-level consistency [6]; interpreted as a reliability audit, they define the *operational envelope* in which an LLM's output can be trusted, rather than a ceiling on generalization: label memorization is controlled, and remaining performance reflects the evidence the model actually reasons with.

### 4.2 Vendor choice matters more than ensemble size

The gap between the best and worst model (+22.4 pp all-inclusive; +25 pp expert-panel) exceeds the gain from any ensemble strategy we tested, and naive majority voting *reduced* accuracy below the best single model because conservative voters dominate ties. Two implications: (i) published "LLM accuracy" without model identity is meaningless; (ii) clinical deployments should select models on blinded benchmarks, not on ensemble size. The recommendation is model-specific — Kimi and Qwen excel on evidence-rich variants, while reasoning models (V4-pro, MiMo) commit more often but less reliably.

### 4.3 Abstention is calibrated behavior, not conservatism

Three independent experiments converge: models abstain more when evidence is missing (AF ablation: abstention falls 80%→33% once allele frequencies are provided), when experts disagree (conflicting variants: +22–39 pp abstention without being told), and when the task has no clinical evidence at all (MaveDB functional task: 73–93% abstention). LLMs behave like evidence-aware decision systems: they express uncertainty where evidence is weak and commit where it is strong. Clinically, this makes abstention a **trustworthy triage signal** — "the model said Uncertain, therefore review by a human" is a safe operating policy, and our data show the model is disproportionately Uncertain precisely when human review is needed.

### 4.3b Reproducibility as a reliability property

At temperature 0, chat-style models are exactly reproducible (100% over 50 re-runs), but the reasoning model V4-pro changed its binary call on 36% of re-run variants, including direct Benign↔Pathogenic flips. Average accuracy alone is therefore insufficient to audit a model for clinical use: a non-deterministic model cannot be deployed regardless of its mean performance, and reported single-run accuracies for such models are themselves noisy. The audit framing makes this explicit: determinism, like accuracy and abstention calibration, is a measured property we report per model rather than assume.

### 4.4 The information-deficit explanation of Benign underperformance

The most striking baseline result — Benign sensitivity of 9.6–43% — is largely explained by missing allele-frequency evidence. With AF provided, Benign sensitivity rises by up to +57.8 pp and all-inclusive accuracy roughly triples. ACMG rules BA1/BS1 (population frequency) are among the strongest Benign evidence; omitting them cripples the Benign side of the classification. Practical implication: any LLM-based variant interpretation pipeline must integrate population-frequency databases; performance numbers reported without AF are systematically pessimistic about Benign recall.

### 4.5 Relation to prior work

AI-CURA [6] demonstrated expert-consistency without leakage control; our label-blinded numbers (62–72%) suggest that a substantial part of unblinded performance may be label memorization. VariantBench [7] and VarLitBench [8] advance evaluation rigor — justifications and ClinGen-anchored evidence, respectively — but neither temporally blinds the gold standard nor spans vendors; we add both, plus independent expert-panel validation. Our conditional-accuracy framing (speak vs. abstain) is, to our knowledge, new to this literature and reconciles the "impressive when confident" and "unusable overall" observations in prior reports. Positioning: whereas AI-CURA asks "can LLMs classify variants?", we ask "under which auditable conditions can an LLM's classification be trusted?" — the audit framing keeps our claims within what temporal blinding can actually establish.

### 4.6 Limitations

(i) Vendor panel is Chinese-commercial; conclusions about LLMs generally require non-Chinese models (in progress). (ii) Temporal blinding approximates leakage control via LastEvaluated date; a variant's *evidence* (submissions, literature) may predate its label, so the model could still have seen evidence if not the final label. (iii) Binary P/B evaluation collapses ACMG's five classes and penalizes "Likely" mapping strategies. (iv) The MaveDB functional direction is a soft validation. (v) Single task (germline SNV/indel); splice/structural/de novo variants unaddressed. (vi) Cost audit (30 variants × 6 models, API-reported usage): reasoning models emit 13–21× more output tokens (chain-of-thought billed as completion), per-variant cost spans 41× (MiMo ¥0.041 vs. chat ¥0.001) and latency spans 29× (65.9 s vs. 2.3 s) — yet reasoning models buy neither accuracy, stability, nor safety (22–28% Benign→Pathogenic false positives).

### 4.7 Conclusion

Under label-leakage control, LLM variant interpretation passes reliability audit under three conditions: the model is chosen on blinded evidence (vendor gap up to +22 pp; majority voting can hurt), complete evidence is provided (AF mandatory; +58 pp Benign sensitivity), and abstention is deployed as a human-review trigger. We provide the first multi-vendor, temporally controlled, independently validated reliability audit, and recommend that (i) published accuracies report model identity, blinding status, and evidence conditions; (ii) clinical pilots adopt "Pathogenic calls auto-flag, Uncertain calls auto-escalate" operating policies; and (iii) future audits extend to non-Chinese vendors and additional task types.

---

## References

[1] Richards S, Aziz N, Bale S, et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genet Med. 2015;17(5):405–424. doi:10.1038/gim.2015.30
[2] Rehm HL, Berg JS, Brooks LD, et al. ClinGen — the Clinical Genome Resource. N Engl J Med. 2015;372(23):2235–2242. doi:10.1056/NEJMsr1409004
[3] Landrum MJ, Lee JM, Benson M, et al. ClinVar: improvements to integrating and interpreting data. Nucleic Acids Res. 2020;48(D1):D835–D844. doi:10.1093/nar/gkz972
[4] Karczewski KJ, Francioli LC, Tiao G, et al. The mutational constraint spectrum quantified from variation in 141,456 humans. Nature. 2020;581:434–443. doi:10.1038/s41586-020-2308-7
[5] Cheng J, Novati G, Pan M, et al. Accurate proteome-wide missense variant effect prediction with AlphaMissense. Science. 2023;381(6664):eadg7492. doi:10.1126/science.adg7492
[6] Hong Kong Genome Institute. AI-CURA, an automated LLM workflow for high-accuracy genetic variant classification. Sci Transl Med. 2026. doi:10.1126/scitranslmed.adz4172
[7] Basharat H, Plotkin S, Le C, Zhu K, Pink M, Alfaro I. VariantBench: a framework for evaluating LLMs on justifications for genetic variant interpretation. In: Proc. IJCNLP-AACL 2025 (SRW), Mumbai, India. ACL. https://aclanthology.org/2025.ijcnlp-srw.26/
[8] 【authors】. VarLitBench and VarLitAgent for benchmarking and agentic curation of variant-specific functional evidence. In: Proc. ICML 2026. arXiv:2604.00075
[9] Sainz O, Campos JA, García-Ferrero I, et al. NLP evaluation in trouble: on the need to measure LLM data contamination for each benchmark. In: Findings of EMNLP 2023. arXiv:2310.18018
[10] Bordt S, et al. How much can we forget about data contamination? OpenReview. https://openreview.net/forum?id=Pf0PaYS9KG
[11] Golchin S, Surdeanu M. Time travel in LLMs: tracing data contamination in large language models. In: Findings of EMNLP 2023. arXiv:2308.08493
[12] Esposito D, Weile J, Shrestha R, et al. MaveDB: an open-source platform to distribute and query data from multiplexed assays of variant effect. bioRxiv. https://www.mavedb.org
[13] Wu C, MacLeod I, Su AI. BioGPS and MyGene.info: organizing online, gene-centric information. Nucleic Acids Res. 2013;41(D1):D561–D565. doi:10.1093/nar/gks1186
[14] DeepSeek-AI. DeepSeek-V3 technical report. arXiv:2412.19437
[15] Moonshot AI. Kimi K2: open agentic intelligence. arXiv:2507.20534 (technical report)
[16] Qwen Team. Qwen3 technical report. arXiv:2505.09388
[17] Xiaomi. MiMo API documentation. https://mimo.mi.com (商业 API 模型，无公开技术报告，引用官方文档)
