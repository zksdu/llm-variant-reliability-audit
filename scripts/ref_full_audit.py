# -*- coding: utf-8 -*-
"""ref_full_audit.py — 参考文献逐字段审计（Crossref/arXiv 权威元数据比对）

对 manuscript_JGG.md 的每条引用：取 Crossref/arXiv 权威元数据，
逐字段比对（第一作者姓氏、年份、标题、期刊、卷、页/文章号）。
"""
import json
import re
import urllib.request

MD = r'D:\0806\Bioinformatics_Paper_Project\docs\manuscript_JGG.md'
UA = {'User-Agent': 'ref-audit/1.0 (mailto:audit@local)'}


def crossref(doi):
    req = urllib.request.Request(f'https://api.crossref.org/works/{doi}', headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=25))['message']


def arxiv(aid):
    req = urllib.request.Request(f'http://export.arxiv.org/api/query?id_list={aid}', headers=UA)
    x = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')
    title = re.findall(r'<title>(.*?)</title>', x, re.S)
    authors = re.findall(r'<name>(.*?)</name>', x, re.S)
    published = re.findall(r'<published>(\d{4})', x)
    return {'title': title[1].strip() if len(title) > 1 else '?',
            'authors': authors, 'year': published[0] if published else '?'}


def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower())


def check(label, cited, meta, fields):
    """fields: {字段名: (引用值, 权威值)}"""
    print(f'--- {label}')
    for k, (cv, mv) in fields.items():
        if mv is None:
            print(f'    {k}: 引用[{cv}] 权威[无此字段]')
            continue
        ok = norm(str(cv)) == norm(str(mv)) if k == 'title' else str(cv).strip() == str(mv).strip()
        mark = 'OK' if ok else '*** 不一致 ***'
        print(f'    {k}: 引用[{cv}] vs 权威[{mv}] {mark}')


t = MD.read_text(encoding='utf-8')
refs = t[t.find('## References'):]

# ============ Crossref 系列（DOI） ============
cr_cases = [
    ('AI-CURA 2026', '10.1126/scitranslmed.adz4172',
     {'年份': ('2026', None), '标题': ('AI-CURA, an automated LLM workflow for high-accuracy genetic variant classification', None)}),
    ('Cheng 2023 AlphaMissense', '10.1126/science.adg7492',
     {'第一作者': ('Cheng', None), '年份': ('2023', None),
      '标题': ('Accurate proteome-wide missense variant effect prediction with AlphaMissense', None),
      '卷': ('381', None)}),
    ('Esposito 2019 MaveDB', '10.1186/s13059-019-1845-6',
     {'第一作者': ('Esposito', None), '年份': ('2019', None),
      '标题': ('MaveDB: an open-source platform to distribute and interpret data from multiplexed assays of variant effect', None),
      '卷': ('20', None), '页/文章号': ('223', None)}),
    ('Lin 2025 npj', '10.1038/s41698-025-00935-4',
     {'第一作者': ('Lin', None), '年份': ('2025', None), '卷': ('9', None), '文章号': ('141', None)}),
    ('Karczewski 2020 gnomAD', '10.1038/s41586-020-2308-7',
     {'第一作者': ('Karczewski', None), '年份': ('2020', None), '卷': ('581', None), '页': ('434-443', None)}),
    ('Landrum 2020 ClinVar', '10.1093/nar/gkz972',
     {'第一作者': ('Landrum', None), '年份': ('2020', None), '卷': ('48', None), '页': ('D835-D844', None)}),
    ('Rehm 2015 ClinGen', '10.1056/NEJMsr1406261',
     {'第一作者': ('Rehm', None), '年份': ('2015', None), '卷': ('372', None), '页': ('2235-2242', None)}),
    ('Richards 2015 ACMG', '10.1038/gim.2015.30',
     {'第一作者': ('Richards', None), '年份': ('2015', None), '卷': ('17', None), '页': ('405-424', None)}),
    ('Wu 2013 mygene', '10.1093/nar/gks1114',
     {'第一作者': ('Wu', None), '第二作者': ('MacLeod', None), '年份': ('2013', None), '卷': ('41', None), '页': ('D561-D565', None)}),
]

for label, doi, expect in cr_cases:
    try:
        m = crossref(doi)
        fams = [a.get('family', '?') for a in m.get('author', [])]
        year = (m.get('issued') or m.get('published-print') or m.get('published-online') or {}).get('date-parts', [[None]])[0][0]
        vol = m.get('volume')
        page = m.get('page') or m.get('article-number')
        fields = {}
        for k, (cv, _) in expect.items():
            if k == '标题':
                fields[k] = (cv, (m.get('title') or [None])[0])
            elif k == '第一作者':
                fields[k] = (cv, fams[0] if fams else None)
            elif k == '第二作者':
                fields[k] = (cv, fams[1] if len(fams) > 1 else None)
            elif k == '年份':
                fields[k] = (cv, year)
            elif k == '卷':
                fields[k] = (cv, vol)
            elif k == '页/文章号':
                fields[k] = (cv, page)
        check(label, doi, m, fields)
        print(f'    期刊: {m.get("container-title", ["?"])[0][:50]}')
    except Exception as e:
        print(f'--- {label}: 获取失败 {type(e).__name__}: {e}')

# ============ arXiv 系列 ============
ax_cases = [
    ('DeepSeek-AI 2024', '2412.19437', 'DeepSeek-AI', '2024', 'DeepSeek-V3 technical report'),
    ('Golchin 2023', '2308.08493', 'Golchin', '2023', 'Time Travel in LLMs: Tracing Data Contamination in Large Language Models'),
    ('Moonshot 2025', '2507.20534', 'Moonshot', '2025', 'Kimi K2: Open Agentic Intelligence'),
    ('Qwen 2025', '2505.09388', 'Qwen', '2025', 'Qwen3 technical report'),
    ('Saadat 2026', '2604.00075', 'Saadat', '2026', 'Large Language Models for Variant-Centric Functional Evidence Mining'),
    ('Sainz 2023', '2310.18018', 'Sainz', '2023', 'NLP evaluation in trouble: on the need to measure LLM data contamination for each benchmark'),
]
print()
for label, aid, fam, yr, ttl in ax_cases:
    try:
        m = arxiv(aid)
        ok_f = fam.lower() in ' '.join(m['authors']).lower()
        ok_t = norm(ttl) in norm(m['title']) or norm(m['title']) in norm(ttl)
        ok_y = m['year'] == yr
        print(f'--- {label}: 一作含"{fam}" {"OK" if ok_f else "*** 不一致 ***"} | 年份 {yr} vs {m["year"]} {"OK" if ok_y else "*** 不一致 ***"} | 标题 {"OK" if ok_t else "*** 标题不一致 ***: " + m["title"][:70]}')
        if label == 'Sainz 2023':
            print('    arXiv 作者全名:', m['authors'])
    except Exception as e:
        print(f'--- {label}: 获取失败 {e}')

# ============ Zenodo DOI（论文数据可用性声明） ============
print()
try:
    req = urllib.request.Request('https://api.zenodo.org/api/records/22264400', headers=UA)
    z = json.load(urllib.request.urlopen(req, timeout=25))
    md_ = z.get('metadata', {})
    print(f'--- Zenodo 10.5281/zenodo.22264400: 标题[{md_.get("title","?")[:70]}] | 状态[{z.get("state")}] | doi[{z.get("doi")}]')
except Exception as e:
    print(f'--- Zenodo 22264400 获取失败: {type(e).__name__}: {e}')
