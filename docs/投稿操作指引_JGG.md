# JGG Editorial Manager 注册与投稿操作指引

> 生成：2026-08-16。入口：https://www.editorialmanager.com/JGG
> 若打不开：开系统代理（Editorial Manager 服务器在国外，你本机代理 127.0.0.1:3067 浏览器会自动走）。

---

## 一、注册（约 5 分钟，只需一次）

1. 打开 https://www.editorialmanager.com/JGG
2. 点左上 **Register Now**（或 Register）
3. 填写（⚠️ 姓名顺序是常见坑）：
   - **First/Given Name**: `Bing`（名）
   - **Last/Family Name**: `Song`（姓）
   - **E-mail**: `songbing@gysy.com`（医院邮箱）
   - **Institution**: `The Third Affiliated Hospital of Guangzhou Medical University`
   - **Country**: `China`
   - 密码：自定（含大小写+数字，8 位以上）
4. 提交后系统发验证邮件到邮箱 → 点邮件里的激活链接
   （收不到看垃圾箱；被拦截则把 editorialmanager.com 加白名单重发）
5. 激活后用邮箱+密码登录

**ORCID**：系统可能提示关联 ORCID——可选。若无账号可跳过（不影响投稿）；
建议后续注册一个（orcid.org，免费），国内作者发表常用。

---

## 二、投稿（约 15 分钟）

登录后：**Author Main Menu → Submit New Manuscript（Submit an Article）**

### 1. Article Type
选 **Research Article**（JGG 的原创研究类型）

### 2. 逐项填写
| 步骤 | 填什么 |
|---|---|
| Title | `When data leakage is controlled: a multi-vendor reliability audit of LLM-based ACMG/AMP variant classification`（直接复制）|
| Abstract | 从 `docs/submission_package.md` 复制 182 词摘要 |
| Keywords | `variant classification; ACMG/AMP; large language models; data leakage; ClinVar; reliability audit; temporal blinding`（逐个添加）|
| Running title | `Reliability Audit of LLM Variant Classification` |
| Authors | 单作者（Bing Song），系统默认即通讯作者，无需添加他人 |
| Funding | 填 "No specific funding" 或选无基金选项 |
| Conflict of Interest | 选 No |

### 3. 上传文件（按顺序，都拖进上传区）
| 顺序 | 文件 | 设为 Role |
|---|---|---|
| 1 | `docs/submission_JGG.docx` | **Manuscript** |
| 2 | `docs/figures_jgg/fig1_JGG.pdf` | **Figure** |
| 3 | `docs/figures_jgg/fig2_JGG.pdf` | Figure |
| 4 | `docs/figures_jgg/fig3_JGG.pdf` | Figure |
| 5 | `docs/figures_jgg/fig4_JGG.pdf` | Figure |
| 6 | Cover letter（`docs/submission_package.md` 末段全文）| 粘贴进 Cover Letter 文本框 |

> 表格已在 Manuscript 内（含 Table 1/2 + S1-S3 清单），无需单独上传。
> 若系统要求图用 TIFF：`figures_jgg/` 里有同名 .tiff 备用。

### 4. Suggested Reviewers（如系统询问，选填）
可建议（均为论文引用的公开工作作者，无利益冲突）：
- VariantBench 作者（Basharat 等，ACL 2025）
- Saadat & Fellay（VarLitBench，EPFL）
- AI-CURA 团队（香港基因组中心）
不想填可留空——JGG 非强制。

### 5. 检查与提交
- **Build PDF**：系统把所有文件合成 PDF 供预览 → 打开目检一遍（重点看图清晰度、表格没乱）
- **Submit**：确认后提交 → 收到确认邮件（含稿件编号，形如 JGG-D-26-XXXXX）

---

## 三、提交后

| 状态 | 含义 |
|---|---|
| Submitted to journal | 已提交，等编辑分派 |
| With editor | 编辑初审中（JGG 较快，通常 1-2 周）|
| Under review | 外审中（1-3 个月）|
| Decision in process | 意见汇总中 |

**两件事记住**：
1. 收到任何邮件（要求修改/补充）直接转给我处理
2. 校样（proof)阶段选 **online-only color**，规避印刷彩图费（$1,000 + $300/图）

---

## 常见坑速查

- **验证邮件收不到** → 垃圾箱 / 重新发送 / 换浏览器
- **Build PDF 后图变模糊** → 确认传的是 PDF 版本（矢量），不是压缩过的预览
- **系统登出频繁** → 正常，15 分钟无操作自动登出，填长摘要先在本地写好粘贴
- **代理** → 投稿全程挂代理；提交按钮卡住就刷新重试（数据已暂存）
