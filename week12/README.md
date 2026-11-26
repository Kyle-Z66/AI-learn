# 第 12 周：效果评测体系 ★ 第二阶段收口

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第二阶段 / 第 12 周。
> 本周目标：建立 golden set + 量化指标 + 四配置消融 + CI 回归，并交付 P2 RAG 项目。
> **这一步做完，和"跑通 Demo 的人"就是两个物种**——前提是所有数字都真实跑出来。

## 一、学习目标（文档原文四任务）

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | 建 golden set：100 条（宁少而精），标准答案 + 相关片段 ID + 标注标准 | [`p2_rag/golden_set.json`](p2_rag/golden_set.json) + `engineering/golden_set.py` |
| 工作日 4h | 定义指标：检索侧四项 + 生成侧三项 + 幻觉率/实体命中 | `engineering/metrics.py` + `core_mechanisms/03~07` |
| 周末 8h | 跑基线 + 消融：四配置对比表 | `engineering/runner.py` + `p2_rag/REPORT.md` |
| 周末 4h | CI 化 + 报告 + P2 交付 | `engineering/ci_gate.py` + [`p2_rag/`](p2_rag/) + [`STAGE_REVIEW.md`](STAGE_REVIEW.md) |

## 二、与第 7~11 周的衔接（检索链与生成链已完成）

| 已掌握 | 第 12 周如何使用（不重复实现） |
| --- | --- |
| 第 7 周解析 / 切分 | 切分粒度影响召回，本周在 BM25 单字切分里体现；不改解析代码 |
| 第 8 周嵌入 / 索引 | dense-only 用确定性 TF-IDF 替身，真实向量接口留作生产替换点 |
| 第 9 周 BM25 / 混合召回 | 直接复用 RRF 思路：score = Σ1/(60+rank)，四配置共用同一语料 |
| 第 10 周重排 | hybrid+rerank 在 Top10 内按实词覆盖重排，验证"重排不是万能" |
| 第 11 周守卫 / 引用 | Faithfulness 复用数字实体抽取；生成侧对四配置一视同仁 |
| 第 6 周 FastAPI / Docker | P2 交付复用应用工厂、非 root 镜像、环境变量注入的成熟形态 |

> **一句话递进关系**：前五周把 RAG 链造出来并让它可靠作答，本周回答"凭什么说它好"——
> 用可复算的指标、可对比的消融、可拦退化的门禁，把主观感觉变成工程证据。

## 三、任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | 建 golden set | `engineering/golden_set.py` + `p2_rag/golden_set.json`（100 条教学样例） |
| 工作日 4h | 定义指标 | `engineering/metrics.py` + `core_mechanisms/01~07` |
| 周末 8h | 基线 + 消融 | `engineering/runner.py` + `core_mechanisms/08` + `p2_rag/REPORT.md` |
| 周末 4h | CI + 报告 + 交付 | `engineering/{ci_gate,report}.py` + `p2_rag/`（API/Docker/博客） |
| 阶段复盘 | 验收卡 + 诚实自评 | [`STAGE_REVIEW.md`](STAGE_REVIEW.md) |

可运行知识点共 10 个：

| 编号 | 文件 | 知识点 |
| --- | --- | --- |
| 01 | `01_golden_set_schema.py` | 标注字段结构 |
| 02 | `02_labeling_rules.py` | 标注规则与门禁 |
| 03 | `03_recall_at_k.py` | Recall@k |
| 04 | `04_mrr.py` | MRR@10 |
| 05 | `05_context_precision_recall.py` | Context Precision / Recall |
| 06 | `06_faithfulness.py` | Faithfulness |
| 07 | `07_answer_relevance.py` | Answer Relevance |
| 08 | `08_ablation_matrix.py` | 四配置消融矩阵 |
| 09 | `09_ci_gate.py` | 阈值与退出码 |
| 10 | `10_report_writer.py` | Markdown 报告渲染 |

## 四、知识点对照表（文档原有 vs 补足）

