# 第 4 周：Token 生命周期 + 流式 + 并发（对齐你的 Java 经验）

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 4 周。
> **本周严格限定在第 4 周范围内**：熔断、健康检查、调用审计与可观测是第 5 周，本周只做缓存/流式/并发三件事。

## 一、学习目标（文档原文）

> 把你在 Java 侧做过的 Token 管理、流式处理、并发控制平移到 Python。**这是你最快建立优势的一周。**

本周是你把 Java 老本行换算成 Python 新战场的一周：过期时间预留安全边界、缓存击穿保护、SSE 流式响应、令牌桶限流——这些概念你都熟，缺的只是 Python/asyncio 的落地写法。

## 二、与第 1、2、3 周的衔接（覆盖已掌握内容，但不重复讲解）

| 第 1~3 周已掌握 | 第 4 周如何使用（不再重复讲解） |
| --- | --- |
| 第 1 周 `asyncio` / `await` / `gather`（`05_asyncio_await.py`） | 本周主战场：`Semaphore` / `TaskGroup` / async 生成器直接沿用异步写法，事件循环原理不再展开 |
| 第 1 周 `Protocol` / `dataclass` / 上下文管理器 | TokenCache 后端抽象用 Protocol；`BenchmarkResult` 用 dataclass；锁用 `async with` |
| 第 1 周"可变默认参数"坑 | 文档给的 `RateLimiter` 标准写法恰好踩了这个坑，本周修正并讲清原因（见 4.3） |
| 第 2 周 tokenization / 上下文窗口 | **必须区分**：第 2 周的 token 是 LLM 分词单位；本周的 Token 是 API `access_token`，两者不是一回事 |
| 第 2 周 `temperature` / streaming 原理（`04_streaming.py`） | 本周把"流式"落到 SSE 帧与 async 生成器，不再重复首 token 延迟等概念 |
| 第 3 周 P1 网关（配置切换 + 降级 + 响应对象） | 本周把缓存/流式/并发作为"周边件"加到网关思路上，**不修改 week03 代码**，只在 engineering 层做增量示范 |
| 第 3 周 `MockProvider` / 三厂商适配器 | 压测用本地 Mock 异步调用模拟 LLM IO，无需 API Key；真实网关调用沿用第 3 周适配器 |

> **一句话递进关系**：第 1 周给你 asyncio，第 2 周让你懂 LLM 的不确定性，第 3 周搭好网关骨架，第 4 周让这个骨架扛住真实流量——缓存省 token、流式降延迟、并发提吞吐。

## 三、三个任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | **Token 缓存** | [`core_mechanisms/01`~`03`](core_mechanisms/) + [`engineering/token_cache.py`](engineering/token_cache.py) —— TTL / 安全边界 / 击穿保护 |
| 工作日 4h | **流式输出** | [`core_mechanisms/04`~`06`](core_mechanisms/) + [`engineering/sse.py`](engineering/sse.py) —— async 生成器 / SSE 帧 / LangChain 流式 |
| 周末 8h | **并发压测** | [`core_mechanisms/07`~`10`](core_mechanisms/) + [`concurrency_lab/`](concurrency_lab/) —— gather / Semaphore / TaskGroup / 令牌桶 + 100 请求对比表 |
| 贯穿 | **认知误区** | [`pitfalls/`](pitfalls/) —— Token 概念混淆、文档标准写法缺陷等本周特有坑 |

> 无 Redis 服务、无 API Key 也能跑：Token 缓存默认内存后端，压测与流式全部本地模拟；配置环境变量后可切真实 Redis。

## 四、知识点对照表（文档原有 vs 对照补足）

### 4.1 动作 1 · Token 缓存（文档原文三条动作全部覆盖）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| Redis + TTL 缓存 access_token | `01_token_cache_ttl.py` | 文档仅列名 → **补足** TTL 存储/读取/过期判定；Redis 后端 + 内存后端双实现，无服务也能跑 |
| 过期时间预留安全边界 | `02_safety_margin.py` | 文档给了 `expireIn - 1000` 提示 → **补足** 通用公式 `有效TTL = 官方过期时间 - 安全余量`，以及余量太小/太大的代价 |
| 缓存击穿保护（分布式锁） | `03_cache_stampede.py` | 文档仅列名 → **补足** `asyncio.Lock` 单进程保护 + 双重检查；Redis `SET NX EX` 分布式锁思路（第 5 周展开完整版） |

