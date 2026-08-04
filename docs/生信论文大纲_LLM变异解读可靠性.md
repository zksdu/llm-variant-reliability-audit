# 生信论文大纲：LLM 变异解读的可靠性评估（数据泄漏控制）

> 创建日期：2026-08-04
> 方向：LLM + 生物信息学（变异解读 / ACMG-AMP 分类）
> 目标期刊：中科院 1 区（GPB / Briefings in Bioinformatics / Genome Medicine）
> 状态：设计阶段（实验未开始）

---

## 一、研究定位

### 标题（候选）
*When Data Leakage Is Controlled: A Multi-Model Reliability Evaluation of LLM-Based ACMG/AMP Variant Classification*

### 一句话
当训练数据泄漏被时间盲法控制后，10+ 个 LLM 的 ACMG/AMP 变异致病性分类还可靠吗？

### 为什么是空白（2026 现状）
- **顶刊已证明可行**：AI-CURA（DeepSeek-R1 做 ACMG 分类，96% 一致率）2026-06 发表于 *Science Translational Medicine*；ClinVar-BERT 发表于 *Genome Medicine* 2026
- **数据泄漏是公认但未解决的问题**：LLM 训练语料含 ClinVar/ClinGen，现有准确率数字不可解释为泛化能力
- **ClawBench（2026-06 bioRxiv）刚提出时间盲法框架，但没有跨模型结果**——空窗期

### 新颖性（审稿人买账的 5 点）
1. **时间盲法分割**：用模型训练截止后发布的 ClinVar 标签做真值，系统性控制泄漏（首个大规模结果）
2. **10+ 模型共识投票**：单模型 vs 多数投票的增益量化（现有研究仅小规模验证）
3. **每 ACMG 规则错误分类学**：PVS1/PS1/PM2/PP3 等逐规则错误分析
4. **证据编造检测**：LLM 引用验证（是否虚构文献/证据）
5. **每变异成本科学**：$ per classified variant 跨模型对比

---

## 二、研究问题（RQ）

| RQ | 问题 | 数据 | 方法 |
|----|------|------|------|
| RQ1 | 控制泄漏后，单模型 ACMG 分类准确率是多少？与未控制时差多少？ | 时间盲法 ClinVar 子集 | 时间分割 + 准确率对比 |
| RQ2 | 多模型共识投票能否提升准确率？增益多少？ | 10+ 模型 × 同变异 | 多数投票 vs 单模型 |
| RQ3 | LLM 在不同 ACMG 规则上的错误模式是什么？ | 逐规则错误 | 错误分类学 |
| RQ4 | LLM 会编造证据吗？频率多少？ | 引用验证 | 引文核实 |
| RQ5 | 不同模型的每变异成本与延迟如何？ | 调用记录 | 成本分析 |

---

## 三、数据源（全公开，零湿实验）

| 资源 | 内容 | 下载 |
|------|------|------|
| **ClinVar** | ~3.2M 变异，~1M 有临床分类 | ftp.ncbi.nlm.nih.gov/pub/clinvar/（variant_summary.txt.gz ~300MB）|
| **ClinGen** | ~4,000 专家精审变异（金标准子集）| ftp.clinicalgenome.org |
| **gnomAD v4.1** | 等位基因频率（PM2/BA1 规则 + 人群分层）| gnomad.broadinstitute.org |
| **AlphaMissense** | 非 LLM 基线 | Zenodo 8208688 |

### 时间盲法设计（核心）
- 取**模型训练截止日期之后**提交/发布的 ClinVar 标签作为真值（确保 LLM 训练时没见过答案）
- 用 RCV 提交日期而非 release 日期重建时间线（严谨性要求）
- 该子集即测试集；训练截止前的数据仅用于 prompt 上下文（不参与评估）

---

## 四、实验设计

### 模型面板（10+）
- **DeepSeek 全量**：V4-pro（主）、V4-flash
- **国外模型子集**（500 变异）：GPT、Claude、Gemini
- **国产开放模型**：Qwen、GLM、Kimi（若 API 可用）

### 流程（每变异）
1. 提取变异信息（基因/转录本/cDNA/蛋白变更 + gnomAD AF）
2. 构造 prompt（ACMG 规则 + 变异描述 + 人群频率）
3. LLM 输出分类 + 证据 + 引用
4. 与 ClinGen/ClinVar 金标准对照
5. 记录：分类、置信度、引用、耗时、成本

### 评估指标
- 准确率（泄漏控制前后对比）、一致性（Kappa）
- 共识增益（多数投票 vs 单模型）
- 逐规则错误率、证据编造率
- $ per variant、延迟

### 规模与成本（已确认预算 ~$2,000）
- 全量：~5,000 变异 × 10+ 模型（DeepSeek 全量）
- 子集：500 变异 × GPT/Claude/Gemini
- DeepSeek 侧 ~$200-800；国外模型 ~$1,000-2,000

---

## 五、可行性（单人 + 零 GPU）

- 纯 Python + pandas + API 调用（复用软件工程项目的 DeepSeek 基建）
- 可选：本地跑 1-2 个开放模型（消费级 GPU）做免费基线
- 周期 3-5 个月

---

## 六、风险与应对

| 风险 | 应对 |
|------|------|
| ClawBench 先发表 | 快速发 preprint + 侧重"共识/成本/错误分类学"等它没有的维度 |
| ClinVar 真值噪声（冲突提交）| 头衔结论只用 ClinGen 专家子集；ClinVar 仅用于规模 |
| "LLM 背答案"质疑 | 时间盲法本身就是贡献；严谨重建标签时间线 |
| API 基准确定性 | temperature=0 + 3 次运行 + 完整 prompt 透明 |
| 临床声明过强 | 框架为"决策支持审计"而非"临床验证"，伦理/局限章节必写 |

---

## 七、与软件工程论文的协同

- 共享方法论基因："LLM 在 X 任务上的失败模式/可靠性评估"
- 复用：DeepSeek API 调用（call_llm）、.env 配置、判定逻辑
- 第二篇可直接引用第一篇的方法论章节
- 投稿节奏可并行（软工篇 2026-08 底、生信篇 2026-12）

---

## 八、下一步（TODO）

- [ ] 下载 ClinVar variant_summary + ClinGen 数据
- [ ] 构建时间盲法测试集（需模型训练截止日期清单）
- [ ] 写数据预处理脚本（变异 → prompt 输入格式）
- [ ] 小规模验证（100 变异 × 3 模型，$20-50）
- [ ] 搭好后再扩全量

---

*大纲生成：2026-08-04。数据与成本数字基于 2026-08 调研，执行时以实际为准。*
