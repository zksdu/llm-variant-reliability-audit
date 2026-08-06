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
