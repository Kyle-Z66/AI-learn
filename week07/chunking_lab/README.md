# 第 7 周动手项目：切分策略对比实验

## 怎么跑

```bash
.venv/Scripts/python.exe -m week07.chunking_lab
```

无需 API Key、无需网络、无需外部数据文件。语料内嵌在 `corpus.py`。

## 实验设计

同一份文档 `SGCC-4012 网关运维知识库`（10 个标题、编号条款、Markdown 表格）
跑四种策略：

| 策略 | 参数 | 意图 |
| --- | --- | --- |
| A 固定 | 512 token / overlap 64 | 基线：最简单也最容易硬切 |
| B 递归 | 512 token / overlap 64 | 优先在段落、换行、句号处断开 |
| C 标题前缀 | 512 token | 按标题栈切，标题拼进每块 |
| D small-to-big | 小块 96 / 父块 512 | 小块检索，返回 `metadata.parent_text` |

## 观察维度

- chunk 数量
- 平均 token（"汉字 1 / 英文词 1"近似，和 reranker 预算同口径）
- 结构截断率：含条款或表格的 chunk 里，首句未收尾或表格行未闭合的比例
- 语义完整性：程序只打印抽检提示，人工看 10 个样本后自行判断

## 文件说明

- `corpus.py`：内置中文语料与 `build_corpus_document()`
- `evaluate.py`：策略执行、截断判据、结果渲染
- `__main__.py`：CLI 打印入口
- `REPORT.md`：真实运行结果与解读

## 边界

本项目**不做** embedding、向量检索与 BM25；它们分别属于第 8、9 周。

## 测试

```bash
.venv/Scripts/python.exe -m pytest -q tests/week07/test_chunking_lab.py
```
