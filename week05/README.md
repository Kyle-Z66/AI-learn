# 第 5 周：AI 网关的"硬骨头"——熔断、降级、审计、可观测

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 5 周。
> **本周严格限定在第 5 周范围内**：第 6 周 P1 收尾复盘不提前写；RAG/Agent 属于后续阶段。

## 一、学习目标（文档原文）

> 这是你 Java 侧最拿手的东西，**做成 P1 的核心竞争力**。面试时这段最能打。

本周把第 3 周的网关骨架升级成"能上线"的形态：三态熔断挡住雪崩、降级链保证有回答、
指数退避重试与幂等键防止放大故障、19 字段审计与日成本报表把每次调用讲清楚。
原理都来自你的 Java 经验，缺的只是 asyncio 与 Python 库的落地写法。

## 二、与第 1~4 周的衔接（覆盖已掌握内容，但不重复讲解）

| 第 1~4 周已掌握 | 第 5 周如何使用（不再重复讲解） |
| --- | --- |
| 第 1 周 `Protocol` / `dataclass` / `async with` | 熔断器的时钟与并发控制用可注入 clock + `asyncio.Lock`，Protocol 思路不再展开 |
| 第 1 周 `time` 与可变默认参数坑 | 文档熔断器标准写法用 `time.time()`，本周换成 `time.monotonic()` 并讲清原因 |
| 第 2 周错误分类（429/5xx 可重试） | 只复用判据结论，把 `is_retryable` 提升为可测试的独立策略，不重讲 API 原理 |
| 第 2 周三厂商适配器 + MockProvider | 降级链直接 `get_provider(..., use_mock=True)`，无需 Key；不重写适配层 |
| 第 3 周 P1 网关 / 降级链 / 成本公式 | 本周在网关外层加熔断、重试、审计；`calculate_cost` 直接复用 |
| 第 4 周 `TaskGroup` / `Semaphore` / 令牌桶 | 明确区分：限流管"放多少进来"，熔断管"还敢不敢放"，本周只补后者 |
| 第 4 周 Token 缓存安全边界 | 缓存命中会低估成本，成本报表必须按真实调用记录统计（见 extra_gotchas） |

> **一句话递进关系**：第 3 周让网关能跑，第 4 周让它扛住流量，第 5 周让它在故障时**不崩、可查、可算账**。

## 三、三个任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | **熔断 + 降级** | [`core_mechanisms/01`~`03`](core_mechanisms/) + [`engineering/circuit_breaker.py`](engineering/circuit_breaker.py) + [`engineering/timeouts.py`](engineering/timeouts.py) —— 三态 / 单探针 / 降级链 / 三层超时 |
| 工作日 4h | **重试 + 幂等** | [`core_mechanisms/04`~`06`](core_mechanisms/) + [`engineering/retry.py`](engineering/retry.py) —— 错误分类 / 指数退避 / Retry-After / 幂等键 |
| 周末 8h | **审计 + 成本核算** | [`core_mechanisms/07`~`09`](core_mechanisms/) + [`audit_lab/`](audit_lab/) —— 19 字段 / SQLite 落库 / 按天按 provider 报表 |
| 贯穿 | **可观测 + 认知误区** | [`core_mechanisms/10`](core_mechanisms/) + [`engineering/metrics.py`](engineering/metrics.py) + [`pitfalls/`](pitfalls/) —— TTFT / 分位数 / 文档代码缺陷 |

> 全部样例无需 API Key、无需外部服务：审计用标准库 `sqlite3` 内存库，成本单价是配置里的教学示意值。

## 四、知识点对照表（文档原有 vs 对照补足）

### 4.1 动作 1 · 熔断 + 降级（文档原文覆盖 + 标准写法修正）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 三态熔断 closed/open/half-open | `01_circuit_breaker_states.py` | 文档给了完整代码 → 保留状态机语义，**补足**可注入时钟与可测试状态快照 |
| 连续失败触发 open，超时后试探 | `01` / `tests/week05` | 文档写了 `time.time()` → **修正**为 `time.monotonic()`，系统改时钟不会误判 |
| 半开态试探恢复 | `02_half_open_probe.py` | 文档 `half_open` 直接 `return True` → **补足**单探针 + 成功阈值，避免恢复瞬间被打爆 |
| 多模型降级链 | `03_degradation_chain.py` | 文档仅列名 → 复用第 3 周 Registry 思路，叠加"熔断打开就跳过该 provider" |
| connect / read / 总超时区分 | `04_timeout_layers.py` | 文档加粗强调 → **补足**三层预算校验、各自抛错位置与"预算偏紧"提示 |

