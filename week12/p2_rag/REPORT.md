# P2 RAG 效果评测报告（本地实跑）

> 数据来源：本仓库 `python -m week12.engineering.engineering_demo` 的输出抄录。
> golden_set.json 为**教学样例**（100 条，metadata 已标注来源），不是真实业务数据；
> 所有指标由 `week12.engineering.runner` 本地真实计算，未复制文档示意值。
> p95 延迟为本地单机教学测量（含检索 + 生成 + 引用组装），不代表线上 SLA。

## 一、运行环境与命令

```bash
python -m week12.engineering.engineering_demo
```

- 语料：20 个知识点片段 + 24 个同主题旧版归档干扰片段；
- 评测集：100 条教学样例，一问一片段，20 个知识点各 5 种问法；
- 生成侧：`FakeGenerator(temperature=0.1)`，四配置共用，答案逐字来自上下文；
- 所有排序与生成均为确定性本地实现，无网络、无 API Key。

## 二、四配置对比表（本次实跑数字）

| 配置 | Recall@5 | MRR@10 | Context Precision | Context Recall | Faithfulness | Answer Relevance | p95 延迟(ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bm25_only | 0.950 | 0.547 | 0.190 | 0.950 | 1.000 | 0.576 | 3.6 |
| dense_only | 0.950 | 0.424 | 0.190 | 0.950 | 1.000 | 0.571 | 3.1 |
| hybrid | 0.950 | 0.530 | 0.190 | 0.950 | 1.000 | 0.581 | 5.3 |
| hybrid_rerank | 0.900 | 0.509 | 0.180 | 0.900 | 1.000 | 0.559 | 6.1 |

## 三、逐案 Recall@5 分布（不看平均分盲区）

| 配置 | 最小 | 中位 | 最大 |
| --- | --- | --- | --- |
| bm25_only | 0.000 | 1.000 | 1.000 |
| dense_only | 0.000 | 1.000 | 1.000 |
| hybrid | 0.000 | 1.000 | 1.000 |
| hybrid_rerank | 0.000 | 1.000 | 1.000 |

均值掩盖了长尾：每个配置都有 5 条完全没召回的 case（归档干扰片段挤进 Top5），
中位数 1.000 说明大部分 case 正常。优化线索在最小值为 0 的那 5 条上。

## 四、CI 门禁示例

比较 `hybrid_rerank`（当前）与 `bm25_only`（基线），默认容差：质量 0.02 / 延迟 25ms。

- 结论：**回归**（`passed=False`，`exit_code=1`）；
- 退化项：`('recall_at_k', 'mrr', 'context_recall')`；
- Recall@5 变化：`-0.050`。

这正说明门禁的价值：它不关心"哪个配置名字更高级"，只看是否相对基线退化。

## 五、结果解读（诚实版）

1. **重排在本次教学语料上负收益**：hybrid+rerank 的 Recall@5 从 0.950 降到 0.900。
   原因是重排用"问题实词覆盖率 + 原文精确出现"，而归档干扰片段短、重复标注词，
   覆盖率反而更高。结论不是"重排没用"，而是"重排必须用评测验证，不能背结论"。
2. **MRR 差异比 Recall 大**：dense-only 0.424 最低，bm25-only 0.547 最高，
   说明四配置都能在 Top5 找到片段，但"排第几"差异明显；用户体验更吃 MRR。
3. **Faithfulness 全部 1.000 不等于答案全对**：它只证明"答案里的数字/实体在上下文里"，
   检索给错片段时照样 1.000。这正是"先修检索再修生成"的量化证据。
4. **Context Precision 约 0.190**：每条只标注 1 个相关片段、Top5 里只有 1 条相关，
   符合 1/5 的算术预期；提高它要靠更准的 Top-K，而不是改报告口径。
5. **延迟需分场景权衡**：本地测量里 hybrid_rerank 最高（6.1ms），dense-only 最低（3.1ms），
   绝对数值很小，只反映教学实现，不能当线上 SLA。

## 六、口径与边界

- Recall@5 分母是标注片段数；Context Precision 分母是 Top-K；MRR 只看首个命中。
- Faithfulness 无可核验声明时记 1.000；Answer Relevance 为实词覆盖率（教学版）。
- dense-only 是 TF-IDF 确定性替身，rerank 是纯函数，均非真实语义模型。
- 替换真实数据的步骤见 [`README.md`](README.md) 的"golden set：数据标注标准与替换步骤"。
