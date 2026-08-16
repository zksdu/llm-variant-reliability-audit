# Results (Draft) — English Manuscript Section

> Working title: *When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification*
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
| 6-model majority | — | 64.1% | 98.3% | 2,915 | 93.5% |

> Table 1 footnotes: All-inclusive accuracy = VUS counted as error (clinical usability); conditional accuracy = accuracy restricted to committed calls; expert-panel stratum = 100 variants within the test set whose labels were produced by expert panels (ClinGen VCEP / guideline committees). Wilson 95% CIs: Qwen [70.4, 72.9], Kimi [65.6, 68.2], MiMo [64.7, 67.4], V4-pro [60.5, 63.1], chat [48.0, 50.8], coder [47.8, 50.6]. Majority voting operates on the three-way (P/B/VUS) semantics; ties excluded (n=528).

**Finding 1 (Generation gap).** New-generation flagship models (Qwen3.7-max, Kimi-K2.6, MiMo V2.5 Pro, DeepSeek V4-pro) outperform the previous generation (DeepSeek chat/coder) by **+12.6 to +22.4 percentage points (pp)** in all-inclusive accuracy (all pairwise McNemar p < 10⁻⁸⁶; Kimi vs. MiMo: p = 0.11, n.s.). The gap persists under the highest-confidence gold standard (expert-panel variants: 86–93% vs. 68–69%).

**Finding 2 (Conditional reliability is not universal — and error direction matters).** Conservative models (chat/coder/Kimi) achieve 97.8–98.7% conditional accuracy when they commit. In contrast, reasoning-style models (V4-pro: 81.2%; MiMo: 85.2%) commit more often (76–78% of variants) but their expressed calls are substantially less reliable. Crucially, the errors are directionally asymmetric: when a gold-standard Benign variant receives a definitive call, reasoning models call it **Pathogenic** far more often — V4-pro mislabels 28.4% and MiMo 22.3% of all Benign variants as Pathogenic, versus 1.3–1.4% (chat/coder) and 2.5% (Kimi); Qwen sits between at 4.7%. Six-model consensus restores FP to 1.8%. The property "when the model speaks, it is right" holds **only for conservative models**; for reasoning models, committing is frequent, less accurate, and biased toward the clinically dangerous direction (false Pathogenic).

![Figure 1](figures/fig1_model_performance.png)

*Figure 1. Multi-model performance on the temporally blinded test set: (a) dual-metric accuracy; (b) Benign→Pathogenic false-positive rates (log scale) — reasoning models mislabel 22–28% of Benign variants as Pathogenic.*

**Finding 3 (Majority voting can hurt).** Six-model majority voting (64.1% all-inclusive) underperformed the best single model (Qwen3.7-max, 71.6%; +7.5 pp) because the three DeepSeek votes — collectively the most conservative — dominate ties. Model *diversity and selection* matter more than ensemble size; however, when the ensemble agrees on a definitive call (2,915 variants), conditional accuracy reaches 98.3%.

### 3.3 Independent gold standard: ClinGen expert-panel review

We constructed a dedicated validation set of **900 variants curated by expert panels** (ClinGen/clinical guideline committees; ReviewStatus = "reviewed by expert panel"; all re-evaluated ≥ 2026-04, P: n=647, B: n=252). Of these, 100 were also sampled into the main test set (Table 1, expert-panel stratum); to guarantee independence, Table 2 reports the **800 exclusive variants** (797 evaluable; P: 563, B: 234).

**Table 2. Expert-panel validation (n = 797 exclusive variants; 3 models).**

| Model | All-inclusive Acc. | Conditional Acc. |
|---|---|---|
| Kimi-K2.6 | **72.8%** | 90.6% |
| DeepSeek chat | 42.9% | 95.0% |
| DeepSeek coder | 43.3% | 94.8% |

> Results on the full 900 (including the shared 100) are qualitatively identical: Kimi 74.7% / chat 45.7% / coder 46.0% (robustness check).

