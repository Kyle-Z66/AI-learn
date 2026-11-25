# 第 6 周：P1 收尾 + 阶段复盘

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 6 周。
> **本周严格限定在第 6 周范围内**：RAG 只做名词级预习（文档原文要求），解析/切分/嵌入都留到第 7 周。

## 一、学习目标（文档原文四任务）

> 这是第一阶段的收口周：把前五周的代码变成一个**能 docker-compose up 跑起来、
> 有接口、有文档、能讲清设计取舍**的项目，并完成阶段复盘与技术输出。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 5h | **P1 收尾**：FastAPI 暴露 REST 接口；Docker 化；写 README（架构图 + 快速开始 + 设计取舍） | `engineering/` + `p1_fastapi/` |
| 工作日 3h | **技术输出**：博客《从 Java AI 能力中心到 Python LLM 网关：一次能力平移》 | `p1_fastapi/BLOG.md` |
| 周末 4h | **阶段复盘**：阶段验收卡 + 复盘模板 | `STAGE_REVIEW.md` |
| 周末 4h | **补短板**：RAG 理论预习（第 7 周要用） | `core_mechanisms/10` —— 只列环节与输入输出 |

## 二、与第 1~5 周的衔接（覆盖已掌握内容，但不重复讲解）

| 第 1~5 周已掌握 | 第 6 周如何使用（不再重复讲解） |
| --- | --- |
| 第 1 周 `dataclass` / `asyncio` | FastAPI 路由全用 `async def`；容器用 dataclass，原理不再展开 |
| 第 2 周 Pydantic schema / 三厂商适配器 | 请求/响应模型复用 Pydantic v2；`get_provider` 继续做底层客户端 |
| 第 3 周 P1 网关 / 降级链 | HTTP 层只调 `P1Gateway.chat()`，**不重写网关逻辑** |
| 第 4 周 SSE 帧 / async 生成器 | `StreamingResponse` 直接复用 `encode_sse()` 与 `async for` |
| 第 5 周熔断 / 审计 / 成本 / 指标 | `/readyz` 读熔断状态；`/v1/chat` 写 19 字段审计；`/metrics` 出指标快照 |
| 第 5 周 19 字段审计 | 每个请求生成 trace_id，HTTP 层只补 user_id/scenario，不另造审计表 |

> **一句话递进关系**：前五周把网关"造出来、扛住流量、算清账"，第 6 周把它"交付出去"——
> 有 HTTP 接口、有容器、有架构图、有博客、有复盘，第一阶段才算闭环。

## 三、四个任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 5h | **P1 收尾** | [`engineering/`](engineering/) + [`p1_fastapi/`](p1_fastapi/) —— 路由 / DI / 健康检查 / Dockerfile / compose / 项目 README |
| 工作日 3h | **技术输出** | [`p1_fastapi/BLOG.md`](p1_fastapi/BLOG.md) —— Java → Python 能力平移叙事 |
| 周末 4h | **阶段复盘** | [`STAGE_REVIEW.md`](STAGE_REVIEW.md) + [`core_mechanisms/09`](core_mechanisms/) —— 验收卡与自评脚本 |
| 周末 4h | **补短板 / RAG 预习** | [`core_mechanisms/10`](core_mechanisms/) —— 九环节输入输出，仅名词级 |

可运行知识点共 10 个，见 [`core_mechanisms/`](core_mechanisms/) 的 01~10；
本周所有 HTTP 测试用 `httpx.ASGITransport`，**不需要启动端口、不需要 API Key**。

## 四、知识点对照表（文档原有 vs 对照补足）

### 4.1 动作 1 · P1 收尾（文档原文覆盖 + 落地口径）

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| FastAPI 暴露 REST 接口 | `01_fastapi_routes.py` / `engineering/app.py` | 文档仅列名 → **补足**应用工厂、路由清单、请求/响应模型分离 |
| Pydantic 请求响应校验 | `02_request_response_models.py` | 第 2 周已学 schema → 补足 HTTP 边界的校验位置与错误响应形态 |
| 依赖注入 `Depends` | `03_dependency_injection.py` | 文档未提 → **补足**容器单例与 `dependency_overrides` 测试替换 |
| 流式接口 | `04_streaming_response.py` | 第 4 周 SSE → **补足** `StreamingResponse` 与生成器对接 |
| 健康检查 | `05_health_readiness.py` | 文档未提 → **补足** liveness / readiness 区别，readiness 读熔断状态 |
| Docker 化 | `08_docker_config.py` / `p1_fastapi/Dockerfile` | 文档仅列名 → **补足**多阶段思路、非 root、密钥走环境变量 |
| README 架构图 / 取舍 | `p1_fastapi/README.md` | 文档点名要求 → Mermaid 架构图 + 接口表 + 5 条设计决策 |

