# Rerank 动手实验室（week10/rerank_lab）

> 教学模拟电网/运维知识库，全部数据在本地构造，不接真实系统、不需要 API Key。

## 一、这个实验室回答什么问题

第 9 周把候选召回准了，但 Top-50 里正确文档可能排在第 20 位。
本实验用确定性教学版 reranker 做二阶段精排，对比三条链路：

1. 纯向量检索（第 8 周）
2. 混合检索 + RRF（第 9 周）
3. 混合检索 + rerank（第 10 周）

## 二、运行方式

```bash
python -m week10.rerank_lab
python -m week10.rerank_lab > week10/rerank_lab/REPORT.md
```

## 三、文件职责

| 文件 | 职责 |
| --- | --- |
| `corpus.py` | 15 条模拟 chunk + 6 条带相关标注的查询（独立复制语料思想） |
| `__main__.py` | 三路召回、Recall@5 / MRR@5 对比表、分组均值 |
| `REPORT.md` | 程序真实运行输出 |

## 四、实验口径

- 候选预算 50；教学语料 15 条，实际候选数 `min(50, 15)`。
- 输出 Top-5；三路共用 `dept` / `valid` 前置过滤与同一批查询。
- 打分复用第 9 周 tokenizer + 专名精确命中加成，确定性、可复现。
- 延迟只做数量级示意（见 `core_mechanisms/08_latency_model.py`），不进指标。
- 超时降级链在 `engineering/fallback.py` 与 `core_mechanisms/04` 验证。

## 五、预期观察

- Recall@5：rerank 与混合检索通常持平——候选集合没变，漏掉的找不回来。
- MRR@5：rerank 把相关文档提前，数值应更好。
- 结论边界：先修检索（第 9 周），再谈精排；完整评测在第 12 周。

真实结果见 [`REPORT.md`](REPORT.md)。