### 4.2 动作 2 · 重试 + 幂等（文档原文覆盖 + 落地口径）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 429 / 5xx / 超时可重试 | `05_retryable_errors.py` | 文档给了分类 → **补足**未知异常默认不重试、`HttpStatusError` 结构化携带状态码 |
| 指数退避重试 | `06_exponential_backoff.py` | 文档仅列名 → **补足**full jitter 防重试风暴、退避上限、注入 sleep 便于测试 |
| 400 / 鉴权失败不可重试 | `05_retryable_errors.py` | 文档给了结论 → 落地为 `is_retryable()` 判据并单测 |
| `Retry-After` 响应头 | `06` / `engineering/retry.py` | 文档未提 → **补足**：服务端明确告知时以它为准，不能比客户端退避更短 |
| 写库/订单要幂等键 | `07_idempotency_key.py` | 文档点名要求 → **补足**键的构造方法（业务标识哈希，不是随机 UUID）与 TTL 去重 |

### 4.3 动作 3 · 审计 + 成本核算（文档原文覆盖 + 4 条验收）

| 文档知识点 / 验收 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 请求/响应/耗时/token/成本/状态全量落库 | `08_audit_fields.py` | 文档建议对齐 `AiExecuteLogs` 19 字段 → 给出 19 字段 dataclass + SQLite 存储 |
| 成本按 provider 差异化计算 | `09_cost_aggregation.py` | 文档仅列名 → 复用第 3 周 `calculate_cost`，按 provider 单价表计算 |
| 按天 / 按 provider 聚合报表 | `audit_lab/` | 文档要求"成本日聚合报表" → 实现 `build_daily_report()` 与可运行入口 |
| 审计表能查到完整链路 | `audit_lab/__main__.py` | 文档验收 → 用 trace_id 串起重试/降级/失败，`find_by_trace()` 直接查 |
| 可观测指标清单 | `10_observability_metrics.py` | 文档给了四类指标 → **补足** TTFT 采集点与 p50/p95/p99 的 nearest-rank 口径 |

### 4.4 对照文档补足的遗漏项（严格限定第 5 周范畴）

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 文档熔断器代码三个缺陷 | `pitfalls/resilience_pitfalls.py` | `time.time()` 非单调、无并发保护、half_open 无限放行；直接抄会出生产事故 |
| 熔断 ≠ 限流 ≠ 降级 | `pitfalls/extra_gotchas.py` | 第 4 周刚学令牌桶，三者最易混；本周给出判定表 |
| 审计日志脱敏 | `engineering/audit.py` | 请求/响应原文可能含密钥与手机号，落库前必须脱敏 |
| 代理请求的成本归因 | `pitfalls/extra_gotchas.py` | 缓存命中、降级换模型会让"按首选单价估算"失真 |
| 分位数计算口径 | `engineering/metrics.py` | p95 有 nearest-rank 与插值两种口径，不说明无法对齐监控 |

## 五、验收标准（文档原文）与本地验证

- [x] 熔断器有单测（连续失败 → open → 超时 → half_open → 恢复）
  → `tests/week05/test_engineering.py`，用可注入时钟驱动，无需真的 sleep 30 秒
- [x] 降级链实测有效（手动 mock 一个 provider 挂掉，验证自动切换）
  → `uv run python -m week05.core_mechanisms.03_degradation_chain`
- [x] 审计表能查到每一次调用的完整链路
  → `uv run python -m week05.audit_lab`，按 trace_id 打印同一链路的全部记录
- [x] 有一个成本报表接口，能按天/按 provider 聚合
  → `uv run python -m week05.audit_lab` 打印报表；接口在 `engineering/cost_report.py`

三件套验收（与前几周相同）：

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest -q
```

## 六、坑提醒（文档原文 + 本周补足）

> 本周不是学新名词，而是把你 Java 侧的 Resilience4j / Sentinel 经验写成 asyncio 版本。

必须记住的几条：
- **别抄文档的 `time.time()`**：单调时钟才能安全计算恢复时间；可注入 clock 才能单测。
- **half_open 不是"全放"**：只允许受控探针，成功到阈值才 closed，否则恢复瞬间二次雪崩。
- **退避必须带抖动**：所有客户端同一时刻重试会形成重试风暴，压垮刚恢复的服务。
- **不是所有错误都值得重试**：400/401/404 重试多少次都是浪费；未知异常默认快速失败。
- **非幂等调用重试必须带幂等键**：键来自业务标识，不能用每次都变的随机 UUID。
- **超时要分层**：connect / read / total 三层预算；total 偏小时要显式确认，不能默默生效。
- **审计要脱敏、成本要按实际模型算**：降级后的 provider 才是真实账单主体。
