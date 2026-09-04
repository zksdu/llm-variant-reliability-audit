# -*- coding: utf-8 -*-
"""临时修订脚本：专用盲集结果写入论文（用后即删）"""
import re

p = r'D:\0806\Bioinformatics_Paper_Project\docs\manuscript_JGG.md'
t = open(p, encoding='utf-8').read()

# 1. 完全盲评估段整体改写
old_block = t[t.find('**Fully blinded stratum (Table S4).**'):t.find('**Cross-ecosystem note')]
assert old_block, '盲分层段未找到'
new_block = '''**Fully blinded evaluation (Table S4).** Because the international models' cutoffs fall in early 2026, we evaluated them in two complementary fully blinded designs. First, on the main set's own \u2265 2026-04 slice (n = 907; P 753 / B 154; August run), the full-set ranking collapses to a three-way tie \u2014 Gemini 88.0% [85.7\u201389.9], Claude 87.1% [84.8\u201389.1], and the domestic leader Qwen 86.8% [84.4\u201388.8]; all pairwise McNemar p > 0.4. Second, on a **dedicated fully blinded set** \u2014 2,000 newly sampled variants (seed 42; 1,000 Pathogenic / 1,000 Benign; pool: 4,772 eligible alleles last evaluated \u2265 2026-04; 342 overlap with the main set; identical prompts; single session) \u2014 the international picture reorders. **Gemini and Claude are statistically indistinguishable** (81.4% [79.6\u201383.0] vs. 80.2% [78.3\u201381.8]; z = 1.0, p = 0.32), both pairing \u224896.5% conditional accuracy with FP rates of 4\u20135% \u2014 the conservative profile. **GPT-5.6-terra emerges as the aggressive outlier**: 64.7% all-inclusive (p < 10\u207b\u00b3\u2070 below both), 25.0% Benign\u2192Pathogenic FP, Benign sensitivity 32.8%, and 58/2,000 unparseable outputs. Gemini's full-set aggressive profile (FP 27.8%) does not persist under full blinding; its FP estimate also differs between the two blinded runs (22.1% on the August stratum vs. 5.2% on the September dedicated set), consistent with its documented non-determinism and possible relay-side version drift \u2014 reinforcing that relay-served rankings require blinded, repeated verification. Claude is the only international model whose profile is stable across every estimate (FP 3.9\u20134.5%). Across both blinded designs, no international model outperforms the best domestic models.

**Table S4. Dedicated fully blinded set (n = 2,000; LastEvaluated \u2265 2026-04; 1,000 P / 1,000 B; single session).**

| Model | All-inclusive (95% CI) | Conditional | Abstention | Benign\u2192Pathogenic FP |
|---|---|---|---|---|
| Gemini 3 Flash | 81.4% [79.6\u201383.0] | 96.6% | 15.7% | 5.2% |
| Claude Sonnet 5 | 80.2% [78.3\u201381.8] | 96.5% | 17.0% | 4.3% |
| GPT-5.6-terra | 64.7% [62.6\u201366.8] | 83.7% | 22.7% | 25.0% |

> Reference (August main-run stratum, n = 907): Gemini 88.0 / Claude 87.1 / Qwen 86.8, three-way tie.

'''
t = t.replace(old_block, new_block)