### 4.2 动作 2 · 流式输出（文档原文三条动作全部覆盖）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| `async` 生成器 `yield` | `04_async_generator.py` | 文档仅要求"理解用法" → **补足** 生成器与协程的区别、`async for` 消费、提前关闭要 `aclose()` |
| SSE（Server-Sent Events） | `05_sse_frames.py` | 文档仅列名 → **补足** 帧格式 `data: ...\n\n`、粘包/跨包处理、`id`/`event`/`retry` 字段 |
| 前端 `EventSource` / fetch 接收 | `05_sse_frames.py` | 文档提到但未落地 → **补足** 两种接收方式的代码形态与适用差异 |
| LangChain 流式接入 | `06_langchain_stream.py` | 第 3 周学到 LCEL → **补足** `astream()` 与 `stream()` 的接法；不重复第 2 周首 token 延迟概念 |

### 4.3 动作 3 · 并发压测（文档标准写法 + 4 条验收）

| 文档知识点 / 验收 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| `asyncio.gather` | `07_gather_vs_serial.py` | 文档要求并发 vs 串行对比 → **补足** 100 请求量化数据，输出对比表 |
| `asyncio.Semaphore` | `08_semaphore.py` | 文档要求并发控制 → **补足** 限流为何必须配 Semaphore：无限并发会被厂商 429 |
| `asyncio.TaskGroup` | `09_taskgroup.py` | 验收标准点名 → **补足** 与 `gather` 的错误传播差异（TaskGroup 首个异常会取消兄弟任务） |
| 令牌桶 `RateLimiter` | `10_rate_limiter.py` / `engineering/rate_limiter.py` | **文档标准写法有两处缺陷**：`_lock: asyncio.Lock = None` 踩第 1 周可变默认参数坑；`get_event_loop().time()` 在无运行循环时会报错 → 本工程给修正版并解释 |
| 100 请求耗时对比表 | `concurrency_lab/` | 文档要求"量化吞吐差异" → 串行 / gather / Semaphore 三档对比 + 倍数 |

### 4.4 对照文档补足的遗漏项（严格限定第 4 周范畴）

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| access_token ≠ LLM token | `pitfalls/concurrency_pitfalls.py` | 文档同时出现第 2 周 tokenization 与本周 Token 缓存，最易混淆；不澄清会导致知识串线 |
| 文档令牌桶代码的两处缺陷 | `10_rate_limiter.py` | `asyncio.Lock` 要用 `field(default_factory=...)`；`get_event_loop()` 要换 `get_running_loop()` |
| SSE 粘包/跨包 | `engineering/sse.py` | 一帧可能跨多个 TCP 包，也可能一包多帧；按行缓冲才能正确还原事件 |
| 缓存击穿 vs 缓存穿透 vs 缓存雪崩 | `pitfalls/extra_gotchas.py` | 文档只提击穿，三者常被混为一谈；本周只做认知对照 |
| 异步生成器的资源释放 | `04_async_generator.py` | 提前 `break` 不 `aclose()` 会泄漏生成器，生产代码必须注意 |

## 五、验收标准（文档原文）与本地验证

- [x] Token 缓存有 Redis 实现 + 单元测试（含并发击穿测试）
  → `engineering/token_cache.py` 双后端；`tests/week04/test_engineering.py` 含并发击穿用例（无 Redis 服务时用内存后端跑）
- [x] 流式接口能真的一字一字吐出来
  → `uv run python -m week04.concurrency_lab` 之外的流式样例：`uv run python -m week04.core_mechanisms.05_sse_frames`
- [x] 并发压测有数据：并发 N 相比串行的耗时对比表
  → `uv run python -m week04.concurrency_lab`，直接打印对比表
- [x] 掌握 `asyncio.Semaphore` / `asyncio.gather` / `asyncio.TaskGroup` 的区别与用法
  → `core_mechanisms/07`~`09` 三个脚本 + `pitfalls/` 边界对照

三件套验收（与前几周相同）：

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest -q
```

## 六、坑提醒（文档原文 + 本周补足）

> 本周不是"学新概念"，而是**把你 Java 侧已经会的可靠性手段翻译成 asyncio 版本**。过期时间安全边界、击穿保护、令牌桶，原理都在，变的只是 API。

必须记住的几条：
- **两种 Token 别混**：第 2 周 tokenization 的 token 是文本分词单位；本周 Token 是 API 访问凭证，会过期、要缓存。
- **`expireIn - 1000` 的思想比数字重要**：任何"提前续期"都要留安全余量，否则请求正好撞上过期。
- **文档给的令牌桶代码不能直接抄**：`asyncio.Lock` 的可变默认值与 `get_event_loop()` 都是坑，修正版见 `10_rate_limiter.py`。
- **并发不等于无限 gather**：不加 `Semaphore` 的 100 并发会直接把厂商配额打满（429），压测里要体现这个差异。
- **SSE 不能按"一次 read = 一帧"处理**：要按 `\n\n` 缓冲切帧，否则粘包时解析出错。
- **熔断与审计是第 5 周**：本周的降级链沿用第 3 周骨架，不提前实现熔断。
