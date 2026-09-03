# JGG Editorial Manager 投稿操作指引（终版 2026-09-04）

> 入口：https://www.editorialmanager.com/JGG
> 打不开时挂系统代理（127.0.0.1:3067）。本指引已对齐终稿（含 15 轮审计与两轮外部审查后的全部修订）。

---

## 〇、投稿前唯一待办（5 分钟）

GitHub 发 **v1.2.0** Release 换新 DOI：

1. 打开 https://github.com/zksdu/llm-acmg-variant-audit/releases/new
2. **Choose a tag** 输入 `v1.2.0` → 选 "Create new tag: v1.2.0 on publish"
3. 标题：`v1.2.0 — dedicated blinded-set revision`
4. 描述：`Adds dedicated fully blinded set (n=2,000) evaluation, cutoff disclosures, and final review fixes.`
5. Publish → 1-2 分钟后到 https://zenodo.org/account/settings/github/ 取新 DOI → **发给助手替换**，等 docx 重建完成后再投稿。
   （若决定沿用 DOI 10.5281/zenodo.22281813 也可直接投，但快照对应 v1.1.0，与终稿有差异。）

---

## 一、注册（约 5 分钟，只需一次；已注册可跳过）

1. 打开 https://www.editorialmanager.com/JGG → **Register Now**
2. ⚠️ 姓名顺序是常见坑：**First/Given Name**: `Kai`；**Last/Family Name**: `Zhang`
   - E-mail: `zhangkai@gdcp.edu.cn`
   - Institution: `Guangdong Communication Polytechnic`
   - Country: `China`
3. 验证邮件激活（收不到看垃圾箱；被拦截则加白名单 editorialmanager.com 重发）
4. ORCID 可选，无账号可跳过

---

## 二、投稿（约 15 分钟）

登录 → **Author Main Menu → Submit New Manuscript**

### 1. Article Type
**Research Article**

### 2. 逐项填写（全部可直接复制）

| 字段 | 填写内容 |
|---|---|
| Title | `Multi-vendor evaluation of large language models for ACMG/AMP variant classification with controlled data contamination` |
| Running title | `Multi-vendor LLM Variant Classification` |
| Abstract | 从 `docs/submission_package.md` 复制（191 词，与 docx 逐字一致；先在本地粘贴好再粘进表单，防登出）|
| Keywords（系统若让逐个添加，共 7 个）| `variant classification` / `ACMG/AMP` / `large language models` / `data leakage` / `ClinVar` / `reliability audit` / `temporal blinding` |
| **Personal Keywords（单独栏目，限 5 个）** | `variant classification` / `ACMG/AMP` / `large language model` / `ClinVar` / `artificial intelligence` |
| Authors | 系统默认张凯（通讯）；**手动添加第一作者 Bing Song 置顶**（First: `Bing`，Last: `Song`，单位：The Third Affiliated Hospital of Guangzhou Medical University；邮箱用其本人邮箱）|
| Funding | No specific funding（或选无基金选项）|
| Conflict of Interest | No |
| Ethics | `Not applicable. This study uses only publicly available database records (ClinVar, ClinGen-derived review statuses, MaveDB); no human participants, patient material, or personal data were involved.` |
| Data availability | `All source data are publicly available (ClinVar, MaveDB, mygene.info). Test sets, gold standards, all 51,000 raw model outputs, and analysis scripts: https://github.com/zksdu/llm-acmg-variant-audit (DOI: 10.5281/zenodo.22281813 — 或 v1.2.0 新 DOI)` |

### 3. 上传文件（按顺序）

| # | 文件 | Role |
|---|---|---|
| 1 | `docs/submission_JGG.docx` | **Manuscript** |
| 2 | `docs/figures_v2/fig1.tiff` | Figure |
| 3 | `docs/figures_v2/fig2.tiff` | Figure |
| 4 | `docs/figures_v2/fig3.tiff` | Figure |
| 5 | `docs/figures_v2/fig4.tiff` | Figure |
| 6 | `docs/figures_v2/fig5.tiff` | Figure |
| 7 | Cover letter | 粘贴进 Cover Letter 文本框（`docs/submission_package.md` 的 Cover Letter 节全文）|

> - 图全部 600 dpi TIFF，超 JGG 的 300 dpi 要求；PDF 版备用于系统提示"矢量优先"时替换
> - 表格（Table 1 + S1–S4）与图注均在 Manuscript 内，无需单独上传
> - **不要**上传 `figures_jgg/`（旧版 4 图，已废弃）

### 4. Suggested Reviewers（选填，非强制）
可建议（均为论文引用的公开工作作者，无利益冲突）：
- VariantBench 作者（Basharat 等，IJCNLP-AACL 2025 SRW）
- Saadat & Fellay（EPFL，VarLitBench）
- AI-CURA 团队（香港基因组研究所）

### 5. 检查与提交
- **Build PDF** → 目检：图清晰度、9 张表格未乱、S4（专用盲集表）在位
- 确认 Title/Abstract 与 docx 一致（防表单缓存旧内容）
- **Submit** → 收确认邮件（稿件编号形如 JGG-D-26-XXXXX）

---

## 三、提交后

| 状态 | 含义 |
|---|---|
| Submitted / With editor | 已提交、编辑初审（JGG 通常 1–2 周）|
| Under review | 外审（1–3 个月）|
| Decision in process | 意见汇总中 |

**两件事**：
1. 任何编辑部邮件（修改/补充要求）直接转发助手处理
2. 校样阶段选 **online-only color**，规避印刷彩图费（$1,000 首图 + $300/后续图）

---

## 常见坑速查

- 验证邮件收不到 → 垃圾箱 / 重发 / 换浏览器
- 图模糊 → 确认传的是 .tiff 本体而非预览压缩图
- 15 分钟自动登出 → 长文本先在本地写好再粘贴
- 提交卡住 → 刷新重试（数据已暂存）
- 全程挂代理；GitHub/Zenodo 打不开多刷新

---

## 本地材料清单（全部就绪，均已过 101 项自动终检）

| 材料 | 位置 |
|---|---|
| Manuscript（含全部修订）| `docs/submission_JGG.docx` |
| 5 张图（tiff/pdf/png 三格式）| `docs/figures_v2/` |
| 标题页/摘要/声明/投稿信 | `docs/submission_package.md` |
| 验证脚本（投稿后任何人可复核）| 仓库 `scripts/final_gate.py` 等 |
