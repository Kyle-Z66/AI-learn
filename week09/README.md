# 第 9 周：混合检索（你的主场）

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第 9 周。
> **本周严格限定在第 9 周**：BM25 + 向量双路召回与融合；rerank 是第 10 周，评测体系是第 12 周。

## 一、学习目标（文档原文四任务）

> 你做过 ES 全文检索封装，这一周是最直接的能力平移：
> analyzer → tokenizer，bool filter → 前置过滤，多查询融合 → RRF。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | **为什么必须混合**：专名在语义空间漂移 | `core_mechanisms/01`、`pitfalls/extra_gotchas.py` |
| 工作日 4h | **融合算法**：RRF（k=60）与归一化加权 | `core_mechanisms/04`~`06`、`engineering/fusion.py` |
| 周末 8h | **双路召回**：BM25 + 向量 → RRF → Top-50 | `engineering/hybrid_retriever.py`、`hybrid_lab/` |

验收口径：能实现双路召回与 RRF、能用专名查询对比"纯向量 vs 混合"、
能讲清为什么 BM25 分数与 cosine 不能直接相加。

## 二、与前周的衔接（覆盖已掌握内容，不重复讲解）

| 已掌握 | 第 9 周如何使用（不再重复讲解） |
| --- | --- |
| 第 8 周 `HashEmbedding` / `InMemoryVectorStore` | 直接复用 `week08.engineering.vector_store.HashEmbedding`，向量库不重写；HNSW/IVF 不再展开 |
| 第 8 周标量过滤 | 过滤从"向量库的一个参数"升级为"两路召回前的统一闸门" |
| 第 7 周文档解析与切分 | 语料已切好；本周只消费 `Chunk` 形态的文本，不重新讲切分策略 |
| 第 5 周降级链 / 熔断 | 融合失败的降级思路与第 5 周同构；本周只建立"双路独立"意识，熔断代码不复制 |
| 第 4 周并发 | 本周两路召回串行执行即可，并发留到第 10 周 batch rerank 再展开 |

> **一句话递进**：第 8 周把"找相似"做通，第 9 周补上"找准确"——
> 专名靠 BM25、语义靠向量，融合阶段才比较，过滤阶段提前拦。

## 三、任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | 为什么混合 | [`core_mechanisms/01_why_hybrid.py`](core_mechanisms/01_why_hybrid.py)、[`pitfalls/`](pitfalls/) |
| 工作日 4h | 融合算法 | [`core_mechanisms/04`](core_mechanisms/) ~ [`10`](core_mechanisms/)、[`engineering/fusion.py`](engineering/fusion.py) |
| 周末 8h | 双路召回工程化 | [`engineering/`](engineering/) —— 双索引 + 融合 + `HybridRetriever` |
| 周末 8h | 专名查询实验 | [`hybrid_lab/`](hybrid_lab/) —— 15 条语料 / 10 条查询 / 真实输出报告 |

可运行知识点共 10 个，见 [`core_mechanisms/`](core_mechanisms/) 的 01~10；
全部样例 `python -m week09.core_mechanisms.XX_xxx` 直接运行，无网络、无 API Key。

## 四、知识点对照表（文档原有 vs 补足）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 专名向量漂移 | `01_why_hybrid.py` | 文档给了结论 → **补足**可运行玩具向量演示撞车 |
| BM25 路 | `02_bm25_scoring.py` / `bm25_index.py` | 文档只点名 `rank_bm25` → **补足**中英文混合 tokenizer |
| 向量路 | `03_dense_retrieval.py` / `dense_index.py` | 文档未展开 → 复用第 8 周嵌入，不重写向量库 |
| RRF（k=60） | `04_rrf_fusion.py` / `fusion.py` | 文档给了公式 → **补足**同分兜底排序与 k 稳定性对比 |
| 加权分数融合 | `05_weighted_fusion.py` | 文档点名需归一化 → **补足**权重翻转排序的可运行对比 |
| 量纲不可相加 | `06_normalization_trap.py` | 文档列在验收 → **补足**可直接打印的数字对照 |
| 查询扩写 | `07_query_rewrite.py` | 文档未提 → **补足**型号/错误码/缩写的确定性扩写 |
| 前置过滤 | `08_filter_and_fusion.py` | 文档只在第 8 周提标量过滤 → **补足**"融合后过滤会少一条"复现 |
| Recall@K | `09_recall_at_k.py` | 文档只说对比 → **补足**最小指标函数与固定 K 口径 |
| 三方消融 | `10_ablation.py` | 文档只说对比 → **补足**固定语料/查询的三路消融表 |

### 补足的四个高频坑

| 坑 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 直接相加原始分 | `pitfalls/hybrid_pitfalls.py` | 文档讲归一化但没演示"谁压倒谁" |
| 去重丢掉双路加成 | `pitfalls/hybrid_pitfalls.py` | RRF 按 doc_id 累加，提前去重会丢强信号 |
| tokenizer 不一致 | `pitfalls/hybrid_pitfalls.py` | ES 经验平移中最容易漏的一环 |
| 过滤放在融合后 | `pitfalls/hybrid_pitfalls.py` | 名额不补位 + 可能的信息泄漏 |

## 五、验收标准与本地验证

- [x] BM25 + 向量双路召回 + RRF 融合 → `engineering/hybrid_retriever.py`
- [x] 专名查询对比"纯向量 vs 混合" → `hybrid_lab/REPORT.md`（程序真实输出）
- [x] 能解释量纲不可直接相加 → `core_mechanisms/06_normalization_trap.py`
- [x] 函数级单测覆盖 → `tests/week09/`

```bash
.venv/Scripts/python.exe -m ruff check week09 tests/week09
.venv/Scripts/python.exe -m mypy week09 tests/week09
.venv/Scripts/python.exe -m pytest -q tests/week09
.venv/Scripts/python.exe -m week09.engineering.engineering_demo
.venv/Scripts/python.exe -m week09.hybrid_lab
```

## 六、坑提醒

- **RRF 的 rank 从 1 开始**：从 0 开始会把第一名权重异常放大。
- **BM25 分数无上界**：和 cosine 直接相加等于让量纲替你决定权重。
- **分词器是索引契约**：改 tokenizer 必须两路一起重建，和 ES 改 analyzer 一样。
- **过滤必须在召回前**：后过滤不会补 Top-K 名额，还可能泄漏越权文档。
- **别越界**：本周不做 cross-encoder rerank（第 10 周），不做评测体系（第 12 周）。
