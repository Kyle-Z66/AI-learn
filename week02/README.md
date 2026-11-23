# 第 2 周：LLM API 基础与 Prompt 工程

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第一阶段 / 第 2 周。
> **本周严格限定在第 2 周范围内**，不触碰第 3 周的 LangChain / P1 网关。

## 一、学习目标（文档原文）

> 理解 LLM 的"非确定性"，掌握调用、参数、结构化输出、Prompt 设计。

本周是**第一次真正调用大模型**。与第 1 周"工程能力平移"不同，这一周的核心是建立对 LLM 行为方式的直觉：它不确定、会犯错、需要被约束。

## 二、与第 1 周的衔接（不重复已掌握内容）

| 第 1 周已掌握 | 第 2 周如何使用（不再重复讲解） |
| --- | --- |
| `asyncio` / `await` / `gather` | 所有模型客户端都是 async，直接沿用并发写法（见 `05_asyncio_await.py`） |
| 类型注解 / `dataclass` / Pydantic 前置 | 用 Pydantic 定义输出 schema，类型注解写法不再展开 |
| `Protocol` / 鸭子类型 | 统一 LLM 客户端接口 `LLMProvider` 沿用第 1 周 `07_protocol.py` 的模式 |
| 上下文管理器 | `with ThreadPoolExecutor` / HTTP 客户端生命周期沿用 |
| pytest / ruff / mypy 三件套 | 测试写法沿用；新增 async 测试（`asyncio_mode=auto` 已配好） |
| uv / pyproject.toml | 新增 `pydantic` / `openai` 依赖，用 `uv add` 管理（见根 README） |

## 三、四个具体任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 5h | **模型 API 原理** | [`api_fundamentals/01`~`09`](api_fundamentals/) —— 8 个文档原理点 + 1 个补足核心点 |
| 工作日 3h | **国内模型接入** | [`engineering/provider_adapters.py`](engineering/provider_adapters.py) + [`engineering_demo.py`](engineering/engineering_demo.py) —— 三厂商适配器 + Mock |
| 周末 4h | **Prompt 工程实战** | [`prompt_lab/`](prompt_lab/) —— 10 个 Prompt 版本对比实验 + [`REPORT.md`](prompt_lab/REPORT.md) |
| 周末 4h | **结构化输出** | [`structured_output/`](structured_output/) —— Pydantic schema + 错误回灌重试 |
| 贯穿 | **非确定性认知** | [`pitfalls/`](pitfalls/) —— LLM 特有坑与认知误区 |

> 无 API Key 也能跑：所有样例默认提供 `MockProvider`（规则化模拟响应），可选配置真实 Key 调三家 API。
> 环境变量名：`DASHSCOPE_API_KEY`（通义千问）、`DEEPSEEK_API_KEY`（DeepSeek）、`ZHIPU_API_KEY`（智谱 GLM）。

## 四、知识点对照表（文档原有 vs 对照补足）

### 4.1 动作 1 · 模型 API 原理

| # | 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- | --- |
| 1 | tokenization | `01_tokenization.py` | 文档仅列名 → **补足** BPE 合并原理、中文 token 与字符的关系、token 数与计费的直接关系 |
| 2 | 上下文窗口 | `02_context_window.py` | 文档仅列名 → **补足** 输入+输出共享同一窗口、超限截断策略、`max_tokens` 预留 |
| 3 | temperature/top_p/max_tokens | `03_sampling_params.py` | 文档仅列名 → **补足** 两者同时生效时的相互作用、抽取类任务为何设 0 仍需重试、`finish_reason=length` 截断识别 |
| 4 | streaming | `04_streaming.py` | 文档仅列名 → **补足** SSE 数据帧格式、首 token 延迟 vs 总延迟、 stream 下如何拿用量 |
| 5 | function calling | `05_function_calling.py` | 文档仅列名 → **补足** tool 定义与 `tool_choice`、**与结构化输出的区别**（模型选工具 vs 强制格式） |
| 6 | system/user/assistant 角色 | `06_roles.py` | 文档仅列名 → **补足** system 优先级、消息顺序、多轮对话如何拼 messages |
| 7 | cache prompt | `07_prompt_caching.py` | 文档仅列名 → **补足** 前缀匹配命中条件、为何动态内容要放末尾、命中率与成本 |
| 8 | 模型路由 | `08_model_routing.py` | 文档仅列名 → **补足** 降级链基础（第 3 周 P1 网关会展开，本周只做路由开关与成本对比） |
| 9 | **非确定性**（文档目标核心，未单列） | `09_non_determinism.py` | **补足**：同一 Prompt 多次结果不同、`temperature=0` 也非绝对确定（浮点/批处理差异）、工程上如何应对 |

### 4.2 动作 2 · 国内模型接入（文档列出的 3 家）