### 4.1 文档原文覆盖

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 100 条 golden set | `golden_set.json` / `01`、`02` | 文档要求"宁少而精"→ 补足字段契约、标注规则、来源标注与真实数据替换步骤 |
| Recall@k / MRR@10 | `03`、`04` / `metrics.py` | 文档列名 → 补足分母口径、strict zip、未命中记 0 |
| Context Precision / Recall | `05` | 文档列名 → 补足"分母不同"的对比与空上下文处理 |
| Faithfulness / Answer Relevance | `06`、`07` | 文档列名 → 复用第 11 周守卫，明确粗实现边界 |
| 四配置消融 | `08` / `runner.py` | 文档要求画表 → 补足共用语料与生成器、逐案分布 |
| CI 回归 | `09` / `ci_gate.py` | 文档只说"做回归" → 补足阈值方向、退出码契约 |
| Markdown 报告 | `10` / `report.py` | 文档给了示意表 → 补足程序渲染与口径说明 |
| P2 可运行 + README + 报告 | `p2_rag/` | 文档要求 → FastAPI 接口、Docker、架构图、BLOG、REPORT 齐全 |

### 4.2 对照文档补足的遗漏项

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 教学样例 vs 真实数据的边界 | `golden_set.json` metadata / `p2_rag/README.md` | 文档要求真实场景数据，不能伪造；写清替换步骤才是诚实交付 |
| 评测集泄漏 | `pitfalls/evaluation_pitfalls.py` | 同集调参会虚高，dev/holdout 是面试官必问 |
| 只报均分的分布盲区 | `report.py` 分布表 | 均值相同但长尾不同，优化线索在分布里 |
| 延迟与质量分开报告 | `REPORT.md` 双列 | 合成"综合分"会让取舍无法复盘 |
| 重排可能是负收益 | `runner.py` 真实指标 | 消融的意义就是验证，而不是背诵"rerank 更好" |
| CI 是护栏不是成绩单 | `pitfalls/extra_gotchas.py` | 防止把"没退化"讲成"质量高" |

## 五、验收标准与本地验证

文档阶段验收卡六条（逐条证据见 [`STAGE_REVIEW.md`](STAGE_REVIEW.md)）：

- [x] P2 项目能跑、有 API、有 Docker → `p2_rag/`（CLI 自检 + FastAPI + Dockerfile/compose）
- [x] 100 条 golden set + 四配置对比表 + 评测报告 → `golden_set.json` + `REPORT.md`
- [x] 能讲清每层技术解决什么、代价是什么 → `p2_rag/README.md` 设计决策表 + BLOG
- [x] 能讲清为什么先修检索再修生成 → `pitfalls/extra_gotchas.py` + 消融数据
- [x] 有一篇 RAG 技术博客 → `p2_rag/BLOG.md`
- [x] 阶段自评（0~5 诚实打分）→ `STAGE_REVIEW.md`

本地验证：

```bash
python -m week12.engineering.engineering_demo   # 100 条四配置真实评测 + 报告 + 门禁
python -m week12.p2_rag                          # 仅导入/自检，不启服务、不需要 Key
python -m ruff check week12 tests/week12
python -m mypy week12 tests/week12
python -m pytest -q tests/week12
```

实测指标见 [`p2_rag/REPORT.md`](p2_rag/REPORT.md)：所有数字来自 `engineering_demo` 实跑输出，
p95 为本地教学测量。

## 六、坑提醒

- **不要造数据**：golden set 是教学样例就明确标注；真实替换步骤写在项目 README。
- **不要用测试集调参**：dev/holdout 分开，最终数字只在 holdout 上报一次。
- **不要只报平均分**：报告强制附逐案 recall 的最小/中位/最大。
- **不要把延迟和质量混谈**：四配置表分列 p95，取舍靠数据不靠感觉。
- **重排不是万能**：本教学语料里 hybrid+rerank 的 Recall 反而略低，消融如实呈现。
- **CI 门禁是护栏**：退出码 1 只说明退化，不代表配置排名；选型看报告与分布。
- **下周进入 Agent**：第 13 周把"检索 + 生成 + 工具"变成可执行流程，本周的评测集是回归基线。