edits = [
    # 2. 摘要
    ('On a fully blinded stratum (n = 907; after every model\u2019s cutoff) no international model outperformed the best domestic models (Gemini 88.0%, Claude 87.1%, Qwen 86.8%, n.s.), while the conservative/aggressive error dichotomy persisted.',
     'On a dedicated fully blinded set (n = 2,000; all labels after every model\u2019s training cutoff), Gemini and Claude were statistically indistinguishable (81.4% vs. 80.2%; both \u224896.5% conditional, FP 4\u20135%), while GPT-5.6-terra fell to 64.7% with 25.0% false positives.'),
    # 3. Finding 6 (i)
    ("(i) **On the full set Gemini 3 Flash leads all nine models** (76.5% [75.3\u201377.7], +4.9 pp over the best domestic model; McNemar p = 1.7\u00d710\u207b\u00b9\u00b3) with the lowest abstention (9.2%) \u2014 but this comparison is not cutoff-controlled: on the fully blinded stratum the lead vanishes into a three-way tie with Claude and Qwen (Table S4), so it may partly reflect residual label exposure. Gemini pays for its output volume with a 27.8% false-positive rate on Benign variants, placing it squarely in the *aggressive* camp with V4-pro (28.4%) and MiMo (22.3%) \u2014 a dichotomy that survives full blinding (22.1%/27.3%/18.2% vs. 3\u20135%).",
     "(i) **On the full set Gemini 3 Flash leads all nine models** (76.5% [75.3\u201377.7], +4.9 pp over the best domestic model; McNemar p = 1.7\u00d710\u207b\u00b9\u00b3) with the lowest abstention (9.2%) \u2014 but this comparison is not cutoff-controlled: under full blinding the lead vanishes (statistical tie with Claude and Qwen; Table S4), so it may partly reflect residual label exposure. Nor does Gemini's full-set aggressive profile persist: on the dedicated blinded set its Benign\u2192Pathogenic FP is 5.2% (vs. 27.8% on the full set), placing it alongside Claude in the *conservative* camp \u2014 while GPT-5.6-terra emerges as the aggressive outlier (FP 25.0%)."),
    # 4. 讨论
    ("under full blinding the ranking collapses to a tie but the dichotomy persists (Table S4).",
     "under full blinding the ranking collapses to a tie, and camp assignment itself shifts \u2014 Gemini's aggressive profile dissolves (FP 5.2% blinded vs. 27.8% full-set) while GPT-5.6-terra becomes the aggressive outlier \u2014 behavior style remains the operative selection criterion, but it can change with label exposure and run conditions, detectable only by blinded, repeated evaluation (Table S4)."),
    # 5. Limitations (ii)
    ('(ii) **Cutoff overlap for international models**: Claude Sonnet 5, GPT-5.6-terra, and Gemini 3 Flash have training cutoffs of 2026-01 to 2026-03, so the 2026-01\u20132026-03 portion of the test set (41.9\u201381.9% depending on model) is not label-blinded for them; the fully blinded stratum (n = 907) shows Gemini\u2019s full-set lead is not robust to this control (Table S4), and all international accuracy comparisons should be read as cutoff-limited.',
     '(ii) **Cutoff overlap for international models**: Claude Sonnet 5, GPT-5.6-terra, and Gemini 3 Flash have training cutoffs of 2026-01 to 2026-03, so the 2026-01\u20132026-03 portion of the main test set (41.9\u201381.9% depending on model) is not label-blinded for them. Two fully blinded controls address this \u2014 the main-set \u2265 2026-04 stratum (n = 907) and a dedicated balanced set (n = 2,000) \u2014 both showing that Gemini\u2019s full-set lead and aggressive profile do not persist (Table S4). The two blinded runs also differ from each other for Gemini (FP 22.1% vs. 5.2%), consistent with relay non-determinism and possible version drift between sessions; international rankings should therefore be read as run-conditional.'),
    # 6. Methods
    ('International results are therefore reported both on the full set and on a **fully blinded stratum** (LastEvaluated \u2265 2026-04, n = 907), on which every model \u2014 domestic and international \u2014 is temporally blinded (International extension, Table S4).',
     'International results are therefore reported on the full set, on the in-set fully blinded stratum (LastEvaluated \u2265 2026-04, n = 907), and on a **dedicated fully blinded set** \u2014 2,000 variants (1,000 P / 1,000 B) sampled seed 42 from all eligible \u2265 2026-04 alleles (pool 4,772: P 2,611 / B 2,161; 342 overlap with the main set), evaluated with identical prompts in a single session (International extension, Table S4).'),
    # 7. 补充清单
    ('- **Table S4.** Fully blinded stratum, LastEvaluated \u2265 2026-04 (n = 907; all nine models cutoff-blinded).',
     '- **Table S4.** Dedicated fully blinded set, LastEvaluated \u2265 2026-04 (n = 2,000; three international models, single session).'),
    # 8. 数据可用性
    ('The temporally blinded test sets, gold standards, all 45,000 raw model outputs (4 parse-failure rows excluded from analysis), and analysis scripts are available at',
     'The temporally blinded test sets, gold standards, all 45,000 raw model outputs (4 parse-failure rows excluded from analysis), the dedicated fully blinded set and its 6,000 raw outputs, and analysis scripts are available at'),
]
for i, (o, n) in enumerate(edits, 1):
    assert o in t, f'第{i}处未找到: {o[:60]}'
    t = t.replace(o, n)

open(p, 'w', encoding='utf-8').write(t)
ma = re.search(r'## Abstract\n\n(.+?)\n\n## Introduction', t, re.S).group(1)
print('全部修订完成；摘要词数:', len(ma.split()))
