# Abstract & Methods (Draft) — English Manuscript Section

> Companion to Results_draft_EN.md. Draft for internal review (2026-08-06).

---

## Abstract (draft)

**Background.** Large language models (LLMs) are increasingly proposed for clinical variant interpretation using ACMG/AMP guidelines. Reported accuracies are difficult to interpret because LLM training corpora include public variant databases (ClinVar, ClinGen): high scores may reflect memorization of ground-truth labels rather than genuine clinical reasoning.

**Objective.** To audit the reliability of LLM-based variant classification under controlled label leakage (temporal blinding), across multiple vendors and evidence conditions — establishing under which operational conditions an LLM's output can be trusted.

**Methods.** We constructed a temporally blinded test set of 5,000 ClinVar variants (all expert-assessed after January 2026, beyond the training cutoff of all evaluated models) and evaluated 6 LLMs from 4 vendors (DeepSeek v4-pro/chat/coder, Kimi-K2.6, MiMo V2.5 Pro, Qwen3.7-max) — 30,000 variant-model evaluations in total. We report dual metrics: all-inclusive accuracy (VUS = error; clinical usability) and conditional accuracy when the model commits (reliability). Independent validation used 900 expert-panel-reviewed variants; ablation studies tested the effect of allele-frequency evidence, behavior on variants with conflicting expert classifications (n=300), and functional-effect variants from MaveDB (n=300).

**Results.** New-generation models achieved 61.8–71.6% all-inclusive accuracy under temporal blinding, rising to 86–93% on expert-panel gold standard. Conditional accuracy when committing was 97.8–98.7% for conservative models (false-positive rate ≤ 0.6%) but only 81.2–85.2% for reasoning models. Providing allele frequencies raised Benign sensitivity from 11.0% to 68.8% (chat) and roughly tripled all-inclusive accuracy. On conflicting variants, models spontaneously raised abstention by 22–39 pp; on evidence-free functional variants, abstention reached 73–93% with chance-level conditional agreement. At temperature 0, chat-style models reproduced outputs exactly (100%) while a reasoning model changed its binary call on 36% of re-run variants, including Benign↔Pathogenic flips.

**Conclusion.** Under label-leakage control, LLM variant interpretation is a qualified yes: reliable when (i) the right model is chosen — vendor differences (up to +22 pp) exceed ensemble gains, and majority voting can *reduce* accuracy; (ii) complete evidence (allele frequency) is provided; and (iii) abstention is treated as a trustworthy signal for human review. We provide the first multi-vendor, temporally controlled reliability audit of this capability, and recommend that (i) published accuracies report model identity, blinding status, and evidence conditions; (ii) clinical pilots adopt "Pathogenic calls auto-flag, Uncertain calls auto-escalate" operating policies; and (iii) future audits extend to non-Chinese vendors and additional task types.

---

## Methods (draft)

### 2.1 Data sources

- **ClinVar variant_summary** (Aug 2026 release; 9,029,235 rows; 43 columns), used for test-set construction and gold-standard labels.
- **ClinVar VCF (GRCh38)** (clinvar.vcf.gz; ~193 MB), used to attach population allele frequencies (AF_ESP, AF_EXAC, AF_TGP) by ALLELEID.
- **MaveDB** (Ensembl-mapped release; 3,158,202 scored variants), used for the functional-effect triangulation experiment; gene symbols resolved via mygene.info (RefSeq accession → symbol).
- All data are public; download URLs in Data Availability.

### 2.2 Temporally blinded test set (label-leakage control)

The central design decision: LLM training corpora contain ClinVar history, so evaluation must use variants whose **gold-standard labels** were produced **after** the model training cutoff. This controls the label-memorization channel specifically; prior *evidence* (literature, submissions) may still be present in training data, and we therefore frame the study as a reliability audit under controlled label leakage rather than a generalization test (see Discussion).

- Model cutoffs (verified 2026-08): DeepSeek V4 ~Dec 2025; Kimi/GLM/MiMo/Qwen families ≤ 2025. We conservatively require **LastEvaluated ≥ 2026-01-01**.
- Eligibility: unambiguous clinical classification (Pathogenic or Benign only; "Likely" and compound terms excluded from the P/B gold standard), a HGVS name, and no conflicting classification.
- De-duplication by ALLELEID (4.9% of raw rows were duplicate allele entries).
- Stratified sampling: 2,500 Pathogenic + 2,500 Benign, seed 42 (reproducible), yielding n = 5,000.
- Result: all 5,000 variants were expert-assessed ≥ 2026-04 (median later), i.e., the models cannot have seen these labels during training.

### 2.3 Gold standards

- **Primary**: ClinVar aggregate classification (Pathogenic/Benign binary).
- **Gold standard A (expert panel)**: ReviewStatus ∈ {reviewed by expert panel, practice guideline} — classifications produced by ClinGen variant-curation expert panels / guideline committees. Dedicated validation set: 900 such variants (P: 647, B: 252; all ≥ 2026-04). Of these, 100 were also sampled into the main test set (Table 1, expert-panel stratum); the dedicated-set analysis therefore reports **800 exclusive variants (797 evaluable)** for strict independence, with the full 900 as a robustness check. Gold standard A (broad): expert-panel ∪ {multiple submitters, no conflicts}.
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
- **Consensus**: majority vote across models on the three-way (P/B/VUS) semantics — semantically close classes (e.g., Pathogenic vs. Likely pathogenic) do not split votes; ties excluded (reported separately).
- Expert-panel stratification (gold A strict/broad) applied to every model and the consensus.
- **Statistics**: Wilson 95% confidence intervals for all accuracies; McNemar's paired test (normal approximation with continuity correction, n > 30) for model comparisons on the shared variant set; consensus vs. best-single-model compared descriptively. Model-output determinism checked by re-running 50 variants × 3 models (temperature 0) and measuring classification agreement.

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
