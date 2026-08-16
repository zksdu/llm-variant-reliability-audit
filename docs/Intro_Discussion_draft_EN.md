# Introduction & Discussion (Draft) — English Manuscript Section

> Companion to Results_draft_EN.md and Abstract_Methods_draft_EN.md. Draft for internal review (2026-08-06).

---

## 1. Introduction (draft)

Clinical variant interpretation — classifying a germline variant as Pathogenic, Benign, or Uncertain per ACMG/AMP guidelines — is a bottleneck in genomic medicine: manual curation is expert-hours per variant and inconsistent across laboratories [1]. Large language models (LLMs) have been proposed as scalable interpreters [2,3], with early work reporting near-expert agreement (e.g., AI-CURA reports ~96% consistency with expert panels [4]).

Two problems undermine these numbers. First, **training-data leakage**: LLM corpora contain public variant databases, so a model asked to classify a variant may reproduce a label it has memorized rather than reason about evidence. Published evaluations rarely control for this. Second, **vendor dependence**: results are typically reported for a single model family, leaving open whether any observed capability is a property of LLMs in general or of one training pipeline.

Recent work has begun to address the first problem: ClawBench [5] proposed temporal blinding — evaluating only variants whose labels postdate the model's training cutoff — but did not scale to multiple vendors. AI-CURA [4] demonstrated clinical-grade performance but without leakage control. No study to date has combined strict temporal blinding, multi-vendor coverage, and independent expert-panel validation at scale.

Here we report the first such audit: 6 LLMs from 4 vendors, 30,000 variant-model evaluations on a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026), with an independent 900-variant expert-panel validation set and three triangulation sub-experiments (allele-frequency ablation, conflicting-interpretation variants, and functional-effect variants). We address three questions: (RQ1) How reliable is LLM variant classification under label-leakage control? (RQ2) Do multi-model consensus and model choice improve reliability? (RQ3) How does reliability depend on the evidence available to the model?

We find that label-leakage control reveals a large vendor gap (up to +22 pp), that the "when the model speaks it is right" property holds only for conservative models, that majority voting can reduce accuracy, and that model reliability tracks evidence availability — abstention is a calibrated, trustworthy signal rather than noise. We frame this work as a **reliability audit** rather than a generalization study: temporal blinding removes the label-memorization channel, but prior *evidence* (literature, submissions) may remain in training data; our goal is therefore to establish under which operational conditions an LLM's output can be trusted, not to claim de novo generalization from sequence alone.

## 5. Discussion (draft)

### 5.1 Principal findings

Under label-leakage control (temporal blinding of the gold-standard label), new-generation LLMs classify 62–72% of variants correctly (all-inclusive), rising to 86–93% on expert-panel-reviewed variants. When conservative models commit to a call, they are right 97.8–98.7% of the time, mislabeling only 1.3–2.5% of Benign variants as Pathogenic; reasoning models, by contrast, mislabel 22–28% of Benign variants as Pathogenic — the clinically dangerous direction. These are substantially lower than unblinded reports (~96% [4]); interpreted as a reliability audit, they define the *operational envelope* in which an LLM's output can be trusted, rather than a ceiling on generalization: label memorization is controlled, and remaining performance reflects the evidence the model actually reasons with.

### 5.2 Vendor choice matters more than ensemble size

The gap between the best and worst model (+22.4 pp all-inclusive; +25 pp expert-panel) exceeds the gain from any ensemble strategy we tested, and naive majority voting *reduced* accuracy below the best single model because conservative voters dominate ties. Two implications: (i) published "LLM accuracy" without model identity is meaningless; (ii) clinical deployments should select models on blinded benchmarks, not on ensemble size. The recommendation is model-specific — Kimi and Qwen excel on evidence-rich variants, while reasoning models (V4-pro, MiMo) commit more often but less reliably.

### 5.3 Abstention is calibrated behavior, not conservatism

