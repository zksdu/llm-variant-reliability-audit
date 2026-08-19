# Results (Draft) — English Manuscript Section

> Working title: *When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification*
> Status: Draft for internal review. All numbers from final full-scale experiments (2026-08-06).

---

## 3. Results

### 3.1 Cohort and experimental scale

We evaluated **6 LLMs from 4 vendors** (DeepSeek: v4-pro, chat, coder; Moonshot: Kimi-K2.6; Xiaomi: MiMo V2.5 Pro; Alibaba: Qwen3.7-max) on a **temporally-blinded test set of 5,000 ClinVar variants** (all LastEvaluated ≥ 2026-01, i.e., after the training cutoff of every evaluated model). In total, **30,000/30,000** domestic and **15,000/15,000** international variant-model pairs completed successfully (4 initial parse failures were automatically retried). All analyses use binary Pathogenic vs. Benign evaluation with VUS treated as abstention (see Methods).

### 3.2 Headline accuracy: models that speak are almost always right

We report two complementary accuracy metrics: **all-inclusive accuracy** (VUS counted as errors; clinical usability) and **conditional accuracy given a definitive call** (VUS excluded; reliability of expressed opinions).

**Table 1. Performance on the temporally-blinded test set (n = 5,000 variants).**

| Model | Vendor | All-inclusive Acc. | Conditional Acc. (spoken) | Spoken n | Expert-panel Acc. (n=100) |
|---|---|---|---|---|---|
| Gemini 3 Flash | Google | **76.5%** | 84.3% | 4,538 | 91.0% |
| Qwen3.7-max | Alibaba | 71.6% | 96.4% | 3,714 | 86.0% |
| Claude Sonnet 5 | Anthropic | 68.5% | 97.0% | 3,532 | 90.0% |
| Kimi-K2.6 | Moonshot | 67.0% | 97.8% | 3,421 | 90.0% |
| MiMo V2.5 Pro | Xiaomi | 66.1% | 85.2% | 3,876 | 92.0% |
| DeepSeek V4-pro | DeepSeek | 61.8% | 81.2% | 3,806 | **93.0%** |
| GPT-5.6-terra | OpenAI | 60.3% | 86.9% | 3,469 | 92.0% |
| DeepSeek chat | DeepSeek | 49.4% | 98.6% | 2,504 | 69.0% |
| DeepSeek coder | DeepSeek | 49.2% | 98.7% | 2,494 | 68.0% |
| 6-model majority | — | 64.1% | 98.4% | 2,911 | 93.5% |

> Table 1 footnotes: All-inclusive accuracy = VUS counted as error (clinical usability); conditional accuracy = accuracy restricted to committed calls; expert-panel stratum = 100 variants within the test set whose labels were produced by expert panels (ClinGen VCEP / guideline committees). Wilson 95% CIs: Qwen [70.4, 72.9], Kimi [65.6, 68.2], MiMo [64.7, 67.4], V4-pro [60.5, 63.1], chat [48.0, 50.8], coder [47.8, 50.6]. Majority voting operates on the three-way (P/B/VUS) semantics; ties excluded (n=528).

**Finding 1 (Generation gap).** New-generation flagship models (Qwen3.7-max, Kimi-K2.6, MiMo V2.5 Pro, DeepSeek V4-pro) outperform the previous generation (DeepSeek chat/coder) by **+12.6 to +22.4 percentage points (pp)** in all-inclusive accuracy (all new-generation vs. previous-generation McNemar p ≤ 2.9×10⁻²⁰; Kimi vs. MiMo: p = 0.12, n.s.). The gap persists under the highest-confidence gold standard (expert-panel variants: 86–93% vs. 68–69%).

**Finding 2 (Conditional reliability is not universal — and error direction matters).** Conservative models (chat/coder/Kimi) achieve 97.8–98.7% conditional accuracy when they commit. In contrast, reasoning-style models (V4-pro: 81.2%; MiMo: 85.2%) commit more often (76–78% of variants) but their expressed calls are substantially less reliable. Crucially, the errors are directionally asymmetric: when a gold-standard Benign variant receives a definitive call, reasoning models call it **Pathogenic** far more often — V4-pro mislabels 28.4% and MiMo 22.3% of all Benign variants as Pathogenic, versus 1.3–1.4% (chat/coder) and 2.5% (Kimi); Qwen sits between at 4.7%. Six-model consensus restores FP to 1.8%. The property "when the model speaks, it is right" holds **only for conservative models**; for reasoning models, committing is frequent, less accurate, and biased toward the clinically dangerous direction (false Pathogenic).

