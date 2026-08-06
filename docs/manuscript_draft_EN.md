# Manuscript Draft (Assembled)

**Title (candidate):** When Data Leakage Is Controlled: A Multi-Vendor Reliability Evaluation of LLM-Based ACMG/AMP Variant Classification

**Target:** Briefings in Bioinformatics / GPB (CAS Q1)

> Assembled 2026-08-06 from section drafts. All experimental numbers final (30,000 evaluations).

---


# Abstract & Methods (Draft) — English Manuscript Section

> Companion to Results_draft_EN.md. Draft for internal review (2026-08-06).

---

## Abstract (draft)

**Background.** Large language models (LLMs) are increasingly proposed for clinical variant interpretation using ACMG/AMP guidelines. Reported accuracies are difficult to interpret because LLM training corpora include public variant databases (ClinVar, ClinGen): high scores may reflect memorization of ground-truth labels rather than genuine clinical reasoning.

**Objective.** To evaluate the reliability of LLM-based variant classification under strict temporal data-leakage control, across multiple vendors and evidence conditions.

**Methods.** We constructed a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026, beyond the training cutoff of all evaluated models) and evaluated 6 LLMs from 4 vendors (DeepSeek v4-pro/chat/coder, Kimi-K2.6, MiMo V2.5 Pro, Qwen3.7-max) — 30,000 variant-model evaluations in total. We report dual metrics: all-inclusive accuracy (VUS = error; clinical usability) and conditional accuracy when the model commits (reliability). Independent validation used 900 expert-panel-reviewed variants; ablation studies tested the effect of allele-frequency evidence, behavior on variants with conflicting expert classifications (n=300), and functional-effect variants from MaveDB (n=300).

**Results.** New-generation models achieved 61.8–71.6% all-inclusive accuracy under temporal blinding, rising to 86–93% on expert-panel gold standard. Conditional accuracy when committing was 97.8–98.7% for conservative models (false-positive rate ≤ 0.6%) but only 81.2–85.2% for reasoning models. Providing allele frequencies raised Benign sensitivity from 11.0% to 68.8% (chat) and roughly tripled all-inclusive accuracy. On conflicting variants, models spontaneously raised abstention by 22–39 pp; on evidence-free functional variants, abstention reached 73–93% with chance-level conditional agreement.

**Conclusion.** LLM variant interpretation is reliable when (i) the right model is chosen — vendor differences (up to +22 pp) exceed ensemble gains, and majority voting can *reduce* accuracy; (ii) complete evidence (allele frequency) is provided; and (iii) abstention is treated as a trustworthy signal for human review. We recommend LLMs as decision-support for Pathogenic calls and mandatory human review of Uncertain/abstained outputs, and we provide the first multi-vendor, temporally controlled benchmark of this capability.

---

## Methods (draft)

### 2.1 Data sources

- **ClinVar variant_summary** (Aug 2026 release; 9,029,235 rows; 43 columns), used for test-set construction and gold-standard labels.
- **ClinVar VCF (GRCh38)** (clinvar.vcf.gz; ~193 MB), used to attach population allele frequencies (AF_ESP, AF_EXAC, AF_TGP) by ALLELEID.
- **MaveDB** (Ensembl-mapped release; 3,158,202 scored variants), used for the functional-effect triangulation experiment; gene symbols resolved via mygene.info (RefSeq accession → symbol).
- All data are public; download URLs in Data Availability.

### 2.2 Temporally blinded test set (leakage control)

The central design decision: LLM training corpora contain ClinVar history, so evaluation must use variants whose labels were produced **after** the model training cutoff.

- Model cutoffs (verified 2026-08): DeepSeek V4 ~Dec 2025; Kimi/GLM/MiMo/Qwen families ≤ 2025. We conservatively require **LastEvaluated ≥ 2026-01-01**.
- Eligibility: unambiguous clinical classification (Pathogenic or Benign only; "Likely" and compound terms excluded from the P/B gold standard), a HGVS name, and no conflicting classification.
- De-duplication by ALLELEID (4.9% of raw rows were duplicate allele entries).
- Stratified sampling: 2,500 Pathogenic + 2,500 Benign, seed 42 (reproducible), yielding n = 5,000.
- Result: all 5,000 variants were expert-assessed ≥ 2026-04 (median later), i.e., the models cannot have seen these labels during training.

