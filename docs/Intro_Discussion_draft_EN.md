# Introduction & Discussion (Draft) — English Manuscript Section

> Companion to Results_draft_EN.md and Abstract_Methods_draft_EN.md. Draft for internal review (2026-08-06).

---

## 1. Introduction (draft)

Clinical variant interpretation — classifying a germline variant as Pathogenic, Benign, or Uncertain per ACMG/AMP guidelines — is a bottleneck in genomic medicine: manual curation is expert-hours per variant and inconsistent across laboratories [1]. Large language models (LLMs) have been proposed as scalable interpreters [2,3], with early work reporting near-expert agreement (e.g., AI-CURA reports ~96% consistency with expert panels [4]).

Two problems undermine these numbers. First, **training-data leakage**: LLM corpora contain public variant databases, so a model asked to classify a variant may reproduce a label it has memorized rather than reason about evidence. Published evaluations rarely control for this. Second, **vendor dependence**: results are typically reported for a single model family, leaving open whether any observed capability is a property of LLMs in general or of one training pipeline.

Recent work has begun to address the first problem: ClawBench [5] proposed temporal blinding — evaluating only variants whose labels postdate the model's training cutoff — but did not scale to multiple vendors. AI-CURA [4] demonstrated clinical-grade performance but without leakage control. No study to date has combined strict temporal blinding, multi-vendor coverage, and independent expert-panel validation at scale.

Here we report the first such evaluation: 6 LLMs from 4 vendors, 30,000 variant-model evaluations on a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026), with an independent 900-variant expert-panel validation set and three triangulation sub-experiments (allele-frequency ablation, conflicting-interpretation variants, and functional-effect variants). We address three questions: (RQ1) How reliable is LLM variant classification under leakage control? (RQ2) Do multi-model consensus and model choice improve reliability? (RQ3) How does reliability depend on the evidence available to the model?

We find that leakage control reveals a large vendor gap (up to +22 pp), that the "when the model speaks it is right" property holds only for conservative models, that majority voting can reduce accuracy, and that model reliability tracks evidence availability — abstention is a calibrated, trustworthy signal rather than noise.

## 5. Discussion (draft)

### 5.1 Principal findings

Under strict temporal blinding, new-generation LLMs classify 62–72% of variants correctly (all-inclusive), rising to 86–93% on expert-panel-reviewed variants. When conservative models commit to a call, they are right 97.8–98.7% of the time with a false-positive rate below 0.6%. These are substantially lower than unblinded reports (~96% [4]) but reflect true generalization rather than memorization.

### 5.2 Vendor choice matters more than ensemble size

The gap between the best and worst model (+22.4 pp all-inclusive; +25 pp expert-panel) exceeds the gain from any ensemble strategy we tested, and naive majority voting *reduced* accuracy below the best single model because conservative voters dominate ties. Two implications: (i) published "LLM accuracy" without model identity is meaningless; (ii) clinical deployments should select models on blinded benchmarks, not on ensemble size. The recommendation is model-specific — Kimi and Qwen excel on evidence-rich variants, while reasoning models (V4-pro, MiMo) commit more often but less reliably.

### 5.3 Abstention is calibrated behavior, not conservatism

Three independent experiments converge: models abstain more when evidence is missing (AF ablation: abstention falls 80%→33% once allele frequencies are provided), when experts disagree (conflicting variants: +22–39 pp abstention without being told), and when the task has no clinical evidence at all (MaveDB functional task: 73–93% abstention). LLMs behave like evidence-aware decision systems: they express uncertainty where evidence is weak and commit where it is strong. Clinically, this makes abstention a **trustworthy triage signal** — "the model said Uncertain, therefore review by a human" is a safe operating policy, and our data show the model is disproportionately Uncertain precisely when human review is needed.

### 5.4 The information-deficit explanation of Benign underperformance

The most striking baseline result — Benign sensitivity of 9.6–43% — is largely explained by missing allele-frequency evidence. With AF provided, Benign sensitivity rises by up to +57.8 pp and all-inclusive accuracy roughly triples. ACMG rules BA1/BS1 (population frequency) are among the strongest Benign evidence; omitting them cripples the Benign side of the classification. Practical implication: any LLM-based variant interpretation pipeline must integrate population-frequency databases; performance numbers reported without AF are systematically pessimistic about Benign recall.

### 5.5 Relation to prior work

AI-CURA [4] demonstrated expert-consistency without leakage control; our temporally blinded numbers (62–72%) suggest a substantial part of unblinded performance may be memorization. ClawBench [5] introduced temporal blinding but reported single-family results; we extend to four vendors and add independent gold standards. Our conditional-accuracy framing (speak vs. abstain) is, to our knowledge, new to this literature and reconciles the "impressive when confident" and "unusable overall" observations in prior reports.

### 5.6 Limitations

(i) Vendor panel is Chinese-commercial; conclusions about LLMs generally require non-Chinese models (in progress). (ii) Temporal blinding approximates leakage control via LastEvaluated date; a variant's *evidence* (submissions, literature) may predate its label, so the model could still have seen evidence if not the final label. (iii) Binary P/B evaluation collapses ACMG's five classes and penalizes "Likely" mapping strategies. (iv) The MaveDB functional direction is a soft validation. (v) Single task (germline SNV/indel); splice/structural/de novo variants unaddressed. (vi) Cost: Kimi-K2.6 (median 6 s/call) was ~7× faster than reasoning models (41–45 s); per-variant cost varies ~10× across the panel — cost-conscious deployments should favor fast models when accuracy differences are modest.

### 5.7 Conclusion

Under leakage control, LLM variant interpretation is a qualified yes: reliable when the model is chosen on blinded evidence (vendor gap +22 pp), given complete evidence (AF mandatory; +58 pp Benign sensitivity), and deployed with abstention as a human-review trigger. We provide the first multi-vendor, temporally controlled, independently validated benchmark, and recommend that (i) published accuracies report model identity, blinding status, and evidence conditions; (ii) clinical pilots adopt "Pathogenic calls auto-flag, Uncertain calls auto-escalate" operating policies; and (iii) future evaluations extend to non-Chinese vendors and additional task types.

---

## References (placeholder)

[1] ACMG/AMP 2015 guidelines (Richards et al., Genet Med 2015).
[2] LLM variant interpretation surveys (2025–2026).
[3] ClinVar-BERT (Genome Medicine 2026).
[4] AI-CURA (Science Translational Medicine 2026).
[5] ClawBench (bioRxiv 2026).
