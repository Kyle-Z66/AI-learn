# 第 1 周：Python 语法速成（面向 Java 程序员）

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 1 周。
> **本目录严格限定在第 1 周范围内**，不触碰第 2 周及以后的 LLM API / Prompt / LangChain 等内容。

## 一、学习目标（文档原文）

> 能读懂并写出工程级 Python 代码。**不要系统学 Python**，你已有 Java 底子，专注差异点。

用户前提：**已掌握 Python 基础语法和 Anaconda 基本使用**。因此本工程不重复讲解变量、if/for、函数定义等基础，而是聚焦 Java 程序员转型时真正卡人的差异点与工程规范。

## 二、三个具体动作与文件映射

| 时段 | 文档动作 | 落地文件 |
| --- | --- | --- |
| 工作日 5h | **语言差异点** | [`language_features/01`~`10`](language_features/) —— 10 个知识点各一个可运行脚本 |
| 工作日 3h | **工程规范** | 根目录 [`pyproject.toml`](../pyproject.toml) + [`engineering/engineering_demo.py`](engineering/engineering_demo.py) |
| 周末 8h | **动手项目** | [`excel_exporter/`](excel_exporter/) —— Excel 批量导出器（分片 + 线程池 + ZIP） |
| 贯穿 | **6 个特有坑** | [`pitfalls/six_pitfalls.py`](pitfalls/six_pitfalls.py)（错误 vs 正确对照） |

## 三、知识点对照表（文档原有 vs 对照补足）

### 3.1 动作 1 · 语言差异点（文档列出的 10 项，全部覆盖）

| # | 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- | --- |
| 1 | 类型注解 `Optional[str]` / `list[str]` | `01_type_annotations.py` | 文档仅举例 → **补足** `X \| None` 现代写法、注解运行时不强制、`TypeAlias`/`Callable`/`TypeVar` |
| 2 | 装饰器 | `03_decorators.py` | 文档仅列名 → **补足** `functools.wraps`、带参装饰器、叠加顺序 |
| 3 | `dataclass` | `02_dataclass.py` | 文档仅列名 → **补足** `field(default_factory=)`（直连坑 #1）、`frozen`/`slots`/`asdict` |
| 4 | 生成器 | `04_generators.py` | 文档仅列名 → **补足** 惰性求值、`yield from`、一次性消费、`send` |
| 5 | `asyncio`/`await` | `05_asyncio_await.py` | 文档只在"坑提醒"强调 → **重点补足** 事件循环、coroutine 不 await 不执行、`gather`/`TaskGroup`/`to_thread`、IO vs CPU 密集 |
| 6 | 上下文管理器 | `06_context_managers.py` | 文档仅列名 → **补足** `contextlib.contextmanager`、`__enter__/__exit__` 与异常抑制 |
| 7 | `Protocol`（对应 Java 接口） | `07_protocol.py` | 文档仅列名 → **补足** 结构化子类型 vs Java 名义子类型、`@runtime_checkable` |
| 8 | `__slots__` | `08_slots.py` | 文档仅列名 → **补足** 省内存原理、与 `dataclass(slots=True)` 结合 |
| 9 | f-string 高级用法 | `09_fstring.py` | 文档仅列名 → **补足** 格式说明符、对齐、`!r`、调试 `=` |
| 10 | 切片 | `10_slicing.py` | 文档仅列名 → **补足** `[start:stop:step]`、负步长反转、切片是浅拷贝 |

### 3.2 动作 2 · 工程规范（文档列出的 5 项，全部覆盖）

| 文档知识点 | 落地位置 | 说明 |
| --- | --- | --- |
| `pyproject.toml` 管理 | `pyproject.toml` | 单一配置文件统一 project / ruff / mypy / pytest |
| 虚拟环境 | 根 README「快速开始」 | `uv sync` 自动建 `.venv`；说明与 conda env 的分工 |
| `ruff` 格式化 + `mypy` 类型检查 | `pyproject.toml` + 三件套命令 | lint 规则含 `UP`（推动现代语法）、`B`（抓可变默认参数） |
| `pytest` 单测 | `tests/week01/` | 覆盖 10 个知识点、6 个坑、Excel 导出器 |
| `uv` 包管理 | 根 README + `pyproject.toml` | `uv sync` / `uv run` 标准流程；dev 依赖分组 |

