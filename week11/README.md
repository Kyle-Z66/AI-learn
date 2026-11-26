# 第 11 周：生成环节 —— Prompt、引用溯源、幻觉抑制

> 配套文档：《大模型应用开发能力补足 — 20 周可执行学习计划》§ 第二阶段 / 第 11 周。
> **本周只做生成侧可靠性**：评测指标体系与 golden set 是第 12 周任务，本周不越界。

## 一、学习目标（文档原文三任务）

> 目标：把检索到的内容可靠地变成答案。核心原则：**上下文不足时必须明确说"信息不足"，而不是编**。

| 时段 | 文档任务 | 本周落地 |
| --- | --- | --- |
| 工作日 4h | 生成 Prompt 设计：system 规则 + context 分隔符 + question | `core_mechanisms/01`、`engineering/generator.py` |
| 工作日 4h | 引用溯源：每段编号，答案带 `[1][2]`，后处理映射回原文 | `core_mechanisms/03`、`09`、`engineering/context.py` |
| 周末 8h | 幻觉抑制 + 拒答：相关性预检 / 数字实体后校验 / 低温度结构化输出 | `core_mechanisms/04~10`、`engineering/guards.py` |
| 动手 | 四类用例实验台 | `answer_lab/`（相关 / 不相关 / 数字幻觉 / 实体幻觉） |

## 二、与第 7~10 周的衔接（检索链已完成，不重复实现）

| 第 7~10 周已掌握 | 第 11 周如何使用（不再重复讲解） |
| --- | --- |
| 第 7 周解析 / 切分 / chunk 元数据 | 直接消费 `SourceChunk(doc_id, title, page, content)`，不重写解析与切分 |
| 第 8 周嵌入与向量索引 | 生成侧不看向量，只看检索链交出的 Top-K 片段顺序 |
| 第 9 周 BM25 / 混合召回 | 检索结果作为上下文候选；本周假设"正确片段已在 Top-K" |
| 第 10 周重排与 Top-K 收敛 | 重排后的顺序即上下文优先级：越靠前越不容易被预算截断 |
| 第 2 周 temperature / Pydantic schema | 复用低温度与结构化输出原理，只讲工程组合，不重复讲 softmax 与校验器 |
| 第 6 周 FastAPI 交付形态 | 引用与拒答作为响应字段；HTTP 层写法留到第 12 周 P2 项目 |

> **一句话递进关系**：前四周把证据找回来，本周把证据"如实写成答案"——
> 带引用、懂拒答、能拦幻觉。生成质量的上限仍由检索决定，这个判断在第 12 周被量化。

## 三、任务与文件映射

| 时段 | 文档任务 | 落地文件 |
| --- | --- | --- |
| 工作日 4h | 生成 Prompt | [`core_mechanisms/01`](core_mechanisms/) + [`engineering/generator.py`](engineering/) |
| 工作日 4h | 引用溯源 | `core_mechanisms/03`、`09` + `engineering/context.py` |
| 周末 8h | 幻觉抑制 / 拒答 | `core_mechanisms/04~10` + `engineering/guards.py` + [`pitfalls/`](pitfalls/) |
| 动手 | 可靠性实验台 | [`answer_lab/`](answer_lab/) —— 四类用例 + [`REPORT.md`](answer_lab/REPORT.md) |

可运行知识点共 10 个，见 `core_mechanisms/` 的 01~10：

| 编号 | 文件 | 知识点 |
| --- | --- | --- |
| 01 | `01_generation_prompt.py` | system 规则 + `<context>` 分隔符 + question |
| 02 | `02_context_budget.py` | 预算截断与 cited sources 同步 |
| 03 | `03_citation_numbering.py` | `[1][2]` 编号生成与抽取 |
| 04 | `04_relevance_precheck.py` | 检索不相关直接拒答 |
| 05 | `05_refusal_template.py` | 统一拒答文案 |
| 06 | `06_number_entity_check.py` | 关键数字 / 实体后校验 |
| 07 | `07_low_temperature.py` | 低温度 + 复用第 2 周知识 |
| 08 | `08_structured_answer.py` | Pydantic `AnswerWithCitations` |
| 09 | `09_citation_mapping.py` | 编号映射回 doc_id / 标题 / 页码 |
| 10 | `10_hallucination_guard.py` | 预检 + 后校验组合守卫 |