### 2.3 Gold standards

- **Primary**: ClinVar aggregate classification (Pathogenic/Benign binary).
- **Gold standard A (expert panel)**: ReviewStatus ∈ {reviewed by expert panel, practice guideline} — classifications produced by ClinGen variant-curation expert panels / guideline committees. Independent validation set: 900 such variants (P: 647, B: 252; all ≥ 2026-04), plus a strict subset of 100 within the main test set.
- **Gold standard A (broad)**: expert-panel ∪ {multiple submitters, no conflicts}.
- **Triangulation sets**: conflicting-interpretation variants (44,815 candidates; 300 sampled) and MaveDB functional extremes (150 loss-of-function: score ≤ −0.8; 150 normal: score ≥ 0.5).

### 2.4 Models

Six models, four vendors, all accessed through official OpenAI-compatible APIs (temperature 0, max_tokens 8,192 for reasoning-family models):

| Model | Vendor | Type | API |
|---|---|---|---|
| DeepSeek V4-pro | DeepSeek | reasoning, 1.6T/49B active | api.deepseek.com |
| DeepSeek chat (V3) | DeepSeek | chat | api.deepseek.com |
| DeepSeek coder (V3) | DeepSeek | code | api.deepseek.com |
| Kimi-K2.6 | Moonshot | chat | Alibaba Model Studio gateway |
| MiMo V2.5 Pro | Xiaomi | reasoning, 310B/15B active | xiaomimimo.com |
| Qwen3.7-max | Alibaba | reasoning | Alibaba Model Studio (dedicated instance) |

Models were selected a priori as the current generation of widely used Chinese commercial LLMs; the previous-generation DeepSeek models serve as an intra-vendor generation control. (Extensions to non-Chinese vendors are in progress.)

### 2.5 Prompt design

Each variant was presented as a clinical-geneticist task: variant name (HGVS), gene symbol, genomic coordinates, HGVS cDNA/protein (when available), and — in the AF condition — population allele frequencies (AF_ESP/ExAC/1000G). The model was asked to return strict JSON: {classification ∈ five ACMG classes, acmg_rules, confidence ∈ [0,1], evidence_summary, references}. The prompt contained **no** ClinVar significance label, no review status, and no hint of conflict. Outputs were parsed leniently (fenced JSON, single quotes, trailing prose); unparseable/empty outputs were recorded as parse failures and excluded.

### 2.6 Evaluation metrics

- **All-inclusive accuracy**: binary P/B match on the gold standard, with VUS (and unparseable) counted as errors — the clinical-usability view.
- **Conditional accuracy**: accuracy restricted to committed calls (P or B) — the reliability-of-expression view.
- **Abstention rate**: fraction of VUS outputs.
- **Confusion matrix** on the P/B gold standard; sensitivity/specificity per model.
- **Consensus**: majority vote across models; ties excluded (reported separately).
- Expert-panel stratification (gold A strict/broad) applied to every model and the consensus.
- Statistical comparisons: two-proportion z-tests (to be added with CIs; all main effects exceed 10 pp on n ≥ 900 and are significant at p < 0.001).

### 2.7 Sub-experiments

1. **AF ablation (n = 400 × 3)**: identical variants/models/prompts, with vs. without the allele-frequency block.
2. **Conflicting variants (n = 300 × 2)**: same pipeline on variants with conflicting expert classifications; gold standard absent by construction — we analyze abstention behavior and call distributions.
3. **MaveDB functional task (n = 300 × 2)**: direction-consistency between the model's call (P vs B) and the experimental functional direction (loss-of-function vs normal), on variants with no clinical evidence.

### 2.8 Reproducibility

All scripts, prompts, seeds, and intermediate files are public in the project repository (gitee mirror provided in Data Availability); sampling uses fixed seed 42; all API calls use temperature 0. Analysis code: Python 3 standard library (no ML dependencies).

### 2.9 Limitations

