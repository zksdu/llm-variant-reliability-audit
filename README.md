# LLM Variant Classification Reliability Audit

Code and data for: **"When Data Leakage Is Controlled: A Multi-Vendor Reliability Audit of LLM-Based ACMG/AMP Variant Classification"**

A temporally blinded, multi-vendor audit of large language models performing ACMG/AMP 2015 germline variant classification:

- **6 Chinese LLMs at full scale** (5,000 variants × 6 models = 30,000 evaluations): DeepSeek v4-pro / chat / coder, Kimi-K2.6, MiMo V2.5 Pro, Qwen3.7-max
- **3 international flagships** on an identical 500-variant subset (1,500 evaluations): Gemini 3 Flash, GPT-5.6-terra, Claude Sonnet 5
- Independent validation on **900 ClinGen expert-panel variants**
- Sub-experiments: allele-frequency ablation, conflicting-classification variants, MaveDB functional-effect task, output determinism, cost profiling, five-class analysis, surface-cue stratification

## Repository layout

```
scripts/    Full pipeline (pure Python 3 standard library)
  preprocess_clinvar.py          ClinVar parsing + temporal test-set construction
  rebuild_temporal.py            Reproducible temporal test set (seed 42)
  run_variant_classification.py  LLM experiments (concurrent, resumable)
  analyze_consensus.py           Dual-metric accuracy, consensus, gold-standard strata
  statistics_analysis.py         Wilson CI + McNemar tests
  annotate_af.py                 Allele-frequency annotation from ClinVar VCF
  extract_expert_panel.py        Expert-panel validation set
  extract_conflicting.py         Conflicting-classification set
  mavedb_sample.py               MaveDB functional test set
  cost_profiling.py              Token usage / cost audit
  generate_figures.py            All manuscript figures (300 dpi PNG + PDF)
data/       Test sets, gold standards, and all raw results (CSV)
docs/       Manuscript drafts, analyses, figures
```

## Reproduction

```bash
# 1. Download public inputs (see Data sources)
# 2. Build the temporal test set (byte-reproducible, seed 42)
python scripts/rebuild_temporal.py
# 3. Run models (requires API keys via .env; never committed)
python scripts/run_variant_classification.py --input data/clinvar_testset_temporal.csv \
    --models deepseek-chat --out data/results.csv
# 4. Analysis
python scripts/merge_results.py && python scripts/analyze_consensus.py \
    --results data/variant_classification_results_all.csv
python scripts/statistics_analysis.py
python scripts/generate_figures.py
```

## Data sources (all public)

| Resource | Source |
|---|---|
| ClinVar variant_summary | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz |
| ClinVar VCF (GRCh38, AF_ESP/EXAC/TGP) | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz |
| MaveDB (Ensembl-mapped) | https://ftp.ensembl.org/pub/current_variation/MaveDB/MaveDB_variants.tsv.gz |
| Gene symbols | mygene.info API |

Large raw files (>100 MB) are not committed; download via the URLs above.

## Key results

See `docs/manuscript_draft_EN.md` (full manuscript), `data/consensus_analysis.md`,
`data/statistics_analysis.md` for complete tables. Headline numbers are
reproducible end-to-end from the raw CSVs in `data/` (verified: sampling is
byte-reproducible at seed 42; the full analysis pipeline reproduces every
table and figure from the committed CSVs).
