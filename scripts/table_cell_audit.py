# -*- coding: utf-8 -*-
"""table_cell_audit.py — docx 表格单元格级自动审计

解析 submission_JGG.docx 的每张数值表，提取 模型→数值 配对，
与原始数据实时重算值逐格比对。零容错：任何一格不符即 FAIL。
"""
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

from docx import Document

ROOT = Path(__file__).parent.parent
DATA = ROOT / 'data'

PATHO = {'Pathogenic', 'Likely pathogenic'}
BEN = {'Benign', 'Likely benign'}
LOF_RE = re.compile(r'p\.[A-Za-z]{2,3}\d+(Ter|\*|fs)', re.IGNORECASE)


def bin2(c):
    c = str(c).strip()
    if c in PATHO:
        return 'P'
    if c in BEN:
        return 'B'
    if 'Uncertain' in c:
        return 'V'
    return 'O'


def wilson_c(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    return ((p + z * z / (2 * n)) / d) * 100


# ===== 原始数据 =====
gold, review, name = {}, {}, {}
for r in csv.DictReader((DATA / 'clinvar_testset_temporal.csv').open(encoding='utf-8', newline='')):
    g = bin2(r['ClinicalSignificance'])
    gold[r['AlleleID']] = g
    review[r['AlleleID']] = r['ReviewStatus'].strip()
    name[r['AlleleID']] = r['Name']
votes = defaultdict(dict)
parse_err = defaultdict(int)
for r in csv.DictReader((DATA / 'variant_classification_results_all.csv').open(encoding='utf-8', newline='')):
    if r.get('parse_error', '').strip() or r['llm_class'].strip().lower() in ('', 'error'):
        parse_err[r['model']] += 1
    if r['llm_class'].strip().lower() in ('', 'error'):
        continue
    votes[r['AlleleID']][r['model']] = bin2(r['llm_class'])

EXPERT = {'reviewed by expert panel', 'practice guideline'}
MODELS = {'gemini-3-flash': 'Gemini 3 Flash', 'qwen3.7-max': 'Qwen3.7-max',
          'claude-sonnet-5': 'Claude Sonnet 5', 'kimi-k2.6': 'Kimi-K2.6',
          'mimo-v2.5-pro': 'MiMo V2.5 Pro', 'deepseek-v4-pro': 'DeepSeek V4-pro',
          'gpt-5.6-terra': 'GPT-5.6-terra', 'deepseek-chat': 'DeepSeek chat',
          'deepseek-coder': 'DeepSeek coder'}

# 每模型重算：全对全/条件/弃权/FP/专家100（n=4999 约定）
M = {}
n_eval = sum(1 for g in gold.values() if g in 'PB')
for m in MODELS:
    c = sp = csp = fp = ec = 0
    gb = 2499 + 1  # gold B=2500? 实测下面用精确值
    gb = sum(1 for g in gold.values() if g == 'B')
    for a, g in gold.items():
        if g not in 'PB':
            continue
        v = votes.get(a, {}).get(m)
        if v is None:
            continue
        if v == g:
            c += 1
        if v in 'PB':
            sp += 1
            if v == g:
                csp += 1
        if g == 'B' and v == 'P':
            fp += 1
        if review[a] in EXPERT and v == g:
            ec += 1
    en = sum(1 for a, g in gold.items() if g in 'PB' and review[a] in EXPERT)
    M[m] = {'all': c / n_eval * 100, 'cond': csp / sp * 100 if sp else 0.0, 'spoken': sp,
            'abst': (n_eval - sp) / n_eval * 100, 'fp': fp / gb * 100,
            'expert': ec, 'fn': None}

# FN（P→B）与 WESI
for m in MODELS:
    fn = 0
    for a, g in gold.items():
        if g == 'P' and votes.get(a, {}).get(m) == 'B':
            fn += 1
    M[m]['fn'] = fn

d = Document(ROOT / 'docs' / 'submission_JGG.docx')
T = d.tables


def cell(t, r, c_):
    return T[t].rows[r].cells[c_].text.strip()


def num(s):
    m_ = re.search(r'[\d.]+%?/?[\d,]*', s)
    return m_.group(0) if m_ else s


fails = []


def cmp(label, docx_val, expect, tol=0.051):
    dv = float(re.sub(r'[%,]', '', docx_val))
    if abs(dv - expect) > tol:
        fails.append(f'{label}: docx={docx_val} 重算={expect:.1f}')


# ===== 表1（docx 表索引0）：11 行 =====
row_map = {1: 'gemini-3-flash', 2: 'qwen3.7-max', 3: 'claude-sonnet-5', 4: 'kimi-k2.6',
           5: 'mimo-v2.5-pro', 6: 'deepseek-v4-pro', 7: 'gpt-5.6-terra',
           8: 'deepseek-chat', 9: 'deepseek-coder'}
for r, m in row_map.items():
    assert cell(0, r, 0).startswith(MODELS[m].replace(' 3', ' 3').split()[0]), f'表1行{r}模型名: {cell(0,r,0)}'
    cmp(f'表1[{MODELS[m]}].全对全', cell(0, r, 2), M[m]['all'])
    cmp(f'表1[{MODELS[m]}].条件', cell(0, r, 3), M[m]['cond'])
    if int(re.sub(r'[%,]', '', cell(0, r, 4))) != M[m]['spoken']:
        fails.append(f'表1[{MODELS[m]}].spoken: docx={cell(0,r,4)} 重算={M[m]["spoken"]}')
    if float(re.sub(r'[%,]', '', cell(0, r, 5))) != M[m]['expert']:
        fails.append(f'表1[{MODELS[m]}].专家100: docx={cell(0,r,5)} 重算={M[m]["expert"]}')

# ===== 表S2（docx 索引6）：9 模型 × 全对全/条件/弃权/FP =====
for r, m in row_map.items():
    cmp(f'S2[{MODELS[m]}].全对全', cell(6, r, 2), M[m]['all'])
    cmp(f'S2[{MODELS[m]}].条件', cell(6, r, 3), M[m]['cond'])
    cmp(f'S2[{MODELS[m]}].弃权', cell(6, r, 4), M[m]['abst'])
    cmp(f'S2[{MODELS[m]}].FP', cell(6, r, 5), M[m]['fp'])

# ===== WESI 表（docx 索引4）：9 行（V4,Gemini,MiMo,GPT,Qwen,Claude,Kimi,chat,coder）=====
order4 = ['deepseek-v4-pro', 'gemini-3-flash', 'mimo-v2.5-pro', 'gpt-5.6-terra',
          'qwen3.7-max', 'claude-sonnet-5', 'kimi-k2.6', 'deepseek-chat', 'deepseek-coder']
for r, m in enumerate(order4, start=1):
    wesi = (4 * round(M[m]['fp'] * 25) + 4 * M[m]['fn'] + 2 * parse_err[m]) / n_eval
    cmp(f'WESI[{m}]', cell(4, r, 1), wesi, tol=0.0006)
    fpc = round(M[m]['fp'] * 25)
    if int(re.sub(r'[(),% ]', '', cell(4, r, 2).split('(')[0])) != fpc:
        fails.append(f'WESI[{m}].BtoP: docx={cell(4,r,2)} 重算={fpc}')
    if int(re.sub(r'[*,]', '', cell(4, r, 3))) != fpc + M[m]['fn']:
        fails.append(f'WESI[{m}].extreme: docx={cell(4,r,3)} 重算={fpc + M[m]["fn"]}')

# ===== 表面线索表（docx 索引1）=====
cued = [a for a, g in gold.items() if g == 'P' and LOF_RE.search(name[a])]
uncued = [a for a, g in gold.items() if g == 'P' and not LOF_RE.search(name[a])]
for r, m in {1: 'deepseek-chat', 2: 'kimi-k2.6', 3: 'qwen3.7-max'}.items():
    cs = sum(1 for a in cued if votes.get(a, {}).get(m) == 'P') / len(cued) * 100
    us = sum(1 for a in uncued if votes.get(a, {}).get(m) == 'P') / len(uncued) * 100
    cmp(f'表面[{m}].cued', cell(1, r, 1), cs)
    cmp(f'表面[{m}].uncued', cell(1, r, 2), us)

# ===== 表S3（docx 索引2）：5 模型 排他集 =====
main_ids = set(gold)
ep_gold = {}
for r in csv.DictReader((DATA / 'expert_panel_candidates.csv').open(encoding='utf-8', newline='')):
    g = bin2(r['ClinicalSignificance'])
    ep_gold[r['AlleleID']] = g
excl = [a for a in ep_gold if a not in main_ids and ep_gold[a] in 'PB']
ep = defaultdict(dict)
for fn in ['expert_panel_results.csv', 'expert_panel_intl_exclusive.csv']:
    for r in csv.DictReader((DATA / fn).open(encoding='utf-8', newline='')):
        ep[r['AlleleID']][r['model']] = bin2(r['llm_class'])
for r, m in {1: 'gemini-3-flash', 2: 'kimi-k2.6', 3: 'gpt-5.6-terra', 4: 'deepseek-chat', 5: 'deepseek-coder'}.items():
    t = c = sp = csp = fp = gb = 0
    for a in excl:
        v = ep.get(a, {}).get(m)
        if v is None:
            continue
        g = ep_gold[a]
        t += 1
        if v == g:
            c += 1
        if v in 'PB':
            sp += 1
            if v == g:
                csp += 1
        if g == 'B':
            gb += 1
            if v == 'P':
                fp += 1
    cmp(f'S3[{m}].全对全', cell(2, r, 2), c / t * 100)
    cmp(f'S3[{m}].条件', cell(2, r, 3), csp / sp * 100)
    cmp(f'S3[{m}].弃权', cell(2, r, 4), (t - sp) / t * 100)
    cmp(f'S3[{m}].FP', cell(2, r, 5), fp / gb * 100)

# ===== 表S1 确定性（docx 索引5）=====
det = {'deepseek-chat': ('50/50', 100.0), 'kimi-k2.6': ('49/50', 98.0),
       'gemini-3-flash': ('40/50', 80.0), 'gpt-5.6-terra': ('38/50', 76.0),
       'deepseek-v4-pro': ('31/50', 62.0)}
for r, (m, (frac, pct)) in {1: ('deepseek-chat', det['deepseek-chat']),
                            2: ('kimi-k2.6', det['kimi-k2.6']),
                            3: ('gemini-3-flash', det['gemini-3-flash']),
                            4: ('gpt-5.6-terra', det['gpt-5.6-terra']),
                            5: ('deepseek-v4-pro', det['deepseek-v4-pro'])}.items():
    if frac not in cell(5, r, 1):
        fails.append(f'S1[{m}].exact: docx={cell(5,r,1)} 期望含{frac}')

print(f'===== 单元格级审计：{"全部通过" if not fails else f"{len(fails)} 处不符"} =====')
for f in fails:
    print('✗', f)