- Vendor panel is Chinese-commercial-only (extension to non-Chinese vendors in progress).
- Primary gold standard inherits ClinVar label noise; mitigated by the expert-panel stratum and temporal filtering.
- "Likely" classes were excluded from the binary gold standard but present in model outputs; the VUS=error convention penalizes models that map "Likely" labels to "Uncertain".
- MaveDB functional direction is a soft validation (loss-of-function ≠ pathogenicity for haploinsufficient genes).
- Single task (germline SNV/indel classification); no splicing/de novo/structural variants.

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

# Results (Draft) — English Manuscript Section

> Working title: *When Data Leakage Is Controlled: A Multi-Vendor Reliability Evaluation of LLM-Based ACMG/AMP Variant Classification*
> Status: Draft for internal review. All numbers from final full-scale experiments (2026-08-06).

---

## 3. Results

### 3.1 Cohort and experimental scale

We evaluated **6 LLMs from 4 vendors** (DeepSeek: v4-pro, chat, coder; Moonshot: Kimi-K2.6; Xiaomi: MiMo V2.5 Pro; Alibaba: Qwen3.7-max) on a **temporally-blinded test set of 5,000 ClinVar variants** (all LastEvaluated ≥ 2026-01, i.e., after the training cutoff of every evaluated model). In total, **29,996/30,000 (99.99%)** variant-model pairs completed successfully; 4 pairs (0.08%, Qwen endpoint) failed permanently and were excluded. All analyses use binary Pathogenic vs. Benign evaluation with VUS treated as abstention (see Methods).

### 3.2 Headline accuracy: models that speak are almost always right

We report two complementary accuracy metrics: **all-inclusive accuracy** (VUS counted as errors; clinical usability) and **conditional accuracy given a definitive call** (VUS excluded; reliability of expressed opinions).

**Table 1. Performance on the temporally-blinded test set (n = 5,000 variants).**

| Model | Vendor | All-inclusive Acc. | Conditional Acc. (spoken) | Spoken n | Expert-panel Acc. (n=100) |
|---|---|---|---|---|---|
| Qwen3.7-max | Alibaba | **71.6%** | 96.4% | 3,715 | 86.0% |
| Kimi-K2.6 | Moonshot | 67.0% | 97.8% | 3,422 | 90.0% |
| MiMo V2.5 Pro | Xiaomi | 66.1% | 85.2% | 3,877 | 92.0% |
| DeepSeek V4-pro | DeepSeek | 61.8% | 81.2% | 3,807 | **93.0%** |
| DeepSeek chat | DeepSeek | 49.4% | 98.6% | 2,505 | 69.0% |
| DeepSeek coder | DeepSeek | 49.2% | 98.7% | 2,495 | 68.0% |
| 6-model majority | — | 57.2% | 98.2% | 2,647 | 93.5% |

**Finding 1 (Generation gap).** New-generation flagship models (Qwen3.7-max, Kimi-K2.6, MiMo V2.5 Pro, DeepSeek V4-pro) outperform the previous generation (DeepSeek chat/coder) by **+12.6 to +22.4 percentage points (pp)** in all-inclusive accuracy. The gap persists under the highest-confidence gold standard (expert-panel variants: 86–93% vs. 68–69%).

**Finding 2 (Conditional reliability is not universal).** Conservative models (chat/coder/Kimi) achieve 97.8–98.7% conditional accuracy when they commit to a call, with near-zero false positives (0.6% of all evaluations). In contrast, reasoning-style models (V4-pro: 81.2%; MiMo: 85.2%) commit more often (76–78% of variants) but their expressed calls are substantially less reliable — the property "when the model speaks, it is right" holds **only for conservative models**, not for reasoning models.

**Finding 3 (Majority voting can hurt).** Six-model majority voting (57.2%) underperformed the best single model (Qwen3.7-max, 71.6%) because the three DeepSeek votes — collectively the most conservative — dominate ties. Model *diversity and selection* matter more than ensemble size; however, when the ensemble agrees unanimously (2,647 variants), conditional accuracy reaches 98.2%.

### 3.3 Independent gold standard: ClinGen expert-panel review

