# 专用完全盲集分析（n=2,000；LastEvaluated ≥ 2026-04；seed 42）

运行：2026-09，3 国际模型 × 2,000（P 1,000 / B 1,000），AF 关闭，研究语境 system prompt。
金标准来自结果内联 prompt_class 列（AlleleID 空值说明见文件头）。

| 模型 | 全对全 (95%CI) | 条件 | 弃权 | FP(B→P) | P敏感 | B敏感 | 解析失败 |
|---|---|---|---|---|---|---|---|
| gemini-3-flash | 81.4% [79.6,83.0] | 96.6% | 15.7% | 5.2% | 92.4% | 70.4% | 1 |
| claude-sonnet-5 | 80.2% [78.3,81.8] | 96.5% | 17.0% | 4.3% | 92.0% | 68.3% | 0 |
| gpt-5.6-terra | 64.7% [62.6,66.8] | 83.7% | 22.7% | 25.0% | 96.6% | 32.8% | 58 |

## 无配对双比例检验（z，双侧）

- 全对全 gemini-3-flash vs claude-sonnet-5: z=1.00, p=0.3158
- FP gemini-3-flash vs claude-sonnet-5: z=0.95, p=0.3441
- 全对全 gemini-3-flash vs gpt-5.6-terra: z=11.90, p=0
- FP gemini-3-flash vs gpt-5.6-terra: z=-12.37, p=0
- 全对全 claude-sonnet-5 vs gpt-5.6-terra: z=10.93, p=0
- FP claude-sonnet-5 vs gpt-5.6-terra: z=-13.09, p=0

## 结论要点

1. Gemini 与 Claude 统计不可区分（全对全与 FP 均 n.s.）——Gemini 的全集领先在完全盲下不复存在。
2. GPT-5.6-terra 显著落后（p<1e-30）且为激进异常值（FP 25.0%、B 敏感 32.8%）。
3. Gemini 的 FP 行为跨运行不稳定：8 月主运行 ≥2026-04 分层 22.1% vs 本次专用集 5.2%（同为完全盲、同为中转端点）——与其已记录的非确定性及中转版本漂移一致；Claude 保守画像跨所有估计稳定（3.9–4.5%）。