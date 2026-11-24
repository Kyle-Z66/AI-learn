# 第 3 周：LangChain 基础 + P1 项目启动

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 3 周。
> 本章节的可直接接入原计划的文档版见 [`第3周知识点补充.md`](第3周知识点补充.md)。
> **本周严格限定在第 3 周范围内**：流式/并发是第 4 周，熔断/审计/可观测是第 5 周，Agent/StateGraph 动手是第 13/14 周。

## 一、学习目标（文档原文）

> 搞懂 LangChain 的核心抽象，把 P1 网关的骨架搭起来。

本周是**从"手写调用"迈向"框架化编排"的第一周**。第 2 周你已经能用原生 SDK 调通三家模型、用 Pydantic 约束输出；这一周解决的是新问题：当组件变多、链路变长，靠手写胶水代码会迅速失控。LangChain 的 5 个抽象和 LCEL 就是来解决这个问题的。

## 二、与第 1、2 周的衔接（覆盖已掌握内容，但不重复讲解）

| 第 1 / 2 周已掌握 | 第 3 周如何使用（不再重复讲解） |
| --- | --- |
| 第 1 周 `Protocol` / 鸭子类型（`07_protocol.py`） | `LLMProvider` 协议直接沿用，本周只在上面加统一响应与降级链，不重讲 Protocol 语法 |
| 第 1 周 `asyncio` / `await` / `gather`（`05_asyncio_await.py`） | LCEL 的 `ainvoke` 直接沿用异步写法；事件循环与并发原理不再展开 |
| 第 1 周 `dataclass` / 类型注解 / `pytest` / `ruff` / `mypy` | 用于 `LLMResponse` / `GatewayConfig` 定义与三件套验收，写法不再解释 |
| 第 2 周三厂商适配器 `get_provider()` / `ChatResponse`（`provider_adapters.py`） | P1 网关**直接 import 复用**，不重写 HTTP 调用、不重写三家 base_url |
| 第 2 周 Pydantic schema `TicketExtract`（`structured_output/models.py`） | `JsonOutputParser` 直接绑定该 schema，不重复定义字段与约束 |
| 第 2 周"错误回灌 → 最多 3 次重试" | 上升为网关降级链中的一环，重试逻辑不重写，只做编排 |
| 第 2 周模型路由与成本概念（`08_model_routing.py`） | 本周落为"配置切换 + 降级链 + 成本打印"的骨架，深化留到第 5 周 |
| uv / pyproject.toml | 新增 `langchain` / `langchain-core` 依赖，仍用 `uv add` 管理 |

> **一句话递进关系**：第 1 周给你语言工具，第 2 周让你能调模型，第 3 周把这些能力组装成可编排、可切换、可扩展的网关骨架。

## 三、三个任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | **LangChain 核心抽象** | [`core_abstractions/01`~`06`](core_abstractions/) —— 5 个抽象 + LCEL 组合原理 |
| 工作日 4h | **2026 现状确认** | [`pitfalls/`](pitfalls/) + [`engineering/gateway_protocol.py`](engineering/gateway_protocol.py) —— 版本陷阱、`create_agent` vs `StateGraph` 边界、import 路径 |
| 周末 8h | **P1 启动** | [`p1_gateway/`](p1_gateway/) —— 多模型统一网关 v0.1（骨架） |
| 贯穿 | **复用前两周成果** | [`engineering/provider_registry.py`](engineering/provider_registry.py) —— 导入第 2 周适配器，做注册表与降级链 |

> 无 API Key 也能跑：所有样例复用第 2 周的 `MockProvider`，LangChain 侧用 `FakeListChatModel` 等本地模型类，不发起真实请求。

## 四、知识点对照表（文档原有 vs 对照补足）

### 4.1 动作 1 · LangChain 五个核心抽象

| # | 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- | --- |
| 1 | Runnable | `01_runnable.py` | 文档仅列名 → **补足** 它是"协议"而非可实例化类；`invoke`/`ainvoke`/`stream`/`batch` 四种调用方式；为何被第 1 周的 `Protocol` 类比 |
| 2 | ChatModel | `02_chat_model.py` | 文档仅列名 → **补足** `init_chat_model` 统一入口、国内厂商 OpenAI 兼容端点必须带 `/v1`、Mock 与真实客户端同接口 |
| 3 | PromptTemplate | `03_prompt_template.py` | 文档仅列名 → **补足** `from_messages` 用法、花括号 `{{ }}` 转义、变量注入与消息顺序 |
| 4 | OutputParser | `04_output_parser.py` | 文档仅列名 → **补足** 与第 2 周 Pydantic schema 的对接方式；Parser 只解析不保证模型输出合法，重试仍走第 2 周逻辑 |
| 5 | Retriever | `05_retriever.py` | 文档仅列名 → **补足** 本周只认 `invoke(query)` 接口；向量库/切分/Rerank 是第 7~10 周，明确不越界 |

### 4.2 动作 1 · 对照补足的关键原理