| 文档知识点 | 落地位置 | 说明 |
| --- | --- | --- |
| 通义千问 `qwen-plus` | `engineering/provider_adapters.py` | OpenAI 兼容模式接入，环境变量 `DASHSCOPE_API_KEY` |
| DeepSeek `deepseek-chat` | 同上 | 环境变量 `DEEPSEEK_API_KEY` |
| 智谱 GLM `glm-4-plus` | 同上 | 环境变量 `ZHIPU_API_KEY` |
| 价格与上下文差异 | `engineering_demo.py` 输出 + 代码 `ModelConfig` | **价格随厂商调整，不硬编码具体数字**；代码固化接入方式，价格/窗口以各厂商官网为准，输出中给出查询入口 |

### 4.3 动作 3 · Prompt 工程实战（文档要求 10 个版本）

`prompt_lab/prompts.py` 定义 10 个版本，同一任务：**从技术文档抽取结构化信息**。变化维度见下表，实验结果见 `REPORT.md`。

| 版本 | 变化维度 | 版本 | 变化维度 |
| --- | --- | --- | --- |
| v01 | 裸指令（零样本） | v06 | 输出格式显式约束（JSON schema 描述） |
| v02 | 加角色设定 | v07 | 负向约束（禁止猜测、字段缺失填 null） |
| v03 | 加任务背景 | v08 | 少样本示例（2-shot） |
| v04 | 分步指令（类 CoT） | v09 | 分隔符包裹输入（防注入） |
| v05 | 字段逐一说明 | v10 | 综合版（v02+v06+v07+v08+v09） |

### 4.4 动作 4 · 结构化输出（文档标准写法全部覆盖）

| 文档要求 | 落地文件 | 说明 |
| --- | --- | --- |
| Pydantic 定义输出 schema | `structured_output/models.py` | `TicketExtract` + `Field` 约束 + `extra="forbid"` |
| 强制模型返回 JSON | `structured_output/extractor.py` | `response_format={"type": "json_object"}` + `temperature=0` |
| 解析失败 → 回灌错误原因 → 最多 3 次 | 同上 | `ValidationError` 文本拼进下一轮 user 消息，而非盲目重试 |

### 4.5 对照文档补足的遗漏项（严格限定第 2 周范畴）

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| `temperature=0` 不等于绝对确定 | `09_non_determinism.py` / `pitfalls/` | 文档目标强调"非确定性"，但正文未展开；这是生产系统必须建立的认知 |
| 可重试错误 vs 不可重试错误 | `structured_output/extractor.py` | 429/5xx 可重试，400 参数错误重试无用；文档只写了捕获 `ValidationError` |
| `finish_reason` 检查 | `03_sampling_params.py` / `pitfalls/` | `max_tokens` 截断不会报错，必须看 `finish_reason` 才知道输出不完整 |
| streaming 的用量统计 | `04_streaming.py` | 流式响应默认不返回 usage，需显式 `stream_options` |
| function calling vs 结构化输出 | `05_function_calling.py` | 两者都返回 JSON，但语义不同（选工具 vs 守格式），最易混淆 |
| prompt cache 前缀稳定性 | `07_prompt_caching.py` | 动态内容放前面会导致缓存永远不命中，文档未提 |

## 五、验收标准（文档原文）与本地验证

- [ ] 三个国内模型 API 全部跑通，有代码可展示
  → `engineering/provider_adapters.py` 三家适配器就位；**需你自己配置 Key 后勾选**（无 Key 时 Mock 全通）
- [x] 用 Pydantic + 重试机制跑通结构化提取，错误可恢复
  → `uv run python -m week02.structured_output`，测试见 `tests/week02/test_structured_output.py`
- [x] 写出一份"Prompt 版本对比实验报告"（哪个版本更稳、为什么）
  → [`prompt_lab/REPORT.md`](prompt_lab/REPORT.md)

三件套验收（与第 1 周相同）：

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest -q
```

## 六、坑提醒（文档原文 + 本周补足）

> 本周的核心不是"学会调 API"，而是理解**非确定性**：同样的输入，输出可能不同。所有工程手段（temperature、schema 约束、重试、对比实验）都是围绕"把不确定性收敛到可接受范围"。

必须记住的几条：
- `temperature=0` 只能大幅降低随机性，不保证 100% 复现；**幂等性要靠 schema 校验 + 重试兜底**。
- 结构化输出必须由 **schema 约束**，不能靠 prompt 里写一句"请返回 JSON"就信任它。
- 抽取类任务失败时**把错误回灌给模型**比盲目重试有效得多（文档标准写法里的核心技巧）。
- 价格与上下文窗口各家随时会变，代码不要硬编码价格数字 —— 这是第 1 周"配置外置"思想的延续。