### 3.3 文档列出的 6 个特有坑（全部覆盖，见 `pitfalls/six_pitfalls.py`）

| # | 文档坑 | 本工程补足的细节 |
| --- | --- | --- |
| 1 | 可变默认参数 | 文档给的 `items = items or []` 有语义缺陷：**传入空列表时也会被替换成新对象** → 补足 `if items is None` 的正确写法并举证 |
| 2 | `None` 检查用 `is None` | 补足 `is`（身份）vs `==`（相等）的原理、None 单例、小整数缓存陷阱 |
| 3 | 缩进即语法 | 补足 `IndentationError`/`TabError`、统一 4 空格、编辑器配置 |
| 4 | 鸭子类型 | 补足 EAFP vs LBYL 风格，并与 `Protocol` 静态检查联动 |
| 5 | 列表推导式 | 补足与生成器表达式的内存差异、何时不该用（可读性） |
| 6 | 字符串 `+=` 性能陷阱 | 补足 `str.join()` 正确写法与原理（字符串不可变 → 每次新建对象） |

### 3.4 对照文档补足的遗漏项（严格限定第 1 周范畴）

> 文档只列了 10 个差异点 + 6 个坑。以下为 Java 程序员转型高频卡点、且属于「Python 语法速成」范畴的补充，文档中未单列或描述不足：

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 类型注解**运行时不强制** | `01_type_annotations.py` | Java 程序员最大认知误区；类型注解不影响运行，需 mypy 才生效 |
| 闭包 **late-binding** 陷阱 | `pitfalls/extra_gotchas.py` | 循环中创建 lambda/函数捕获循环变量，结果全是最后一个值，Java 无此问题 |
| **浅拷贝 vs 深拷贝** / 列表别名 | `pitfalls/extra_gotchas.py` | 与坑 #1 同源，`list.copy()` 只复制一层；Java 的 `=` 语义迁移易错 |
| **EAFP vs LBYL** | `07_protocol.py` / `six_pitfalls.py` | Python 惯用"先做再捕获异常"，Java 惯用"先检查"，风格差异显著 |
| `asyncio.to_thread` 与线程池桥接 | `05_asyncio_await.py` | 文档动手项目要求 `asyncio + ThreadPoolExecutor`，须讲清二者如何协作 |
| 模块与包、绝对/相对导入 | `engineering/engineering_demo.py` | 对应 Java 的 package/import，是工程规范的实际痛点 |

## 四、验收标准（文档原文）与本地验证

- [x] `uv` 创建的项目能跑通 `ruff check` + `mypy` + `pytest` 三件套
  → `uv sync && uv run ruff check . && uv run mypy && uv run pytest`
- [x] Excel 导出器能跑，有单测
  → `uv run python -m week01.excel_exporter`，测试见 `tests/week01/test_excel_exporter.py`
- [ ] 能读懂 `fastapi` 官方教程的任意一节（**无需编码，属个人阅读任务**，留给你自己勾选）

## 五、坑提醒（文档原文，务必重视）

> `asyncio` 是 Python 后端最重要的技能点。LLM 调用是 IO 密集型，同步写法会让并发直接崩，**必须用异步** —— 这个点面试必问。

本工程的 `05_asyncio_await.py` 与 `excel_exporter/` 都围绕这一点设计，请重点看：
- coroutine 必须 `await` 才会执行（只创建不 await = 什么都没发生）；
- `asyncio.gather` 并发调度 IO，`asyncio.to_thread` 把阻塞的同步库（如 openpyxl）丢进线程池；
- CPU 密集任务用进程池/多线程并不提速（GIL），IO 密集才是 asyncio 的主场。
