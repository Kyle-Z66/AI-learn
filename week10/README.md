# 第 10 周：Rerank 重排

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第 10 周。
> **本周严格限定在第 10 周**：cross-encoder 精排、延迟预算与降级；评测体系是第 12 周。

## 一、学习目标（文档原文四任务）

> 首阶段用 bi-encoder 快速召回，二阶段用 cross-encoder 精排。
> 关键不是"接上模型"，而是**理解它的延迟代价与适用边界**。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | **Rerank 原理**：bi vs cross | `core_mechanisms/01`、`02` |
| 工作日 4h | **延迟成本意识**：50 个 ~310ms，100 个 ~590ms | `core_mechanisms/03`、`08`、`pitfalls/` |
| 周末 8h | **接入 + 效果对比**：Top-50 → Top-5 | `engineering/`、`rerank_lab/` |

验收口径：Top-50 → Top-5；超时降级有单测覆盖；纯向量/混合/混合+rerank 三方对比。

## 二、与前周的衔接（覆盖已掌握内容，不重复讲解）

| 已掌握 | 第 10 周如何使用（不再重复讲解） |
| --- | --- |
| 第 9 周混合检索 / RRF | 作为首阶段候选来源，不重讲 BM25 / 向量融合原理 |
| 第 8 周向量召回 | bi-encoder 侧只复用 `DenseIndex` 与 `HashEmbedding`，不重写向量库 |
| 第 5 周熔断 / 降级链 | 只做轻量三态状态示意，不复制 week05 文件；思路与 Java Redis/WebSocket 降级同构 |
| 第 4 周 `gather` / `Semaphore` | `06_batch_rerank.py` 复用并发经验，限制精排在途数量 |
| 第 7 周切分 | 语料已切好，本周只消费 candidate 文本 |

> **一句话递进**：第 9 周解决"有没有"，第 10 周解决"排得对不对"——
> 但每一步都要问：候选从哪来、超时怎么办、多花的延迟值不值。

## 三、任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | 原理与打分 | [`core_mechanisms/01`](core_mechanisms/) ~ [`02`](core_mechanisms/) |
| 工作日 4h | 预算 / 超时 / 熔断 / 并发 | [`core_mechanisms/03`](core_mechanisms/) ~ [`08`](core_mechanisms/) |
| 周末 8h | 效果指标 | [`core_mechanisms/09`](core_mechanisms/) ~ [`10`](core_mechanisms/) |
| 周末 8h | 工程化容错 | [`engineering/`](engineering/) —— reranker / fallback / 结果模型 |
| 周末 8h | 对比实验 | [`rerank_lab/`](rerank_lab/) —— Top-50 → Top-5 与真实输出 |

## 四、知识点对照表（文档原有 vs 补足）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| bi vs cross | `01_bi_vs_cross.py` | 文档给了定性描述 → **补足**两阶段对照表与职责边界 |
| cross-encoder 打分 | `02_rerank_score.py` / `reranker.py` | 文档点名模型 → **补足**确定性教学替身，避免下载模型 |
| 候选预算 | `03_candidate_budget.py` | 文档给了数字 → **补足**交互式/离线两种预算函数 |
| 超时降级 | `04_timeout_fallback.py` / `fallback.py` | 文档给了代码骨架 → **补足** `degraded`/`reason` 标记供指标统计 |
| 熔断复用 | `05_breaker_reuse.py` | 文档只做类比 → **补足**轻量三态示意，时钟可注入 |
| 批量并发 | `06_batch_rerank.py` | 文档未提 → **补足** gather + Semaphore，保序且限流 |
| Top-K 选择 | `07_topk_selection.py` | 文档给了数字 → **补足** strict zip 对齐与同分兜底 |
| 延迟模型 | `08_latency_model.py` | 文档给了两点 → **补足**线性示意并标注教学假设 |
| 三方对比 | `09_three_way_compare.py` | 文档列在验收 → **补足**固定语料的可运行对比 |
| Recall / MRR | `10_rerank_metrics.py` | 文档点名两个指标 → **补足**可复现的 before/after 口径 |

### 补足的坑点

| 坑 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 超时拖垮请求 | `pitfalls/rerank_pitfalls.py` | 文档给了降级代码，没讲"为什么必须降级" |
| 候选过多延迟爆炸 | `pitfalls/rerank_pitfalls.py` | 延迟线性涨、收益递减，需要量化直觉 |
| 把 rerank 当召回 | `pitfalls/rerank_pitfalls.py` | 首阶段漏掉的文档精排找不回 |
| 先修检索再修生成 | `pitfalls/extra_gotchas.py` | 排错顺序错会浪费大量时间 |
| 降级链 Java 同构 | `pitfalls/extra_gotchas.py` | 把既有经验显式平移，降低认知成本 |

## 五、验收标准与本地验证

- [x] Top-50 → Top-5 精排链路 → `engineering/reranker.py`、`rerank_lab/`
- [x] 超时降级有单测覆盖 → `tests/week10/test_engineering.py`
- [x] 三方指标对比 → `rerank_lab/REPORT.md`（程序真实输出）
- [x] 函数级单测覆盖 → `tests/week10/`

```bash
.venv/Scripts/python.exe -m ruff check week10 tests/week10
.venv/Scripts/python.exe -m mypy week10 tests/week10
.venv/Scripts/python.exe -m pytest -q tests/week10
.venv/Scripts/python.exe -m week10.engineering.engineering_demo
.venv/Scripts/python.exe -m week10.rerank_lab
```

## 六、坑提醒

- **rerank 不能当召回**：候选集合在首阶段就定了，精排只改顺序。
- **超时必须降级**：返回首阶段 Top-K 并标记 `degraded`，请求不能失败。
- **候选不是越多越好**：交互式 30~50，批处理才上 100+。
- **指标分开报**：Recall 持平而 MRR 提升是正常现象，别混着讲。
- **别越界**：本周不做完整评测体系（第 12 周），不做生成 prompt（第 11 周）。