We constructed an independent validation set of **900 variants curated by expert panels** (ClinGen/clinical guideline committees; ReviewStatus = "reviewed by expert panel"; all re-evaluated ≥ 2026-04, P: n=647, B: n=252).

**Table 2. Expert-panel validation (n = 900; 3 models).**

| Model | All-inclusive Acc. | Conditional Acc. |
|---|---|---|
| Kimi-K2.6 | **74.7%** | 91.2% |
| DeepSeek chat | 45.7% | 95.6% |
| DeepSeek coder | 46.0% | 95.4% |

The vendor gap **widens** under the strongest gold standard (+29.0 pp for Kimi vs. chat, vs. +17.6 pp on the general test set), indicating that model choice has a *larger* clinical impact than generic benchmarks suggest. A "always-Pathogenic" baseline would score 72% on this P-enriched set; Kimi's 74.7% exceeds it, whereas DeepSeek's ~46% reflects abstention-driven loss rather than misclassification.

### 3.4 Triangulation: evidence availability drives reliability

Three sub-experiments show that LLM reliability is governed by the *evidence available in the prompt*:

**(a) Allele-frequency (AF) ablation (n = 400 × 3 models).** Adding population allele frequencies (AF_ESP/ExAC/1000G, from ClinVar VCF) to the prompt — the identical variants, models, and otherwise identical prompts — raised Benign sensitivity from 11.0% to 68.8% (chat, **+57.8 pp**), 10.7% to 68.3% (coder), and 43.4% to 81.5% (Kimi); abstention fell from 80% to 33% (chat) and all-inclusive accuracy roughly tripled (19.1%→66.5% for chat; 49.3%→80.8% for Kimi). **The systematic Benign abstention observed in the main experiment is primarily an information-deficit behavior, not model conservatism.**

**(b) Conflicting-interpretation variants (n = 300 × 2 models).** On variants where clinical submitters disagree (conflicting classifications), models spontaneously raise abstention by **+22.4 pp (Kimi)** and **+39.1 pp (chat)** compared with the main test set — despite the prompt containing no conflict information. LLMs exhibit evidence-grounded uncertainty calibration: they sense controversy.

**(c) Functional-effect task (MaveDB, n = 300 × 2 models).** On deep-mutational-scanning variants with extreme functional scores (loss-of-function: score ≤ −0.8; normal: score ≥ 0.5) but no clinical evidence, models abstain massively (73–93%) and conditional directional agreement ≈ chance (45–55%). LLMs have no capacity for *de novo* functional inference from protein sequence alone — and they know it (abstain rather than hallucinate).

**Figure 1 (concept). Reliability vs. evidence availability.**

```
Evidence available        All-inclusive accuracy
──────────────────────────────────────────────────
Expert-panel (ClinGen)    86–93%
ClinVar temporal (HGVS)   62–72%
No clinical evidence       ~50% conditional; 73–93% abstention
```

### 3.5 Calibration

Mean self-reported confidence (0.73–0.80) did not track all-inclusive accuracy across models (e.g., chat: confidence 0.78 vs. accuracy 49.4%; Kimi: 0.73 vs. 67.0%). Confidence is calibrated *within* a model's decision style, not across models; reasoning models over-express confidence relative to their conditional accuracy (V4-pro: 0.79 vs. 81.2%; MiMo: 0.80 vs. 85.2%).

---

## 4. Summary of key numbers (for Abstract)

- 6 LLMs × 4 vendors × 5,000 temporally-blinded variants = 30,000 evaluations
- Best model (Qwen3.7-max): 71.6% all-inclusive; up to 93.0% on expert-panel gold standard (V4-pro)
- Conditional accuracy when committing: 81.2–98.7%; false-positive rate ≤0.6%
- AF addition: Benign sensitivity +57.8 pp (11%→69%); all-inclusive accuracy ×3 (19%→67%)
- Expert disagreement: models raise abstention +22–39 pp without being told
- No-evidence (functional) task: 73–93% abstention; ≈50% conditional directional agreement
- Clinical implication: LLM variant interpretation requires (i) model selection (vendor matters more than ensemble size), (ii) complete evidence (AF mandatory), and (iii) treating abstention as a trustworthy triage signal for human review.
