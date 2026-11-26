# 第 8 周动手项目：向量检索四项实验

## 怎么跑

```bash
.venv/Scripts/python.exe -m week08.vector_lab
```

无数据库、无 API Key、无网络。向量来自本地确定性 `HashEmbedding`（教学替身）。

## 实验内容

| 实验 | 观察点 |
| --- | --- |
| 三种相似度 | 同一查询在 cosine / dot / euclidean 下的 Top-3 |
| 标量过滤 | `dept_id=ops` 且 `valid_until > 今天`，过期/越权文档不进候选 |
| 持久化重载 | JSON 快照保存后重载，Top-3 是否一致 |
| 召回基准 | 候选占比 30% / 60% / 100% 时的 recall@3 |

## 语料

`corpus.py` 复制了第 7 周切分文案的本地副本（10 条），每条带 `dept_id` 与
`valid_until`。刻意保留一条过期记录和跨部门记录，用来验证过滤确实生效。

## 边界

- 不实现 BM25 / 混合检索（第 9 周）。
- 不连接真实向量数据库；pgvector DDL 在 `core_mechanisms/05` 生成。
- 哈希向量只反映词面重合，不能用来评价真实 embedding 的语义质量。

## 测试

```bash
.venv/Scripts/python.exe -m pytest -q tests/week08/test_vector_lab.py
```