### 4.2 动作 2~4 · 技术输出 / 复盘 / 预习

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| 技术博客 | `p1_fastapi/BLOG.md` | 文档给了标题 → 补足可复用的叙事结构：背景 → 平移映射 → 决策 → 数据 → 面试话术 |
| 阶段验收卡 | `STAGE_REVIEW.md` / `09_stage_checklist.py` | 文档给了 6 条 → 补足可运行自评脚本，逐条给证据 |
| 复盘模板四问 | `STAGE_REVIEW.md` | 文档给了模板 → 补一份填写示例，附 0~5 分自评 |
| RAG 理论预习 | `10_rag_preview.py` | 文档只说"开始预习" → **补足**九环节输入输出清单；明确第 7 周才实现 |

### 4.3 对照文档补足的遗漏项（严格限定第 6 周范畴）

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| ASGI 无端口异步测试 | `06_asgi_testing.py` | 文档要求单测覆盖率 >60%，不掌握 ASGITransport 就得起服务端口，CI 很难跑 |
| 覆盖率口径与门禁 | `07_coverage_gate.py` | 文档只写 >60%，没说行覆盖还是分支覆盖、怎么卡门禁 |
| 同步阻塞与异步路由边界 | `pitfalls/fastapi_pitfalls.py` | `async def` 里用 `time.sleep` 会阻塞事件循环，第 1 周 asyncio 知识在这里最易翻车 |
| 架构图 ≠ 代码目录树 | `pitfalls/extra_gotchas.py` | 面试看的是数据流与决策，不是文件清单 |
| Docker 密钥不进镜像 | `p1_fastapi/docker-compose.yml` | 文档没提；`.env` 注入是上线基本要求 |

## 五、验收标准（文档阶段验收卡）与本地验证

- [x] GitHub 上有一个能 docker-compose up 跑起来的 P1 项目
  → `p1_fastapi/Dockerfile` + `docker-compose.yml`；本地无 Docker 时用 ASGITransport 验证同一 app
- [x] README 含架构图、接口列表、关键设计决策
  → `p1_fastapi/README.md`，Mermaid 图 + 5 条决策
- [x] 有单测，覆盖率 > 60%
  → `tests/week06/` + `uv run pytest --cov=week06 --cov-report=term-missing --cov-fail-under=60`
- [x] 有一篇技术博客
  → `p1_fastapi/BLOG.md`
- [x] 能不看代码讲清 token 缓存策略、熔断降级链、成本核算模型
  → `STAGE_REVIEW.md` 的"面试自述"段 + 第 4/5 周对应样例
- [x] 能讲清 P1 和"只会调 API"的区别
  → `BLOG.md` 的"差异化"章节

三件套验收（与前几周相同）：

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest -q
uv run pytest --cov=week06 --cov-report=term-missing --cov-fail-under=60
```

## 六、坑提醒（文档原文 + 本周补足）

> 本周不发明新算法，重点在**交付形态**：接口、容器、文档、复盘。

- **`async def` 里别用 `time.sleep`**：阻塞事件循环，压测数据全废；用 `await asyncio.sleep`。
- **liveness 和 readiness 不是一回事**：前者"'我'活着"，后者"'我'能接客"；熔断打开时应让 readiness 失败。
- **流式接口别先把数据攒完**：`StreamingResponse` 要接 async 生成器，否则只是伪流式。
- **Docker 镜像里不能有 Key**：环境变量注入；compose 文件里的 `${VAR}` 不是硬编码。
- **覆盖率 60% 是线覆盖门禁**：分支覆盖另行统计，别把两个数字混着讲。
- **RAG 预习只看名词**：解析/切分是第 7 周任务，本周实现就越界了。
