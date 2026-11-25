# 从 Java AI 能力中心到 Python LLM 网关：一次能力平移

> 第 6 周技术输出。用途：面试时讲清"我做了什么、为什么这么做、和只会调 API 的区别"。
> 叙事主线：**不是换语言重写，而是把 Java 侧的可靠性经验平移成 Python 的可运行系统。**

## 1. 背景：我原来在做什么

在 Java 侧做过能力中心类的系统：统一接入多个下游、配置化路由、超时与重试、
调用审计与成本核算。这些概念并不陌生，缺的是把它们落到 Python + LLM 场景的具体写法。

于是我把学习计划的前六周当成一个完整项目来做：

| 周次 | 交付物 | 对应 Java 经验 |
| --- | --- | --- |
| 第 1 周 | Python 语法与 asyncio 样例 | 从 JVM 并发模型切到事件循环 |
| 第 2 周 | LLM API 原理 + 三厂商适配器 + Prompt 实验 | 多下游 SDK 的统一封装 |
| 第 3 周 | LangChain 抽象 + LCEL + P1 网关 v0.1 | 能力网关骨架 |
| 第 4 周 | Token 缓存 / SSE 流式 / 并发压测 | 缓存策略 + 流式响应 + 线程池 |
| 第 5 周 | 熔断 / 降级 / 重试幂等 / 审计成本 | Resilience4j + 审计表 |
| 第 6 周 | FastAPI / Docker / 文档 / 复盘 | 服务化交付与可观测 |

## 2. 能力平移映射表（面试可直接讲）

| Java 侧概念 | Python 落地 | 关键差异 |
| --- | --- | --- |
| `CompletableFuture` / 线程池 | `asyncio.gather` / `Semaphore` / `TaskGroup` | 单线程事件循环，IO 等待才让出；CPU 密集仍需进程池 |
| Feign / RestTemplate | OpenAI 兼容适配器 + `Protocol` |  Duck typing，接口靠协议约定而非显式 implements |
| Resilience4j CircuitBreaker | 自研三态熔断 + `asyncio.Lock` | 时钟必须用 `monotonic()`，并发计数要加锁 |
| `@Retryable` | 可重试判据 + full jitter + `Retry-After` | 错误分类要显式写，未知异常默认快速失败 |
| AOP 日志切面 | FastAPI 依赖注入 + 19 字段审计 | 在 HTTP 边界生成 trace_id，串起重试与降级 |
| EasyExcel 导出 | `openpyxl` + `ThreadPoolExecutor` + ZIP | 分片思路一致，GIL 下 IO 密集仍可用线程 |
| 配置项管理 | `pyproject.toml` + 环境变量 + 单价配置表 | 价格不写死，厂商调价只改配置 |

## 3. 架构与数据流

调用方 → FastAPI 边界校验 → P1Gateway 选模型 → Provider 适配器 → 厂商 API；
旁路写入熔断状态、审计记录与指标，再聚合出按 provider 的成本日报。

流式走 `StreamingResponse` + 第 4 周的 SSE 编码，非流式走统一 `ChatResponse`。
完整图和接口表见 [README.md](README.md)。

## 4. 三个最难的点

1. **熔断器的"能上线"版本**。文档给的标准写法能看懂原理，但直接抄会有三个坑：
   `time.time()` 受系统时钟影响、并发失败计数无锁、half_open 无限放行。
   修正版用可注入单调时钟 + `asyncio.Lock` + 单探针 + 成功阈值，
   因此 30 秒恢复窗口可以用假时钟在单测里瞬间走完。
2. **区分"暂时故障"和"确定错误"**。429/5xx/超时可重试，400/401 不可重试；
   指数退避要带抖动，服务端给了 `Retry-After` 就以它为准；非幂等写操作必须带业务幂等键，
   用随机 UUID 当键等于没做幂等。
3. **成本要记在实际模型上**。降级后调用的是备用 provider，
   如果还按首选模型单价算账，日报就是错的；缓存命中也要单独标注命中率，
   否则会误以为模型降价了。

## 5. 数据（本地 Mock 环境，非真实账单）

- 100 请求、单次 10ms 模拟 IO：串行 1555ms，`gather` 15.8ms，`Semaphore(10)` 156.7ms；
- 100 个并发首次取 token，击穿保护下只刷新 1 次；
- 审计 19 字段落 SQLite，按 trace 可查到失败 → 降级 → 成功完整链路；
- 单测：三件套全绿，覆盖率用 `--cov-fail-under=60` 卡门禁。

## 6. 面试叙事（30 秒版）

> 我把 Java 侧的能力网关经验平移成了 Python LLM 网关：统一三家模型适配器，
> 用 LCEL/网关做编排；缓存层处理 token 与并发，流式用 SSE 降首字节延迟；
> 稳定性层做了三态熔断、分级超时、可重试错误判据和幂等键；
> 每次调用落 19 字段审计并聚合按 provider 的成本日报。
> 最后用 FastAPI 暴露接口、Docker 交付，并写了架构决策与单测门禁。
> 和"只会调 API"的区别是：**我交付的是一套有指标、可降级、能算账的系统，不是一段调用代码。**

## 7. 边界与下一步

第一阶段到本周收口；RAG 只做了名词级预习。第 7 周开始进入检索侧：
文档解析、切分策略实验与检索质量评测——那才是下一场硬仗。