| 补足知识点 | 样例文件 | 为什么必须补 |
| --- | --- | --- |
| LCEL 组合原理 | `06_lcel_chain.py` | 文档只列 5 个抽象名，没讲它们如何拼起来；`\|` 生成 `RunnableSequence`、`RunnableParallel`、`RunnableLambda` 是理解"万物皆 Runnable"的关键 |
| `ainvoke` 与同步阻塞的陷阱 | `06_lcel_chain.py` | 链上任一环阻塞则异步优势失效，与第 1 周 asyncio、第 4 周并发直接相关 |
| import 三层路径 | `pitfalls/langchain_pitfalls.py` | `langchain_core`（稳定契约）/ `langchain`（高层封装）/ `langchain_community`（社区集成），照抄旧博客是本周最高频翻车点 |
| `create_agent` vs `StateGraph` 边界 | `pitfalls/langchain_pitfalls.py` | 文档只给了结论没给判据；补五维速查表，本周只记边界不动手 |
| 废弃清单 | 同上 | `LLMChain` / `AgentExecutor` / 旧 memory 类全部废弃，见到即判为过期教程 |

### 4.3 动作 2 · 2026 现状确认（文档"版本陷阱"原文全部覆盖）

| 文档原文要求 | 落地位置 | 说明 |
| --- | --- | --- |
| 简单 Agent → `create_agent` | `pitfalls/langchain_pitfalls.py` | 给出适用边界与"本周不动手"的明确指示 |
| 复杂流程 → `StateGraph` | 同上 | 对应你 RPA 流程编排场景，动手留到第 14 周 |
| 不要用旧 `LLMChain` / `AgentExecutor` / 旧 memory | 同上 | 列出识别特征，避免照抄旧教程 |
| 面试能说清 harness vs graph | `week03/README.md` 坑提醒 | 五维对照表可直接复述 |

### 4.4 动作 3 · P1 多模型统一网关 v0.1（文档目标逐条覆盖）

| 文档要求 | 落地文件 | 说明 |
| --- | --- | --- |
| `LLMProvider(Protocol)` 统一抽象 | `engineering/gateway_protocol.py` | 复用第 1 周 Protocol + 第 2 周适配器接口，不重写 |
| `QwenProvider` / `DeepSeekProvider` / `ZhipuProvider` | `engineering/provider_registry.py` | **直接复用第 2 周已写好的三个适配器**，只做注册与配置切换 |
| 基于配置切换 + 降级链 | `p1_gateway/gateway.py` | 最小骨架：优先级列表 + `try/except`；熔断/健康检查/审计留到第 5 周 |
| 统一响应：内容、token、耗时、成本 | `p1_gateway/models.py` | `LLMResponse` dataclass；成本公式 `输入token/1000×单价 + 输出token/1000×单价`，单价从配置读不硬编码 |

## 五、验收标准（文档原文）与本地验证

- [ ] 能用一句话说清 Runnable / ChatModel / PromptTemplate / Parser / Retriever 各自职责
  → `core_abstractions/01`~`05` 头部总览表 + 各文件示例
- [ ] P1 v0.1 能用同一套代码调通 3 个模型，有成本打印
  → `uv run python -m week03.p1_gateway`；Mock 模式三家全通，真实调用**需你自己配 Key 后勾选**
- [ ] 能说清 `create_agent` 和 `StateGraph` 的适用边界
  → `pitfalls/langchain_pitfalls.py` 五维对照表
- [ ] 能用 LCEL 写出一条 `prompt | model | parser` 链，并说清 `invoke` 与 `ainvoke` 的区别
  → `uv run python -m week03.core_abstractions.06_lcel_chain`（本周补足项）

三件套验收（与前两周相同）：

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest -q
```

## 六、坑提醒（文档原文 + 本周补足）

> 本周的核心不是"学会 LangChain 的 API"，而是理解**抽象的价值**：5 个抽象把"调模型、拼提示、解析输出、召回文档"切成可组合的标准件，LCEL 让它们能被同一套协议编排。你 Java 侧做服务编排的经验在这里可以直接平移。

必须记住的几条：
- **不要照抄旧教程的 import**：`LLMChain`、`AgentExecutor`、旧 memory 类全部废弃；优先从 `langchain_core` 导入稳定契约。
- **Runnable 是协议不是类**：别写 `Runnable()`；任何实现 `invoke`/`ainvoke` 的组件都能被 `|` 串起来。
- **PromptTemplate 别手写字符串拼接**：花括号转义和变量注入都会出错，用 `from_messages` / `from_template`。
- **本周别扎进 Retriever 实现**：向量库、切分、Rerank 是第 7~10 周，这周只认 `invoke(query)` 接口。
- **别推翻第 2 周代码重写网关**：正确做法是复用适配器、套协议与配置切换；重复造轮子会吃掉你前两周的产出。
- **熔断/审计/可观测不是本周任务**：P1 v0.1 只要骨架干净、下周能往上加东西，宁可功能少也要接口清晰。
