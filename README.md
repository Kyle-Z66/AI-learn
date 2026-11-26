# AI-learn

记录 Python 和大模型功能的学习过程。

本仓库按**周**组织示例工程，配套《大模型应用开发能力补足 —— 20 周可执行学习计划》。每周目录包含该周每个动作的可运行样例代码、中文知识点注释与单元测试。

## 周索引

| 周次    | 主题                                    | 目录                           | 状态      |
| ------- | --------------------------------------- | ------------------------------ | --------- |
| 第 1 周 | Python 语法速成（面向 Java 程序员）     | [`week01/`](week01/README.md) | ✅ 已完成 |
| 第 2 周 | LLM API 基础与 Prompt 工程              | [`week02/`](week02/README.md) | ✅ 已完成 |
| 第 3 周 | LangChain 基础 + P1 项目启动            | [`week03/`](week03/README.md) | ✅ 已完成 |
| 第 4 周 | Token 生命周期 + 流式 + 并发            | [`week04/`](week04/README.md) | ✅ 已完成 |
| 第 5 周 | AI 网关硬骨头：熔断、降级、审计、可观测 | [`week05/`](week05/README.md) | ✅ 已完成 |
| 第 6 周 | P1 收尾 + 阶段复盘                      | [`week06/`](week06/README.md) | ✅ 已完成 |
| 第 7 周 | RAG 基础 + 文档解析与切分               | [`week07/`](week07/README.md) | ✅ 已完成 |
| 第 8 周 | Embedding 与向量数据库                  | [`week08/`](week08/README.md) | ✅ 已完成 |
| 第 9 周 | 混合检索（BM25 + 向量 + RRF）           | [`week09/`](week09/README.md) | ✅ 已完成 |
| 第 10 周 | Rerank 重排 + 超时降级                  | [`week10/`](week10/README.md) | ✅ 已完成 |
| 第 11 周 | 生成环节：引用溯源与幻觉抑制            | [`week11/`](week11/README.md) | ✅ 已完成 |
| 第 12 周 | 效果评测体系 + P2 交付 + 阶段复盘       | [`week12/`](week12/README.md) | ✅ 已完成 |

> 第一阶段（第 1~6 周）：Python 基础 → LLM API → LangChain → 并发 → 稳定性 → P1 HTTP 交付。
> 第二阶段（第 7~12 周）：解析/切分 → 嵌入/向量库 → 混合检索 → 重排 → 生成可靠性 → 评测与 P2 交付。

## 快速开始

推荐用 `uv` 管理依赖（学习计划指定的 2026 主流工具）。若你已习惯 Anaconda，两者可共存：**conda 负责解释器，uv 负责项目依赖**。

```bash
# 1. 同步依赖：uv 会自动创建 .venv 虚拟环境（对应"虚拟环境"知识点）
uv sync

# 2. 三件套验收（对应第 1 周验收标准第 1 条）
uv run ruff check .          # 代码规范检查（E/F/I/B/UP/SIM）
uv run mypy                  # 静态类型检查
uv run pytest                # 单元测试

# 3. 运行任一知识点的可运行样例（无需 API Key，默认 Mock）
uv run python week01/language_features/01_type_annotations.py
uv run python -m week01.excel_exporter        # 第1周：Excel 批量导出器
uv run python week02/api_fundamentals/01_tokenization.py
uv run python -m week02.structured_output     # 第2周：结构化输出 + 错误回灌重试
uv run python -m week03.core_abstractions.06_lcel_chain  # 第3周：LCEL 组合原理
uv run python -m week03.p1_gateway            # 第3周：P1 多模型统一网关 v0.1
uv run python -m week04.core_mechanisms.05_sse_frames  # 第4周：SSE 逐字输出
uv run python -m week04.concurrency_lab       # 第4周：100 请求并发压测对比
uv run python -m week05.core_mechanisms.01_circuit_breaker_states  # 第5周：三态熔断
uv run python -m week05.audit_lab             # 第5周：全链路审计 + 成本日报表
uv run python -m week06.engineering.engineering_demo  # 第6周：FastAPI 无端口调用示范
uv run python -m week06.p1_fastapi            # 第6周：P1 服务入口（本地 HTTP 服务）
uv run python -m week07.chunking_lab          # 第7周：四策略切分对比表
uv run python -m week08.vector_lab            # 第8周：相似度 + 标量过滤 + 召回基准
uv run python -m week09.hybrid_lab            # 第9周：纯向量 vs 混合检索对比
uv run python -m week10.rerank_lab            # 第10周：混合 + rerank 三方对比
uv run python -m week11.answer_lab            # 第11周：引用 / 拒答 / 幻觉守卫
uv run python -m week12.engineering.engineering_demo  # 第12周：四配置评测回归
uv run pytest --cov=week06 --cov-report=term-missing --cov-fail-under=60
uv run pytest --cov=week12 --cov-report=term-missing --cov-fail-under=60
```

