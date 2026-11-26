# 第 8 周：Embedding 与向量数据库

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第二阶段 / 第 8 周。
> **本周严格限定在第 8 周范围内**：不实现 BM25 / 混合检索（第 9 周），
> 第 7 周的解析与切分仅以 README 一句话衔接。

## 一、学习目标

> 掌握嵌入模型选型 + 向量库部署，并把 PostgreSQL / GaussDB 的运维经验
> 平移成"向量检索 + RBAC 标量过滤"的差异化论点。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | Embedding 原理与选型 | `core_mechanisms/01~04` |
| 工作日 4h | 向量库三选一（推荐 pgvector） | `core_mechanisms/05` + `engineering/pgvector_sql.py` |
| 周末 8h | 建索引 + 调参 + 标量过滤 | `core_mechanisms/06~10` + `vector_lab/` |

## 二、与第 7 周的衔接（一句话衔接，不重复讲解）

| 第 7 周已掌握 | 第 8 周如何使用（不再重复讲解） |
| --- | --- |
| 第 7 周 `Document` / `Chunk` | 只取 `Chunk.text` 作为嵌入输入，结构与切分不再展开 |
| 第 7 周 `title_path` / `page` / `source` | 原样写入向量库 metadata，供过滤与引用使用 |
| 第 7 周语义完整性抽检 | 换成"召回率基准"来量化检索质量，方法见 `10_recall_benchmark` |
| 第 7 周四段式文档字符串 + `demo()` | 全部样例沿用同一写法 |

> **一句话递进关系**：第 7 周把文档切成可检索的块，第 8 周把块变成向量、
> 放进可过滤的库，并证明"检索质量是可度量的"。

## 三、任务与文件映射

| 任务 | 落地文件 |
| --- | --- |
| Embedding 原理与度量 | [`core_mechanisms/01~04`](core_mechanisms/) |
| pgvector 表与索引 | [`core_mechanisms/05~06`](core_mechanisms/) + [`engineering/pgvector_sql.py`](engineering/) |
| 标量过滤 / 入库 / 持久化 / 召回 | [`core_mechanisms/07~10`](core_mechanisms/) + [`vector_lab/`](vector_lab/) |
| 认知误区 | [`pitfalls/`](pitfalls/) —— 归一化、模型一致、维度、过期、ANN 取舍 |

可运行知识点共 10 个；所有样例用本地确定性 `HashEmbedding`，**无 API Key、无网络**。

## 四、知识点对照表（文档原有 vs 补足）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 向量语义与归一化 | `01_embedding_basics.py` | 文档点名 → 补足可运行向量与范数观察 |
| cosine/dot/euclidean | `02_similarity_metrics.py` | 文档点名 → 补足统一"越大越相关"的口径 |
| 模型选型 | `03_model_selection.py` | 文档给三个模型 → 补足维度/稀疏/部署约束表 |
| 维度选择 | `04_dimension_truncation.py` | 文档提维度 → 补足截断损失与入库拒绝演示 |
| pgvector 建表 | `05_pgvector_schema.py` | 文档给 SQL → 补足参数化生成与自检清单 |
| HNSW / IVF | `06_hnsw_ivf.py` | 文档点名 → 补足取舍表与索引建议函数 |
| 标量过滤 | `07_scalar_filter.py` | 文档给 SQL WHERE → 补足内存库 where 与过滤前置 |
| 向量库 add/search | `08_vector_store.py` | 文档未细化 → 补足统一契约与 Top-K |
| 持久化 | `09_persistence_reload.py` | 文档未提 → 补足 JSON 快照与一致性验证 |
| 召回率 | `10_recall_benchmark.py` | 文档提 ef_search/probes → 补足 recall@K 评估口径 |

## 五、验收标准与本地验证

- [x] 能解释 cosine / dot / euclidean 的适用差异
  → `python -m week08.core_mechanisms.02_similarity_metrics`
- [x] pgvector 或 Milvus 任选其一跑起来 → 本周用 `engineering/pgvector_sql.py`
  生成可执行的参数化 DDL/检索 SQL；离线环境用内存库验证同一语义
- [x] 实现带元数据过滤的向量检索
  → `python -m week08.core_mechanisms.07_scalar_filter`
- [x] 能说清 HNSW vs IVF 的取舍
  → `core_mechanisms/06` + `pitfalls/extra_gotchas.py`

三件套验证：

```bash
.venv/Scripts/python.exe -m ruff check week08 tests/week08
.venv/Scripts/python.exe -m mypy week08 tests/week08
.venv/Scripts/python.exe -m pytest -q tests/week08
```

## 六、坑提醒

- **未归一化误用 dot**：长文本凭范数虚假领先，先归一化或改用 cosine。
- **query/doc 用不同模型**：向量空间不对齐，全量重嵌前不要混用索引。
- **维度不匹配**：`vector(1024)` 差一维都不能入库，别用截断/补零凑数。
- **过期文档未过滤**：政策/手册类知识库尤其致命，过滤必须在打分前。
- **RBAC 后置**：Top-K 里全是无权文档时，看起来像"检索不准"。
- **ANN 不是玄学**：ef_search / probes 越大召回越高、延迟也越高，要画曲线。
- **本周越界警告**：不做 BM25 / 混合检索（第 9 周）；哈希向量只是教学替身。