## 四、知识点对照表（文档原有 vs 补足）

### 4.1 文档原文覆盖

| 文档知识点 | 样例文件 | 文档描述充分度与本工程处理 |
| --- | --- | --- |
| system 严格基于上下文 / 不确定就拒答 | `01_generation_prompt.py` | 文档给了原则 → 补足消息结构、分隔符与编号约定 |
| 上下文预算 `build_context` | `02_context_budget.py` / `context.py` | 文档给了代码骨架 → 补足 `ContextBundle` 把 text/sources/truncated 绑成快照 |
| 每段编号 + `[1][2]` 引用 | `03_citation_numbering.py` | 文档仅描述 → 补足"先截断再编号"与编号抽取函数 |
| 后处理映射回原文 | `09_citation_mapping.py` | 文档仅描述 → 补足 `Citation` 结构与越界编号处理 |
| 相关性预检 | `04_relevance_precheck.py` | 文档给了判断条件 → 补足中文分词与停用词、可解释交集 |
| 数字 / 实体后校验 | `06_number_entity_check.py` | 文档给了方向 → 补足数字边界匹配、引用编号剔除 |
| 低温度 + 结构化输出 | `07`、`08` | 文档给了参数 → 复用第 2 周，不重复讲原理 |

### 4.2 对照文档补足的遗漏项（严格限定第 11 周范畴）

| 补足知识点 | 落地文件 | 为什么必须补 |
| --- | --- | --- |
| 统一拒答模板与 refused 状态 | `05_refusal_template.py` / `models.py` | 文档只说"说信息不足"，没说前端契约与指标口径 |
| 组合守卫与失败项可观测 | `10_hallucination_guard.py` / `guards.py` | 两道闸要一次跑完并收齐失败项，否则排障靠猜 |
| 引用编号漂移 | `pitfalls/generation_pitfalls.py` | 编号在截断前分配是静默缺陷，面试常追问 |
| 低温度 ≠ 不幻觉 | `pitfalls/generation_pitfalls.py` | 最常见的过度自信，需要可运行反例 |
| 先修检索再修生成 | `pitfalls/extra_gotchas.py` | 决定第 12 周评测顺序的认知边界 |
| 四类用例实验台 | `answer_lab/` | 文档验收三条分散，实验台把它们合成可复现的一键验证 |

## 五、验收标准与本地验证

文档验收三条：

- [x] 答案带引用编号，能回溯到原文
  → `python -m week11.engineering.engineering_demo` 打印 `[1]` → `DOC-001#p3`
- [x] 实现"上下文不相关则拒答"
  → `python -m week11.answer_lab` 第二类用例输出统一拒答文案
- [x] 有一个幻觉检测的粗实现（数字 / 实体校验）
  → 第三、四类用例失败项分别为 `('500',)` 与 `('李四',)`

本地验证：

```bash
python -m week11.core_mechanisms.01_generation_prompt   # 任选 01~10
python -m week11.engineering.engineering_demo
python -m week11.answer_lab
python -m ruff check week11 tests/week11
python -m mypy week11 tests/week11
python -m pytest -q tests/week11
```

实测记录见 [`answer_lab/REPORT.md`](answer_lab/REPORT.md)（4/4 用例判定符合预期）。

## 六、坑提醒

- **上下文不足仍编造**：模型会"补全"缺失信息；把 `refused` 当成一等状态处理，别只看着 200 状态码。
- **引用编号漂移**：先截断再编号；截断后 `sources` 与 `chunks` 必须同步收窄。
- **预算把证据切掉**：`truncated=True` 要能观测；守卫"通过"不等于答案完整。
- **低温度不等于不幻觉**：0~0.2 只压随机性，证据问题必须靠预检 + 后校验解决。
- **中文分词别用 `split()`**：单字 + 二元组 + 停用词过滤；预检只认长度≥2 的词，
  否则"预算"与"成本计算"靠一个"算"字就被误判为相关。
- **不要越界做评测**：golden set / 指标 / 消融是第 12 周任务，本周只做生成侧可靠性。