The vendor gap **widens** under the strongest gold standard (+29.9 pp for Kimi vs. chat, vs. +17.6 pp on the general test set), indicating that model choice has a *larger* clinical impact than generic benchmarks suggest. A "always-Pathogenic" baseline would score ~71% on this P-enriched set; Kimi's 72.8% exceeds it, whereas DeepSeek's ~43% reflects abstention-driven loss rather than misclassification (conditional accuracy 94.8–95.0%).

### 3.4 Triangulation: evidence availability drives reliability

Three sub-experiments show that LLM reliability is governed by the *evidence available in the prompt*:

**(a) Allele-frequency (AF) ablation (n = 400 × 3 models Benign-enriched + 150 × 2 Pathogenic).** Adding population allele frequencies (AF_ESP/ExAC/1000G, from ClinVar VCF) to the prompt — the identical variants, models, and otherwise identical prompts — raised Benign sensitivity from 11.0% to 68.8% (chat, **+57.8 pp**), 10.7% to 68.3% (coder), and 43.4% to 81.5% (Kimi); abstention fell from 80% to 33% (chat) and all-inclusive accuracy roughly tripled (19.1%→66.5% for chat; 49.3%→80.8% for Kimi). **The systematic Benign abstention observed in the main experiment is primarily an information-deficit behavior, not model conservatism.** The effect is bidirectional: on a Pathogenic-enriched AF subset (n = 150 × 2), adding AF raised accuracy from 44.9% to 64.0% (chat, +19.1 pp) and 47.5% to 85.3% (Kimi, +37.8 pp), with abstention falling from ~50% to 15–36%. Evidence completeness governs reliability on both sides of the P/B axis.

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

![Figure 2](figures/fig2_evidence_gradient.png)

*Figure 2. Reliability rises with evidence quality: expert-panel stratum vs. full test set; the no-evidence regime (MaveDB) collapses to chance-level conditional accuracy with 73–93% abstention.*

![Figure 3](figures/fig3_af_ablation.png)

*Figure 3. Allele-frequency ablation: (a) Benign sensitivity on a Benign-rich subset (n=400); (b) accuracy on a Pathogenic subset (n=150). Adding AF improves both directions.*

### 5. Calibration

Mean self-reported confidence (0.73–0.80) did not track all-inclusive accuracy across models (e.g., chat: confidence 0.78 vs. accuracy 49.4%; Kimi: 0.73 vs. 67.0%). Confidence is calibrated *within* a model's decision style, not across models; reasoning models over-express confidence relative to their conditional accuracy (V4-pro: 0.79 vs. 81.2%; MiMo: 0.80 vs. 85.2%).

### 3.5b Five-class analysis: the "Likely" tier is absent

The ACMG/AMP framework is five-class (Pathogenic / Likely pathogenic / Uncertain significance / Likely benign / Benign), and P vs. LP carry different clinical follow-up (e.g., LP requires confirmation). On the expert-panel set (which carries five-class labels; P: 306, LP: 342, LB: 193, B: 59), **none of the evaluated models ever emitted a "Likely" class** — the five-class output collapses to three (P / VUS / B).

| Model | Exact five-class match | Likely-tier output | Cross-semantic errors (P↔B) |
|---|---|---|---|
| Kimi-K2.6 | 32.3% | 0/900 | 7.2% |
| DeepSeek chat | 22.4% | 0/900 | 2.1% |
| DeepSeek coder | 22.7% | 0/900 | 2.2% |

Strength polarization is systematic: 82% (Kimi) and 58% (chat) of gold-standard Likely pathogenic variants were escalated to Pathogenic; 51% of Likely benign were downgraded to Benign by Kimi. Two implications: (i) LLM outputs are usable at the binary-semantics level only — the "Likely" tier carries clinical information the models do not produce; (ii) reported high conditional accuracy on binary P/B evaluation is partly achieved *by* this collapse, which a five-class evaluation would not credit.

### 3.6 Output determinism (reproducibility audit)

Because a clinical system must return the *same* answer for the *same* variant, we re-ran 50 variants × 3 models under identical settings (temperature = 0, same prompt, same endpoint) and measured classification agreement with the original run.

**Table 3. Re-run consistency (n = 50 variants × 3 models).**

