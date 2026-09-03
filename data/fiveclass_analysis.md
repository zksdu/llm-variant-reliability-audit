# 五分类混淆矩阵分析（专家评审 900 集）

**金标准五分类分布**：Pathogenic 306 / Likely pathogenic 342 / Likely benign 193 / Benign 59

## 关键发现

### 1. 模型从不输出 "Likely" 类别（核心发现）
三个模型的五分类输出中 "Likely" 类极少出现：Kimi 11/900（1.2%）、coder 4/900（0.4%）、chat 2/900（0.2%）（2026-09-03 复核修正）。
**LLM 的 ACMG 五分类输出实际上是三分类（Pathogenic / Uncertain / Benign）**，
强度信息（Likely 档）完全丢失。

### 2. 强度极化：Likely 被升级/降级
- 金标准 Likely pathogenic（342）：Kimi 82% 升级为 Pathogenic、chat 58% 升级
- 金标准 Likely benign（193）：Kimi 53% 降级为 Benign、14% 升为 Pathogenic（2026-09-03 从原始数据复核修正）
- 五分类精确匹配率：Kimi 32.3% / chat 22.4% / coder 22.7%
  （"低"主要是 Likely 档缺失所致）

### 3. 跨语义错误（P↔B 翻转）
- Kimi 7.2%（65/900，主要是把 LB/Benign 判成 P：53 例）
- chat 2.1% / coder 2.2%
- 注意：主测试集（纯 P/B 金标准）假阳性仅 0.6%——差异源于专家评审集
  含 Likely 类，模型对 Likely 边界变异极化到 P

## 临床含义
- P 与 LP 的临床随访策略不同（LP 需更多证据确认）——LLM 输出丢失
  Likely 档意味着强度信息不可靠，临床使用必须只依赖二分类语义
- "模型说 P" 在专家评审集上有 5.9% 概率金标准是 LB/Benign（Kimi）——
  高置信金标准下的小样本警示（n=900，其中 B/LB 只有 252）