> 若暂时不想装 uv，也可在已装好依赖的 Python 3.12+ 环境直接运行：
> `python -m pytest`、`python -m ruff check .`、`python -m mypy`。

## 目录结构

```
AI-learn/
├── pyproject.toml              # uv 项目元数据 + ruff/mypy/pytest 统一配置
├── week01/                     # 第 1 周：Python 语法速成（面向 Java 程序员）
│   ├── README.md               # 本周目标 / 动作 / 知识点对照 / 验收标准
│   ├── language_features/      # 动作 1：10 个语言差异点（逐个可运行）
│   ├── pitfalls/               # 文档要求的 6 个坑 + 文档未展开的补足要点
│   ├── engineering/            # 动作 2：工程规范的可运行示范
│   └── excel_exporter/         # 动作 3：Excel 批量导出器（asyncio + 线程池 + ZIP）
├── week02/                     # 第 2 周：LLM API 基础与 Prompt 工程
│   ├── README.md               # 本周目标 / 4 个任务 / 知识点对照 / 验收标准
│   ├── api_fundamentals/       # 动作 1：8 个原理点 + 1 个补足核心点
│   ├── pitfalls/               # LLM 非确定性等认知误区
│   ├── engineering/            # 动作 2：三厂商适配器 + Mock 客户端
│   ├── prompt_lab/             # 动作 3：10 个 Prompt 对比实验 + REPORT.md
│   └── structured_output/      # 动作 4：Pydantic schema + 错误回灌重试
├── week03/                     # 第 3 周：LangChain 基础 + P1 项目启动
│   ├── README.md               # 本周目标 / 3 个任务 / 与前两周衔接 / 验收标准
│   ├── core_abstractions/      # 动作 1：5 个核心抽象 + LCEL 组合原理（01~06）
│   ├── pitfalls/               # 版本陷阱 / import 路径 / 废弃清单
│   ├── engineering/            # 动作 2：复用第 2 周适配器 + 网关协议 + 降级链
│   └── p1_gateway/             # 动作 3：P1 多模型统一网关 v0.1（骨架）
├── week04/                     # 第 4 周：Token 生命周期 + 流式 + 并发
│   ├── README.md               # 本周目标 / 3 个任务 / 与前 3 周衔接 / 验收标准
│   ├── core_mechanisms/        # 缓存 / 流式 / 并发共 10 个知识点（01~10）
│   ├── pitfalls/               # Token 概念混淆 / 文档标准写法缺陷
│   ├── engineering/            # TokenCache + SSE + RateLimiter + 示范
│   └── concurrency_lab/        # 动手项目：100 请求并发压测对比表
├── week05/                     # 第 5 周：熔断 + 降级 + 审计 + 可观测
│   ├── README.md               # 本周目标 / 3 个任务 / 与前 4 周衔接 / 验收标准
│   ├── core_mechanisms/        # 熔断 / 超时 / 重试 / 幂等 / 审计 / 指标（01~10）
│   ├── pitfalls/               # 文档熔断器缺陷 / 可靠性认知误区
│   ├── engineering/            # 熔断器 + 重试 + 超时 + 审计 + 成本 + 指标
│   └── audit_lab/              # 动手项目：19 字段审计 + 成本日聚合报表
├── week06/                     # 第 6 周：P1 收尾 + 阶段复盘
│   ├── README.md               # 本周目标 / 4 任务 / 与前 5 周衔接 / 阶段验收卡
│   ├── core_mechanisms/        # FastAPI 交付与复盘 10 个知识点（01~10）
│   ├── pitfalls/               # 同步阻塞 / 伪流式 / Docker 密钥等坑
│   ├── engineering/            # app + schemas + 依赖注入 + 无端口示范
│   ├── p1_fastapi/             # 可交付项目：入口 / Dockerfile / compose / README / BLOG
│   └── STAGE_REVIEW.md         # 第一阶段验收卡 + 复盘模板示例
├── week07/                     # 第 7 周：RAG 基础 + 文档解析与切分
│   ├── core_mechanisms/        # 九环节 / 五格式解析 / 四种切分策略（01~10）
│   ├── pitfalls/               # 解析丢结构 / 切分截断等坑
│   ├── engineering/            # Document + Chunk 模型 / parsers / chunkers
│   └── chunking_lab/           # 动手项目：512/64 四策略对比表 + REPORT
├── week08/                     # 第 8 周：Embedding 与向量数据库
│   ├── core_mechanisms/        # 相似度 / 选型 / HNSW-IVF / 标量过滤（01~10）
│   ├── pitfalls/               # 归一化 / 模型一致性 / 权限过滤缺位等坑
│   ├── engineering/            # HashEmbedding + 内存向量库 + pgvector SQL
│   └── vector_lab/             # 动手项目：度量对比 / 过滤 / 召回基准
├── week09/                     # 第 9 周：混合检索
│   ├── core_mechanisms/        # BM25 / 向量 / RRF / 归一化陷阱（01~10）
│   ├── pitfalls/               # 量纲混加 / 过滤时机 / tokenizer 漂移等坑
│   ├── engineering/            # 双路索引 + 融合 + HybridRetriever
│   └── hybrid_lab/             # 动手项目：专名查询与纯向量召回对比
├── week10/                     # 第 10 周：Rerank 重排
│   ├── core_mechanisms/        # bi/cross encoder / 预算 / 降级 / 指标（01~10）
│   ├── pitfalls/               # 超时拖垮 / 重排当召回 / 候选过多等坑
│   ├── engineering/            # DeterministicReranker + fallback + 指标
│   └── rerank_lab/             # 动手项目：Top-50 → Top-5 三方对比
├── week11/                     # 第 11 周：生成环节
│   ├── core_mechanisms/        # Prompt / 预算 / 引用 / 预检 / 幻觉守卫（01~10）
│   ├── pitfalls/               # 编造 / 引用漂移 / 低温度误解等坑
│   ├── engineering/            # ContextBundle + guards + FakeGenerator
│   └── answer_lab/             # 动手项目：四类用例的引用与拒答验证
├── week12/                     # 第 12 周：效果评测体系 + P2 交付
│   ├── core_mechanisms/        # golden set / 指标 / 消融 / CI / 报告（01~10）
│   ├── pitfalls/               # 造数据 / 测试集泄漏 / 延迟与质量混谈等坑
│   ├── engineering/            # 100 条样例集 / metrics / runner / report / CI gate
│   ├── p2_rag/                 # 可交付项目：FastAPI / Docker / README / BLOG / REPORT
│   └── STAGE_REVIEW.md         # 第二阶段验收卡 + 复盘模板示例
├── tests/week01/               # 第 1 周单元测试
├── tests/week02/               # 第 2 周单元测试
├── tests/week03/               # 第 3 周单元测试
├── tests/week04/               # 第 4 周单元测试
├── tests/week05/               # 第 5 周单元测试
├── tests/week06/               # 第 6 周单元测试
├── tests/week07/               # 第 7 周单元测试
├── tests/week08/               # 第 8 周单元测试
├── tests/week09/               # 第 9 周单元测试
├── tests/week10/               # 第 10 周单元测试
├── tests/week11/               # 第 11 周单元测试
└── tests/week12/               # 第 12 周单元测试
```

## 约定

- 每个样例文件头部都有中文文档字符串，标注**对应知识点 / 周次要点 / 易忽略细节 / 示例用途**。
- 关键代码行用中文注释说明「为什么」而不仅是「做什么」，尤其针对 Java → Python 的思维差异。
- `week01/` ~ `week12/` 的 `README.md` 对照表区分「文档原有知识点」与「对照文档补足的内容」，补足项均标注来源。
- 第 7~12 周复用第 1~6 周的 Pydantic、网关、并发、熔断、SSE、FastAPI 与审计思维；
  必要回顾只在衔接表出现，不重复讲解已掌握原理。
- 第二阶段所有 embedding / rerank / LLM 生成均使用确定性本地替身，无需 API Key；
  `REPORT.md` 中的数字来自仓库内可复现实跑，替换真实业务语料与模型即可迁移。