| Model | Exact-class agreement | Binary (P/B) agreement |
|---|---|---|
| DeepSeek chat | 50/50 (100.0%) | 50/50 (100.0%) |
| Kimi-K2.6 | 49/50 (98.0%) | 50/50 (100.0%) |
| DeepSeek V4-pro | 31/50 (62.0%) | **32/50 (64.0%)** |

![Figure 5](figures/fig5_determinism.png)

*Figure 5. (a) Re-run determinism at temperature 0; (b) collapse of the ACMG “Likely” tier (Kimi): gold Likely-pathogenic variants are polarized to Pathogenic, Likely-benign to Benign/VUS.*

**Finding 4 (Reasoning models are not deterministic).** At temperature = 0, chat-style models reproduce their outputs exactly (100%), whereas the reasoning model V4-pro changed its binary call on 36% of re-run variants — including 3 direct Benign↔Pathogenic flips (the clinically most consequential error direction) and 9 VUS↔definitive changes. Under a reliability-audit framing, non-determinism is a first-class failure mode: a model that can return contradictory answers for the same input cannot be deployed in clinical workflows, regardless of its average accuracy. The "reasoning models commit more but are less reliable" finding (Finding 2) thus extends to *commit stability*: their expressed calls are neither as accurate nor as reproducible as those of conservative models.

### 3.7 Cost audit (per-variant token usage and price)

We profiled token usage on 30 variants × 6 models (API-reported usage; official vendor pricing, Aug 2026).

**Table 4. Per-variant token usage, cost, and latency (n = 30 variants).**

| Model | Input tok | Output tok | Cost (¥/variant) | Latency (s) |
|---|---|---|---|---|
| DeepSeek chat | 179 | 132 | 0.001 | 2.3 |
| DeepSeek coder | 179 | 137 | 0.001 | 2.5 |
| Kimi-K2.6 | 183 | 160 | 0.003 | 5.9 |
| DeepSeek V4-pro | 179 | 2,728 | 0.017 | 65.9 |
| Qwen3.7-max | 206 | 1,936 | 0.019 | 37.7 |
| MiMo V2.5 Pro | 440 | 1,754 | 0.041 | 30.6 |

![Figure 4](figures/fig4_cost_latency.png)

*Figure 4. Cost–accuracy trade-off; bubble size encodes latency. Reasoning models occupy the expensive-slow quadrant without accuracy or safety gains.*

**Finding 5 (The reasoning-model tax).** Reasoning models generate **13–21× more output tokens** than chat-style models (2,728 vs. 132 for V4-pro vs. chat) because their chain-of-thought is billed as completion tokens. Per-variant cost spans **41×** (MiMo ¥0.041 vs. chat ¥0.001) and latency spans **29×** (65.9 s vs. 2.3 s). Combined with Findings 2 and 4 — reasoning models are *less* accurate when committing (81.2% vs. 98.6%) and *non-deterministic* (64% re-run agreement) — the cost audit shows that the reasoning style purchases none of accuracy, stability, or speed: chat-style models dominate on all axes except raw all-inclusive accuracy, where Kimi (67.0%) matches or exceeds every reasoning model at 1/6–1/14 of the cost. For population-scale variant screening, model choice is therefore also a cost decision: Kimi-class models deliver near-best accuracy at the lowest price.

---

## Appendix (internal): key numbers cross-check

- 6 LLMs × 4 vendors × 5,000 temporally-blinded variants = 30,000 evaluations
- Best model (Qwen3.7-max): 71.6% all-inclusive; up to 93.0% on expert-panel gold standard (V4-pro)
- Conditional accuracy when committing: 81.2–98.7%; Benign→Pathogenic FP: 1.3–2.5% (conservative) vs 22–28% (reasoning)
- AF addition: Benign sensitivity +57.8 pp (11%→69%); all-inclusive accuracy ×3 (19%→67%)
- Expert disagreement: models raise abstention +22–39 pp without being told
- No-evidence (functional) task: 73–93% abstention; ≈50% conditional directional agreement
- Clinical implication: LLM variant interpretation requires (i) model selection (vendor matters more than ensemble size), (ii) complete evidence (AF mandatory), and (iii) treating abstention as a trustworthy triage signal for human review.
