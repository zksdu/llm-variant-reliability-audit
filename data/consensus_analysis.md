# 共识分析结果（LLM 变异分类）

数据: 100 变异 × 3 模型

## 1. 准确率（二分类 P/B）

| 方法 | 金标准 | 准确率 | 正确/总数 |
|---|---|---|---|
| deepseek-v4-pro | 全体 | 59.0% | 59/100 |
| | 金A严 | 100.0% | 1/1 |
| | 金A宽 | 46.4% | 26/56 |
| deepseek-chat | 全体 | 50.0% | 50/100 |
| | 金A严 | n/a |
| | 金A宽 | 35.7% | 20/56 |
| deepseek-coder | 全体 | 49.0% | 49/100 |
| | 金A严 | n/a |
| | 金A宽 | 33.9% | 19/56 |
| **3 模型共识** | 全体 | 49.0% | 49/100 |
| | 金A严 | n/a |
| | 金A宽 | 33.9% | 19/56 |
| 共识+弃权（排除 0 分歧） | 全体 | 49.0% | 49/100 |

> 金A严 = ReviewStatus∈{expert panel, practice guideline}；金A宽 = 金A严 ∪ {multiple submitters, no conflicts}。

## 1b. 明确表态时的准确率（排除 VUS 弃权）

| 方法 | 表态数/100 | 准确率 | 正确/总数 |
|---|---|---|---|
| deepseek-v4-pro | 68 | 86.8% | 59/68 |
| deepseek-chat | 50 | 100.0% | 50/50 |
| deepseek-coder | 49 | 100.0% | 49/49 |
| **3 模型共识** | 49 | 100.0% | 49/49 |

> 明确表态 = 模型未输出 VUS（Uncertain significance）；VUS 视为模型弃权。

## 1c. 混淆矩阵（3 模型共识 vs 金标准）

|  | 金标准=P | 金标准=B |
|---|---|---|
| 模型=P | 44 | 0 |
| 模型=B | 0 | 5 |
| 模型=VUS | 4 | 47 |

> 敏感度/特异度、F1 等指标待全量数据后补充。


## 2. 共识错误的案例

- 142201: 共识=Uncertain significance 金标准=Benign
- 256446: 共识=Uncertain significance 金标准=Benign
- 1648511: 共识=Uncertain significance 金标准=Benign
- 2828605: 共识=Uncertain significance 金标准=Benign
- 195656: 共识=Uncertain significance 金标准=Pathogenic
（共 51 个错误）

## 3. 校准（置信度 vs 准确率）

- deepseek-v4-pro: 平均置信度 0.74
- deepseek-chat: 平均置信度 0.78
- deepseek-coder: 平均置信度 0.78

> 注：Brier score 等严格校准指标待全量数据后补充

## 4. 时间盲法对照（泄漏控制）

> 测试集全部为 2026-01 后评估（模型截止 2025-12 之后），即全部为泄漏控制样本。
> 与 2025 前评估样本的对比需补充非时间盲法子集。