Three independent experiments converge: models abstain more when evidence is missing (AF ablation: abstention falls 80%→33% once allele frequencies are provided), when experts disagree (conflicting variants: +22–39 pp abstention without being told), and when the task has no clinical evidence at all (MaveDB functional task: 73–93% abstention). LLMs behave like evidence-aware decision systems: they express uncertainty where evidence is weak and commit where it is strong. Clinically, this makes abstention a **trustworthy triage signal** — "the model said Uncertain, therefore review by a human" is a safe operating policy, and our data show the model is disproportionately Uncertain precisely when human review is needed.

### 5.3b Reproducibility as a reliability property

At temperature 0, chat-style models are exactly reproducible (100% over 50 re-runs), but the reasoning model V4-pro changed its binary call on 36% of re-run variants, including direct Benign↔Pathogenic flips. Average accuracy alone is therefore insufficient to audit a model for clinical use: a non-deterministic model cannot be deployed regardless of its mean performance, and reported single-run accuracies for such models are themselves noisy. The audit framing makes this explicit: determinism, like accuracy and abstention calibration, is a measured property we report per model rather than assume.

### 5.4 The information-deficit explanation of Benign underperformance

The most striking baseline result — Benign sensitivity of 9.6–43% — is largely explained by missing allele-frequency evidence. With AF provided, Benign sensitivity rises by up to +57.8 pp and all-inclusive accuracy roughly triples. ACMG rules BA1/BS1 (population frequency) are among the strongest Benign evidence; omitting them cripples the Benign side of the classification. Practical implication: any LLM-based variant interpretation pipeline must integrate population-frequency databases; performance numbers reported without AF are systematically pessimistic about Benign recall.

### 5.5 Relation to prior work

AI-CURA [4] demonstrated expert-consistency without leakage control; our label-blinded numbers (62–72%) suggest that a substantial part of unblinded performance may be label memorization. ClawBench [5] introduced temporal blinding but reported single-family results; we extend to four vendors and add independent gold standards. Our conditional-accuracy framing (speak vs. abstain) is, to our knowledge, new to this literature and reconciles the "impressive when confident" and "unusable overall" observations in prior reports. Positioning: whereas AI-CURA asks "can LLMs classify variants?", we ask "under which auditable conditions can an LLM's classification be trusted?" — the audit framing keeps our claims within what temporal blinding can actually establish.

### 5.6 Limitations

(i) Vendor panel is Chinese-commercial; conclusions about LLMs generally require non-Chinese models (in progress). (ii) Temporal blinding approximates leakage control via LastEvaluated date; a variant's *evidence* (submissions, literature) may predate its label, so the model could still have seen evidence if not the final label. (iii) Binary P/B evaluation collapses ACMG's five classes and penalizes "Likely" mapping strategies. (iv) The MaveDB functional direction is a soft validation. (v) Single task (germline SNV/indel); splice/structural/de novo variants unaddressed. (vi) Cost audit (30 variants × 6 models, API-reported usage): reasoning models emit 13–21× more output tokens (chain-of-thought billed as completion), per-variant cost spans 41× (MiMo ¥0.041 vs. chat ¥0.001) and latency spans 29× (65.9 s vs. 2.3 s) — yet reasoning models buy neither accuracy, stability, nor safety (22–28% Benign→Pathogenic false positives).

### 5.7 Conclusion

Under label-leakage control, LLM variant interpretation passes reliability audit under three conditions: the model is chosen on blinded evidence (vendor gap up to +22 pp; majority voting can hurt), complete evidence is provided (AF mandatory; +58 pp Benign sensitivity), and abstention is deployed as a human-review trigger. We provide the first multi-vendor, temporally controlled, independently validated reliability audit, and recommend that (i) published accuracies report model identity, blinding status, and evidence conditions; (ii) clinical pilots adopt "Pathogenic calls auto-flag, Uncertain calls auto-escalate" operating policies; and (iii) future audits extend to non-Chinese vendors and additional task types.

---

## References (placeholder)

[1] ACMG/AMP 2015 guidelines (Richards et al., Genet Med 2015).
[2] LLM variant interpretation surveys (2025–2026).
[3] ClinVar-BERT (Genome Medicine 2026).
[4] AI-CURA (Science Translational Medicine 2026).
[5] ClawBench (bioRxiv 2026).
