"""
第 12 周 · P2 项目：FastAPI 应用（/v1/query + 探测 + 指标 + 评测摘要）
================================================================
【对应知识点】文档第 12 周：P2 项目可运行、有 API；第 6 周 FastAPI 交付复用

【周次学习要点】
  - create_app() 每次返回独立 app 与状态，测试互不污染（第 6 周决策延续）。
  - /v1/query 返回答案、引用、拒答与守卫状态；业务拒答是 200，不是 5xx。
  - /eval 返回四配置 Recall@5 摘要（缓存结果），完整报告由 runner 生成到 REPORT.md。

【易忽略细节 / 对照文档补足】
  1. 文档只说"有 API"，没说未知检索配置怎么办 → 这里转 422，避免悄悄走默认配置。
  2. /metrics 的 p95 来自真实请求耗时列表，是本地教学测量，不是线上 SLA。
  3. 路由是 async def，但检索与生成是同步纯计算；真实项目要用线程池或异步客户端
     （第 1 周 asyncio 边界已讲），否则事件循环会被 CPU 密集计算拖住。

【示例用途】被 main.py 与 tests/week12/test_p2_rag.py 引用；不单独运行。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from fastapi import FastAPI, HTTPException

from week12.engineering.golden_set import load_golden_set
from week12.engineering.metrics import p95_latency_ms, recall_at_k
from week12.p2_rag.retrieval import CONFIGS, retrieve
from week12.p2_rag.schemas import (
    CitationItem,
    EvalResponse,
    MetricsResponse,
    QueryRequest,
    QueryResponse,
)
from week12.p2_rag.service import RAGService


@dataclass
class ServiceState:
    """单 app 内的轻量状态：服务实例、耗时样本与拒答计数。"""

    latencies: list[float] = field(default_factory=list)
    refusal_count: int = 0
    last_config: str = "hybrid"


@lru_cache(maxsize=1)
def eval_summary() -> EvalResponse:
    """四配置 Recall@5 摘要；结果缓存，避免每次 /eval 重跑 400 次检索。"""
    cases = load_golden_set()
    recalls = [
        sum(
            recall_at_k(retrieve(case.question, config), case.relevant_chunk_ids)
            for case in cases
        ) / len(cases)
        for config in CONFIGS
    ]
    return EvalResponse(
        golden_set_count=len(cases),
        configs=list(CONFIGS),
        recall_at_5=recalls,
        note="仅 Recall@5 摘要；完整四配置指标见 p2_rag/REPORT.md",
    )


def create_app() -> FastAPI:
    """应用工厂：返回独立 app，状态随 app 创建，便于隔离测试。"""
    app = FastAPI(title="P2 Enterprise RAG", version="1.0.0")
    state = ServiceState()

    @app.post("/v1/query", response_model=QueryResponse)
    async def query(request: QueryRequest) -> QueryResponse:
        try:
            outcome = RAGService(config=request.config).query(request.question)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        answer = outcome.answer
        state.latencies.append(outcome.latency_ms)
        state.refusal_count += int(answer.refused)
        state.last_config = request.config
        return QueryResponse(
            answer=answer.text,
            citations=[
                CitationItem(
                    number=item.number,
                    doc_id=item.doc_id,
                    title=item.title,
                    page=item.page,
                    source=item.source,
                )
                for item in answer.citations
            ],
            refused=answer.refused,
            guard_passed=answer.guard.passed,
            config=request.config,
            latency_ms=outcome.latency_ms,
        )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics", response_model=MetricsResponse)
    async def metrics() -> MetricsResponse:
        return MetricsResponse(
            count=len(state.latencies),
            p95_latency_ms=p95_latency_ms(state.latencies),
            refusal_count=state.refusal_count,
            last_config=state.last_config,
        )

    @app.get("/eval", response_model=EvalResponse)
    async def evaluate() -> EvalResponse:
        return eval_summary()

    return app
