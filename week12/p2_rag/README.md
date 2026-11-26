# P2 · 企业级 RAG 知识库服务

> 第二阶段收尾项目：第 7~10 周检索链 → 第 11 周生成可靠性 → 第 12 周评测体系与交付。
> 配套：[`week12/README.md`](../README.md) · 阶段复盘：[`STAGE_REVIEW.md`](../STAGE_REVIEW.md)
> 评测报告：[`REPORT.md`](REPORT.md) · 技术博客：[`BLOG.md`](BLOG.md)

## 架构图（数据流，不是目录树）

```mermaid
flowchart LR
    C[调用方] --> F[FastAPI 边界层<br/>Pydantic 校验 + 统一响应]
    F --> S[RAGService<br/>配置分流 + 计时]
    S --> R[retrieval.py<br/>BM25 / 伪稠密 / RRF / rerank]
    R --> G[generation.py<br/>复用第 11 周 FakeGenerator]
    G --> A[带引用答案 + 守卫状态]
    A --> F
    F --> H[/healthz]
    F --> M[/metrics 请求数/p95/拒答数]
    F --> E[/eval 四配置 Recall@5 摘要]
    D[golden_set.json 100 条教学样例] --> RUN[engineering.runner 本地评测]
    RUN --> REP[REPORT.md 四配置对比表]
    RUN --> CI[engineering.ci_gate 退出码 0/1]
```

**边界原则**：本项目不重写第 11 周的守卫与引用映射；检索排序、评测、HTTP 交付各自独立，
替换真实向量/重排模型时只改 `retrieval.py` 的两个排序函数。

## 接口列表

| 方法 | 路径 | 作用 | 关键返回 |
| --- | --- | --- | --- |
| POST | `/v1/query` | 查询入口，`config` 可选四配置之一 | `answer / citations / refused / guard_passed / latency_ms` |
| GET | `/healthz` | liveness，进程是否存活 | `{"status":"ok"}` |
| GET | `/metrics` | 轻量指标 | `count / p95_latency_ms / refusal_count / last_config` |
| GET | `/eval` | 四配置 Recall@5 摘要（缓存） | `golden_set_count / configs / recall_at_5` |
| GET | `/docs` | 自动 OpenAPI 文档 | Swagger UI |

非法请求（空 question、未知 config、多余字段）返回 422；业务拒答仍是 200，
通过 `refused=true` 与固定拒答文案表达。

## 快速开始

```bash
# 本地自检：只验证导入与链路，不启动长驻服务，不需要 API Key
python -m week12.p2_rag

# 本地起服务（需要时再启动）
uvicorn week12.p2_rag.main:app --host 127.0.0.1 --port 8000
curl -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"系统 cyclone 影响多少人？","config":"hybrid"}'

# 无端口接口测试（CI 推荐）：见 tests/week12/test_p2_rag.py
python -m pytest -q tests/week12

# 容器（真 Key 从宿主环境注入，不写进镜像）
docker compose -f week12/p2_rag/docker-compose.yml up --build
```

## golden set：数据标注标准与替换步骤

`golden_set.json` 恰好 100 条，**全部是教学样例**（`metadata.source =
"教学样例-非真实业务数据"`），不是真实业务数据，也不能当线上指标使用。

- 标注规则：每条含 `question` / `answer` / `relevant_chunk_ids` / `metadata`；
  答案中的数字与实体必须逐字出现在 `relevant_chunk_ids` 指向的片段里；
  一问一片段，20 个知识点各 5 种问法，metadata 记录 topic / 难度 / 标注规则。
- 真实替换步骤：
  1. 用真实文档与领域专家标注替换 100 条（宁少而精，先把难例标清楚）；
  2. 保持四个字段不变，`relevant_chunk_ids` 用 `week12/p2_rag/retrieval.py`
     里 `SourceChunk.source` 粒度（`DOC-001#p3`）；
  3. 更新 `runner.py` 的 `WATCH_ENTITIES` 为真实专有名词；
  4. 重跑 `python -m week12.engineering.engineering_demo`，把新输出抄进
     `REPORT.md`，并重新标定 `ci_gate.py` 的容差；
  5. 把 dev / holdout 分开：调参只用 dev，最终数字只在 holdout 上报告一次。

## 关键设计决策

| 决策 | 为什么这么选 | 放弃了什么 / 代价 |
| --- | --- | --- |
| 四配置共用语料与生成器 | 消融只改检索排序，结论可归因 | 不能同时比较不同生成 Prompt |
| 伪稠密 + 确定性 rerank | 离线可复现、不需要 Key，CI 无网络依赖 | 不是真实语义向量/模型，数字只能当教学参考 |
| BM25 用中文单字切分 | 模拟无词典场景，与第 7 周切分实验呼应 | 召回宽、噪声大，MRR 偏低 |
| 引用与守卫复用第 11 周 | 生成侧一套实现，服务与评测共同验证 | P2 与第 11 周耦合，升级要同步 |
| 拒答用 200 + refused 字段 | 业务状态与系统错误分层，前端契约稳定 | 客户端必须显式检查 refused |
| 报告数字由 runner 渲染 | 指标可复算，避免手抄错或复制示意值 | p95 随机器负载波动，只作本地测量 |
| 生产镜像 `--no-dev` + 非 root | 减小攻击面（第 6 周决策延续） | 调试工具不在镜像内，靠日志/指标排障 |

## 与 engineering_demo / answer_lab 的区别

| 维度 | `week11/answer_lab` | `week12.engineering_demo` | 本 P2 项目 |
| --- | --- | --- | --- |
| 关注点 | 单条答案的引用与幻觉 | 100 条样本的四配置指标 | 可部署的服务 + 可复算评测 |
| 检索 | 固定上下文，不排序 | 四配置排序对比 | 运行时按 config 分流 |
| 数据 | 4 条手写用例 | 100 条教学 golden set | 同一份 golden set，服务与评测共用语料 |
| 形态 | CLI 自检 | CLI 报告 | FastAPI + Docker + `/eval` |

## 诚实边界

1. 本项目没有真实向量库、真实 Rerank 模型、真实业务文档；所有 key 留空也能跑。
2. 报告里的 p95 是本地单机测量，质量指标受教学语料区分度限制（见 REPORT.md 解读）。
3. 评测集是累加资产：本周的 100 条只是起点，上线前必须用真实难例替换并做 dev/holdout 划分。