![Figure 1](figures/fig1_model_performance.png)

*Figure 1. Multi-model performance on the temporally blinded test set: (a) dual-metric accuracy; (b) Benign→Pathogenic false-positive rates (log scale) — reasoning models mislabel 22–28% of Benign variants as Pathogenic.*

**Finding 3 (Majority voting can hurt).** Six-model majority voting (64.1% all-inclusive) underperformed the best single model (Qwen3.7-max, 71.6%; +7.5 pp) because the three DeepSeek votes — collectively the most conservative — dominate ties. Model *diversity and selection* matter more than ensemble size; however, when the ensemble agrees on a definitive call (2,911 variants), conditional accuracy reaches 98.4%.

### 3.2b Surface-cue stratification: how much performance is readable from the variant name?

HGVS protein notation can itself reveal the answer class: nonsense (p.Xxx###Ter) and frameshift (fs) notation in a haploinsufficient-gene context is near-diagnostic of pathogenicity (ACMG PVS1-like). We stratified gold-standard Pathogenic variants by the presence of such loss-of-function (LoF) surface cues in the variant name.

| Model | P sensitivity, cued (n=1,671) | P sensitivity, uncued (n=828) | Gap |
|---|---|---|---|
| DeepSeek chat | 98.5% | 67.8% | −30.7 pp |
| Kimi-K2.6 | 99.8% | 77.7% | −22.1 pp |
| Qwen3.7-max | 99.5% | 83.8% | −15.7 pp |

**Finding 4 (Part of headline accuracy is name-reading).** Two-thirds of gold-standard Pathogenic variants (1,671/2,499) carry an LoF cue directly in their name, and on these, every model is near-ceiling (98.5–99.8%) — performance achievable without gene-disease knowledge beyond recognizing the notation. On the 828 uncued variants (missense, synonymous, splice-region), sensitivity drops to 67.8–83.8%, still well above the 50% base rate — models retain genuine discriminative signal, but 16–31 pp weaker. Naive accuracy metrics conflate these two regimes; a reliability audit should report both strata. Qwen degrades least (−15.7 pp), consistent with its overall lead.

### 3.3 Independent gold standard: ClinGen expert-panel review

We constructed a dedicated validation set of **900 variants curated by expert panels** (ClinGen/clinical guideline committees; ReviewStatus = "reviewed by expert panel"; all re-evaluated between 2026-01 and 2026-07, P-side 645, B-side 252). Of these, 100 were also sampled into the main test set (Table 1, expert-panel stratum); to guarantee independence, Table S3 reports the **800 exclusive variants** (797 evaluable; P: 550, B: 247).

**Table 2. Expert-panel validation (n = 797 exclusive variants; 5 models).**

| Model | Vendor | All-inclusive | Conditional | Abstention | FP rate |
|---|---|---|---|---|---|
| Gemini 3 Flash | Google | **79.0%** | 85.4% | 7.4% | 36.4% |
| Kimi-K2.6 | Moonshot | 72.8% | 90.6% | 19.7% | 19.8% |
| GPT-5.6-terra | OpenAI | 69.5% | 84.7% | 17.9% | 36.4% |
| DeepSeek chat | DeepSeek | 42.9% | 95.0% | 54.8% | 7.3% |
| DeepSeek coder | DeepSeek | 43.3% | 94.8% | 54.3% | 7.7% |

> Claude Sonnet 5 excluded: all API calls returned 429 rate-limit errors on this set; no valid results obtained.

> Results on the full 900 (including the shared 100) are qualitatively identical: Kimi 74.7% / chat 45.7% / coder 46.0% (robustness check).

The vendor gap **widens** under the strongest gold standard (+29.9 pp for Kimi vs. chat, vs. +17.6 pp on the general test set), indicating that model choice has a *larger* clinical impact than generic benchmarks suggest. A "always-Pathogenic" baseline would score 69.0% on this P-enriched set; Kimi's 72.8% exceeds it, whereas DeepSeek's ~43% reflects abstention-driven loss rather than misclassification (conditional accuracy 94.8–95.0%).

### 3.4 Triangulation: evidence availability drives reliability

Three sub-experiments show that LLM reliability is governed by the *evidence available in the prompt*:

**(a) Allele-frequency (AF) ablation (n = 400 × 9 models Benign-enriched + 150 × 2 Pathogenic).** Adding population allele frequencies (AF_ESP/ExAC/1000G, from ClinVar VCF) to the prompt — the identical variants, models, and otherwise identical prompts — raised Benign sensitivity from 11.0% to 68.8% (chat, **+57.8 pp**), 10.7% to 68.3% (coder), and 43.4% to 81.5% (Kimi); abstention fell from 80% to 33% (chat) and all-inclusive accuracy roughly tripled (19.1%→66.5% for chat; 49.3%→80.8% for Kimi). **The systematic Benign abstention observed in the main experiment is primarily an information-deficit behavior, not model conservatism.** The effect is bidirectional: on a Pathogenic-enriched AF subset (n = 150 × 2), adding AF raised accuracy from 44.9% to 64.0% (chat, +19.1 pp) and 47.5% to 85.3% (Kimi, +37.8 pp), with abstention falling from ~50% to 15–36%. Evidence completeness governs reliability on both sides of the P/B axis.

The AF effect is consistent across all nine tested models (range +28.8 to +52.8 pp): chat 15.0→66.5%, coder 15.8→66.2%, Kimi 50.5→80.8%, Qwen 57.8→92.2%, Gemini 67.2→96.0%, GPT 37.5→90.2%, Claude 56.2→90.0%, V4-pro 35.5→71.5%, MiMo 44.8→80.2%.

**(b) Conflicting-interpretation variants (n = 300 × 2 models).** On variants where clinical submitters disagree (conflicting classifications), models spontaneously raise abstention by **+22.5 pp (Kimi)** and **+39.1 pp (chat)** compared with the main test set — despite the prompt containing no conflict information. LLMs exhibit evidence-grounded uncertainty calibration: they sense controversy.

**(c) Functional-effect task (MaveDB, n = 300 × 2 models).** On deep-mutational-scanning variants with extreme functional scores (loss-of-function: score ≤ −0.8; normal: score ≥ 0.5) but no clinical evidence, models abstain massively (73–93%) and conditional directional agreement ≈ chance (45–55%). LLMs have no capacity for *de novo* functional inference from protein sequence alone — and they know it (abstain rather than hallucinate).

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

### 3.5 Calibration

Mean self-reported confidence (0.73–0.80) did not track all-inclusive accuracy across models (e.g., chat: confidence 0.78 vs. accuracy 49.4%; Kimi: 0.73 vs. 67.0%). Confidence is calibrated *within* a model's decision style, not across models; reasoning models over-express confidence relative to their conditional accuracy (V4-pro: 0.79 vs. 81.2%; MiMo: 0.80 vs. 85.2%).

### 3.5b Five-class analysis: the "Likely" tier is absent

The ACMG/AMP framework is five-class (Pathogenic / Likely pathogenic / Uncertain significance / Likely benign / Benign), and P vs. LP carry different clinical follow-up (e.g., LP requires confirmation). On the expert-panel set (which carries five-class labels; P: 306, LP: 342, LB: 193, B: 59), **none of the evaluated models ever emitted a "Likely" class** — the five-class output collapses to three (P / VUS / B).

| Model | Exact five-class match | Likely-tier output | Cross-semantic errors (P↔B) |
|---|---|---|---|
| Kimi-K2.6 | 32.3% | 0/900 | 7.2% |
| DeepSeek chat | 22.4% | 0/900 | 2.1% |
| DeepSeek coder | 22.7% | 0/900 | 2.2% |
| Gemini 3 Flash | — | 646 LB/5,000 | 27.8% FP |
| Claude Sonnet 5 | — | 1,065 LB/5,000 | 3.9% FP |
| GPT-5.6-terra | — | 591 LB/5,000 | 17.9% FP |

> Note: International models were evaluated on the full 5,000-variant test set (not the 900-variant expert panel set); "LB" = Likely benign output. No model emitted Likely pathogenic (LP = 0 across all 15,000 international calls).

Strength polarization is systematic: 82% (Kimi) and 58% (chat) of gold-standard Likely pathogenic variants were escalated to Pathogenic; 51% of Likely benign were downgraded to Benign by Kimi. Two implications: (i) LLM outputs are usable at the binary-semantics level only — the "Likely" tier carries clinical information the models do not produce; (ii) reported high conditional accuracy on binary P/B evaluation is partly achieved *by* this collapse, which a five-class evaluation would not credit.

### Clinical risk stratification (Weighted Error Severity Index)

To quantify clinical harm, we computed a Weighted Error Severity Index (WESI): Benign-to-Pathogenic misclassification = weight 4 (unnecessary prophylactic surgery, cascade screening), Pathogenic-to-Benign = weight 4 (missed diagnosis), VUS abstention = weight 0 (safe deferral).

| Model | WESI | B-to-P (extreme) | Total extreme | Abstention |
|---|---|---|---|---|
| V4-pro | **0.585** | 711 (28.4%) | **716** | 23% |
| Gemini | **0.577** | 694 (27.8%) | **712** | 9% |
| MiMo | **0.460** | 557 (22.3%) | **573** | 22% |
| GPT | **0.363** | 448 (17.9%) | **454** | 31% |
| Qwen | 0.108 | 118 (4.7%) | 133 | 26% |
| Claude | **0.086** | 97 (3.9%) | **107** | 29% |
| Kimi | **0.060** | 63 (2.5%) | **74** | 32% |
| chat | **0.029** | 35 (1.4%) | **36** | 50% |
| coder | **0.026** | 32 (1.3%) | **33** | 50% |

**Finding 7 (A 22-fold clinical risk spectrum).** The safest (coder, 33 extreme events/5000) and most dangerous (V4-pro, 716 events) differ by 22x. Each B-to-P triggers 3-5 cascade tests in relatives. V4-pro's 711 false positives could affect 2100-3500 relatives. **For clinical deployment, model selection should prioritize WESI over raw accuracy.**

### 3.6 Output determinism (reproducibility audit)

Because a clinical system must return the *same* answer for the *same* variant, we re-ran 50 variants × 3 models under identical settings (temperature = 0, same prompt, same endpoint) and measured classification agreement with the original run.

**Table 3. Re-run consistency (n = 50 variants × 3 models).**

| Model | Exact-class agreement | Binary (P/B) agreement |
|---|---|---|
| DeepSeek chat | 50/50 (100.0%) | 50/50 (100.0%) |
| Kimi-K2.6 | 49/50 (98.0%) | 50/50 (100.0%) |
| Gemini 3 Flash | 40/50 (80.0%) | 44/50 (88.0%) |
| GPT-5.6-terra | 38/50 (76.0%) | 39/50 (78.0%) |
| DeepSeek V4-pro | 31/50 (62.0%) | **32/50 (64.0%)** |
| Claude Sonnet 5 | — | — |

![Figure 5](figures/fig5_determinism.png)

*Figure 5. (a) Re-run determinism at temperature 0; (b) collapse of the ACMG “Likely” tier (Kimi): gold Likely-pathogenic variants are polarized to Pathogenic, Likely-benign to Benign/VUS.*

> Cross-check: the 100 expert-panel variants shared between the main test set and the dedicated 900-variant set were classified twice in independent runs (same model, same prompt); agreement was chat 99/100, coder 100/100, Kimi 97/100 — consistent with the determinism ranking above.

**Finding 5 (Reasoning models are not deterministic — worsens with sample size).** At temperature = 0 (n = 200 per model), the determinism spectrum is: Kimi 96.0% > chat 92.5% > Claude 88.0% > Gemini 86.0% > GPT 78.0% > **V4-pro 40.0%**. Critically, the number of direct Benign↔Pathogenic flips (the clinically most consequential error direction): Kimi/chat/Claude = **0**, Gemini = 15, GPT = 10, **V4-pro = 79**. V4-pro changed its binary call on **60% of re-run variants** — at n = 50 this was estimated at 36%, but the larger sample reveals substantially worse non-determinism. Three models (chat, Kimi, Claude) never flip across semantic boundaries; their non-determinism is entirely VUS↔definitive shifts, which are clinically safe (changes abstention, not direction). Under a reliability-audit framing, non-determinism with cross-semantic flips is a first-class failure mode: **a model that returns contradictory clinical directions for the same input cannot be deployed regardless of its average accuracy.**

### 3.8 International extension: three foreign flagships at full scale

To test whether the domestic findings generalize across training ecosystems, we evaluated Gemini 3 Flash, GPT-5.6-terra, and Claude Sonnet 5 on the **complete temporally blinded test set** (5,000 variants each; identical prompts; research-context system prompt for all three; see Methods).

**Table 5. Nine-model comparison on the complete test set (n = 5,000 per model).**

| Model | Vendor | All-inclusive | Conditional | Abstention | Benign→Pathogenic FP | Expert-panel (n=100) |
|---|---|---|---|---|---|---|
| Gemini 3 Flash | Google | **76.5%** | 84.3% | 9.2% | 27.8% | 91% |
| Qwen3.7-max | Alibaba | 71.6% | 96.4% | 25.7% | 4.7% | 86% |
| Claude Sonnet 5 | Anthropic | 68.5% | 97.0% | 29.3% | **3.9%** | 90% |
| Kimi-K2.6 | Moonshot | 67.0% | 97.8% | 31.6% | 2.5% | 90% |
| MiMo V2.5 Pro | Xiaomi | 66.1% | 85.2% | 22.5% | 22.3% | 92% |
| DeepSeek V4-pro | DeepSeek | 61.8% | 81.2% | 23.9% | 28.4% | 93% |
| GPT-5.6-terra | OpenAI | 60.3% | 86.9% | 30.6% | 17.9% | 92% |
| DeepSeek chat | DeepSeek | 49.4% | 98.6% | 49.9% | 1.4% | 69% |
| DeepSeek coder | DeepSeek | 49.2% | 98.7% | 50.1% | 1.3% | 68% |

![Figure 6](figures/fig6_nine_model.png)

*Figure 6. Nine-model comparison on the complete test set.*

**Finding 6 (The domestic findings generalize — and sharpen — internationally).** Three observations extend beyond the Chinese ecosystem. (i) **Gemini 3 Flash leads all nine models** (76.5% [75.3–77.7], +4.9 pp over the best domestic model; McNemar p = 1.7×10⁻¹³) with the lowest abstention (9.2%) — but pays for it with a 27.8% false-positive rate on Benign variants, placing it squarely in the *aggressive* camp with V4-pro (28.4%) and MiMo (22.3%). (ii) **Claude behaves as a conservative model**: 97.0% conditional accuracy with 3.9% FP — an order of magnitude below the aggressive camp and closest to Kimi's (2.5%; Fisher exact p = 0.008, distinguishable but both single-digit), and it exceeds Kimi in all-inclusive accuracy (p = 2.7×10⁻³) while sitting below Qwen (p = 3.0×10⁻¹⁵). On the independent expert-panel set (Table 2), the same dichotomy sharpens: Gemini and GPT both show 36.4% false-positive rates (vs. Kimi 19.8% and chat/coder 7–8%), confirming that the aggressive/conservative split holds under the strongest gold standard across ecosystems. The conservative/aggressive dichotomy of Finding 2 is thus a property of model *behavior*, not vendor nationality. (iii) **GPT-5.6-terra trails its foreign peers** (60.3%, significantly below Qwen: McNemar p = 4.7×10⁻⁹⁰) and sits below every current-generation domestic model — capability tracks neither nationality nor presumed price tier, reinforcing the audit's central message that model choice must be made on measured, blinded evidence rather than vendor reputation.

**Cross-ecosystem note: the "Likely" tier survives on the benign side only.** Unlike the six domestic models — which *never* emit a "Likely" class (§3.5b) — all three foreign models use "Likely benign": Claude 1,065/5,000 (21.3%), Gemini 646/5,000 (12.9%), GPT 591/5,000 (11.8%). Strikingly, **not one foreign model ever emitted "Likely pathogenic" (0/15,000 calls)** — strength information survives only on the benign side, while the pathogenic side polarizes to full "Pathogenic" in every ecosystem. The five-class collapse is therefore asymmetric and partially ecosystem-dependent, with direct consequences for clinical workflows that distinguish Pathogenic from Likely pathogenic follow-up.

> Note: foreign-model results are obtained via an OpenAI-compatible relay with a research-context system prompt (disclosed in Methods and Limitations); a prompt-robustness check is reported below.

### Prompt-asymmetry robustness check (full-scale, n = 5,000)

Qwen3.7-max was re-evaluated on the complete test set with the same system prompt used for international models. The prompt shifts Qwen conservative: accuracy 71.6-to-65.5% (-6.2 pp), abstention +8.1 pp, FP 4.7-to-1.0%. Binary agreement 100%. Under unified prompt: Gemini 76.5% (FP 27.8%), Claude 68.5% (FP 3.9%), Qwen 65.5% (FP 1.0%). The conservative/aggressive dichotomy persists; Qwen's original accuracy was slightly inflated relative to prompted international models.

### Foreign-model determinism

## Appendix (internal): key numbers cross-check

- 6 LLMs × 4 vendors × 5,000 temporally-blinded variants = 30,000 evaluations
- Best model (Qwen3.7-max): 71.6% all-inclusive; up to 93.0% on expert-panel gold standard (V4-pro)
- Conditional accuracy when committing: 81.2–98.7%; Benign→Pathogenic FP: 1.3–2.5% (conservative) vs 22–28% (reasoning)
- AF addition: Benign sensitivity +57.8 pp (11%→69%); all-inclusive accuracy ×3 (19%→67%)
- Expert disagreement: models raise abstention +22–39 pp without being told
- No-evidence (functional) task: 73–93% abstention; ≈50% conditional directional agreement
- Clinical implication: LLM variant interpretation requires (i) model selection (vendor matters more than ensemble size), (ii) complete evidence (AF mandatory), and (iii) treating abstention as a trustworthy triage signal for human review.
