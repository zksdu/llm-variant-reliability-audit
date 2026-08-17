# 统计检验结果

可评定变异（金标准 P/B）: 4999

## 1. 全对全准确率（VUS=错）+ Wilson 95% CI

| 模型 | 准确率 | 95% CI |
|---|---|---|
| deepseek-v4-pro | 61.8% | [60.5%, 63.1%] |
| deepseek-chat | 49.4% | [48.0%, 50.8%] |
| deepseek-coder | 49.2% | [47.8%, 50.6%] |
| kimi-k2.6 | 67.0% | [65.6%, 68.2%] |
| mimo-v2.5-pro | 66.1% | [64.7%, 67.4%] |
| qwen3.7-max | 71.6% | [70.4%, 72.9%] |
| gemini-3-flash | 76.5% | [75.3%, 77.7%] |
| claude-sonnet-5 | 68.5% | [67.2%, 69.8%] |
| gpt-5.6-terra | 60.3% | [58.9%, 61.7%] |

## 2. McNemar 配对检验（行模型 vs 列模型，p 值）

| 对比 | p 值 | 显著 |
|---|---|---|
| qwen3.7-max vs deepseek-chat | 2.43e-214
| qwen3.7-max vs kimi-k2.6 | 2.94e-20
| kimi-k2.6 vs deepseek-chat | 6.78e-166
| deepseek-v4-pro vs deepseek-chat | 1.55e-86
| mimo-v2.5-pro vs deepseek-chat | 1.08e-141
| kimi-k2.6 vs mimo-v2.5-pro | 1.15e-01
| gemini-3-flash vs qwen3.7-max | 1.74e-13
| claude-sonnet-5 vs qwen3.7-max | 3.02e-15
| gpt-5.6-terra vs qwen3.7-max | 4.73e-90
| claude-sonnet-5 vs kimi-k2.6 | 2.72e-03
| gpt-5.6-terra vs deepseek-v4-pro | 9.36e-03

## 3. 共识 vs 最佳单模型（6 模型多数投票）

| 6 模型共识（全对全口径）| 64.1% | [62.7%, 65.5%] (n=4471) |
| 6 模型共识（表态口径）| 98.3% | [97.8%, 98.7%] (n=2915) |
| 最佳单模型（gemini-3-flash）| 76.5% | — |

> McNemar：n>30 正态近似（含连续性校正）；共识平票不计入。
