# AI-learn

记录 Python 和大模型功能的学习过程。

本仓库按**周**组织示例工程，配套《大模型应用开发能力补足 —— 20 周可执行学习计划》。每周目录包含该周每个动作的可运行样例代码、中文知识点注释与单元测试。

## 周索引

| 周次    | 主题                                | 目录                           | 状态      |
| ------- | ----------------------------------- | ------------------------------ | --------- |
| 第 1 周 | Python 语法速成（面向 Java 程序员） | [`week01/`](week01/README.md) | ✅ 已完成 |
| 第 2 周 | LLM API 基础与 Prompt 工程          | [`week02/`](week02/README.md) | ✅ 已完成 |
| 第 3 周 | LangChain 基础 + P1 项目启动         | [`week03/`](week03/README.md) | ✅ 已完成 |
| 第 4 周 | Token 生命周期 + 流式 + 并发         | [`week04/`](week04/README.md) | ✅ 已完成 |

> 后续周次将按同样结构追加：`week05/`、`week06/` ……

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
├── tests/week01/               # 第 1 周单元测试
├── tests/week02/               # 第 2 周单元测试
├── tests/week03/               # 第 3 周单元测试
└── tests/week04/               # 第 4 周单元测试
```

## 约定

- 每个样例文件头部都有中文文档字符串，标注**对应知识点 / 周次要点 / 易忽略细节 / 示例用途**。
- 关键代码行用中文注释说明「为什么」而不仅是「做什么」，尤其针对 Java → Python 的思维差异。
- `week01/README.md` / `week02/README.md` / `week03/README.md` / `week04/README.md` 的对照表区分「文档原有知识点」与「对照文档补足的内容」，补足项均标注来源。
