# 第 7 周：RAG 基础 + 文档解析与切分

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第二阶段 / 第 7 周。
> **本周严格限定在第 7 周范围内**：只做解析与切分，embedding / 向量库留到第 8 周，
> BM25 / 混合检索留到第 9 周。

## 一、学习目标

> 搞清 RAG 每个环节在做什么，重点攻克"切分"。本周产出是一份**同语料四策略对比表**，
> 以及能真实读 PDF / Word / HTML / Markdown / Excel 的解析器。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | RAG 全景：画出每一环输入输出 | `core_mechanisms/01` |
| 工作日 4h | 实装五种格式解析 | `core_mechanisms/02~05` + `engineering/parsers.py` |
| 周末 8h | 四种切分策略实验 + small-to-big | `core_mechanisms/06~10` + `chunking_lab/` |

## 二、与第 6 周的衔接（覆盖已掌握内容，不重复讲解）

| 第 6 周已掌握 | 第 7 周如何使用（不再重复讲解） |
| --- | --- |
| 第 6 周 `10_rag_preview` 九环节 | `01_rag_pipeline.py` 只补"输入输出的具体形状"，不重讲概念 |
| 第 1 周 `dataclass` | `Document` / `Chunk` 继续用 dataclass，原理不再展开 |
| 第 1 周 openpyxl | Excel 解析直接复用，Python↔Java 行模型差异只在注释里点出 |
| 第 6 周四段式文档字符串 + `demo()` 入口 | 本周全部样例沿用同一写法 |
| 第 6 周无端口测试风格 | 解析样例用 `tempfile` 生成文件再读回，测试不需要外链 |

> **一句话递进关系**：第 6 周把 RAG 环节"背下来"，第 7 周把前两环"做出来"——
> 解析保真决定有没有信息，切分决定信息能不能被单独检索到。

## 三、任务与文件映射

| 时段 | 落地文件 |
| --- | --- |
| RAG 全景 | [`core_mechanisms/01`](core_mechanisms/) —— 九环节输入输出清单 |
| 五种解析 | [`core_mechanisms/02~05`](core_mechanisms/) + [`engineering/parsers.py`](engineering/) |
| 五种切分 | [`core_mechanisms/06~10`](core_mechanisms/) + [`engineering/chunkers.py`](engineering/) |
| 对比实验 | [`chunking_lab/`](chunking_lab/) —— `python -m week07.chunking_lab` |
| 认知误区 | [`pitfalls/`](pitfalls/) —— 丢页码/表格/标题、调参顺序颠倒 |

可运行知识点共 10 个，见 `core_mechanisms/` 的 01~10；所有样例无需 API Key 与网络。

## 四、知识点对照表（文档原有 vs 补足）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| RAG 九环输入输出 | `01_rag_pipeline.py` | 文档列名 → **补足**每环的具体输入/输出数据结构 |
| PDF 解析 | `02_parse_pdf.py` | 文档只列库名 → **补足**页码边界与空文本兜底 |
| Word 解析 | `03_parse_docx.py` | 文档只列库名 → **补足**标题样式与表格行拼接 |
| HTML 解析 | `04_parse_html.py` | 文档只列库名 → **补足**script/style 清理 |
| Markdown / Excel | `05_parse_markdown_excel.py` | 文档列名 → **补足**sheet 名保留与 None 单元格处理 |
| 固定 / 递归切分 | `06` / `07` | 文档给参数 → **补足**可运行滑窗与分隔符优先级 |
| 标题 / 语义切分 | `08` / `09` | 文档给思路 → **补足**title_path 栈与无 embedding 的词重合近似 |
| small-to-big | `10` | 文档给概念 → **补足**父块文本入 metadata 的具体契约 |
| 四种策略对比 | `chunking_lab/` | 文档给四个维度 → **补足**可复跑的截断率判据与样本提示 |
| 好 chunk 判据 / 调参顺序 | `pitfalls/extra_gotchas.py` | 文档给面试话术 → 补足可运行数字与顺序清单 |

## 五、验收标准与本地验证

- [x] 能解析 PDF / Word / HTML / Markdown 四种格式（另补 Excel）
  → `python -m week07.engineering.engineering_demo`
- [x] 4 种切分跑在同一份文档上有对比表
  → `python -m week07.chunking_lab`，结果见 [`chunking_lab/REPORT.md`](chunking_lab/REPORT.md)
- [x] 能说清"什么样的 chunk 是好 chunk"
  → `pitfalls/extra_gotchas.py` 三条判据 + 人工抽检提示

三件套验证（在仓库根目录）：

```bash
.venv/Scripts/python.exe -m ruff check week07 tests/week07
.venv/Scripts/python.exe -m mypy week07 tests/week07
.venv/Scripts/python.exe -m pytest -q tests/week07
```

## 六、坑提醒

- **解析丢页码**：PDF 不插换页符，跨页内容会被误认为同页，引用指向错误页。
- **解析丢表格**：python-docx 只看 paragraphs 时表格行完全消失，故障码对应关系丢失。
- **解析丢标题层级**：把标题从正文剥掉，chunk 脱离原文后无法判断所属章节。
- **固定长度截条款**："第 N 条"被劈成两半，两半都命中却都答不全。
- **overlap 不是越大越好**：重复内容稀释 Top-K 多样性，还线性放大索引体积。
- **先修检索再修生成**：直接调 rerank 假设召回完美，通常并不成立。
- **本周越界警告**：不实现 embedding / 向量库（第 8 周），不实现 BM25（第 9 周）。
