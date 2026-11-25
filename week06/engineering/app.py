"""
第 6 周 · 工程层：FastAPI 应用工厂（P1 的 HTTP 外壳）
================================================================
【对应知识点】文档第 6 周：FastAPI 暴露 REST 接口 + 可交付项目

【周次学习要点】
  - 路由只做三件事：校验边界、调用第 3 周网关、把结果写进第 5 周审计与指标。
  - 健康检查分 liveness(/healthz) 与 readiness(/readyz)：后者读熔断状态。
  - 流式接口用 StreamingResponse 接 async 生成器，复用第 4 周 SSE 编码。

【易忽略细节 / 对照文档补足】
  1. 文档只说"暴露接口"，没说熔断打开时怎么办 → readiness 返回 503，让流量摘除实例。
  2. 每个请求生成 trace_id 并回传，重试/降级记录可用它串起来。
  3. 流式这里演示 HTTP 层；真实逐 token 需要 provider 层 astream（第 4 周已讲接法）。
  4. 所有路由都是 async def，耗时操作必须 await，不能在里面用 time.sleep。

【示例用途】被 p1_fastapi/main.py、engineering_demo.py 引用；
             测试见 tests/week06/test_engineering.py
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from week03.p1_gateway.models import GatewayRequest
from week04.engineering.sse import SSEEvent, encode_sse
from week05.engineering.audit import AuditRecord, new_trace_id
from week05.engineering.metrics import RequestMetric

from week06.engineering.dependencies import ServiceContainer, get_container
from week06.engineering.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MetricsResponse,
)


def create_app() -> FastAPI:
    """应用工厂：每次调用得到独立 app，测试互不污染。"""
    app = FastAPI(title="P1 LLM Gateway", version="1.0.0")

    @app.post("/v1/chat", response_model=ChatResponse)
    async def chat(
        request: ChatRequest,
        service: Annotated[ServiceContainer, Depends(get_container)],
    ) -> ChatResponse:
        trace_id = new_trace_id()
        gateway_request = GatewayRequest(
            messages=[
                {"role": "system", "content": "你是运维助手，请抽取工单关键信息"},
                {"role": "user", "content": request.question},
            ]
        )
        response = await service.gateway.chat(gateway_request)
        provider = service.gateway.registry.last_used or "unknown"
        used_fallback = provider != service.config.order[0]

        service.audit.append(
            AuditRecord(
                trace_id=trace_id,
                request_id=f"{trace_id}-01",
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                user_id=request.user_id,
                scenario=request.scenario,
                provider=provider,
                model=response.model,
                status="success_after_fallback" if used_fallback else "success",
                http_status=200,
                error_type="",
                error_message="",
                retry_count=0,
                fallback_used=used_fallback,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                latency_ms=response.latency_ms,
                cost_yuan=response.cost_yuan,
                request_digest=request.question[:200],
                response_digest=response.content[:200],
            )
        )
        service.metrics.record(
            RequestMetric(
                provider=provider,
                latency_ms=response.latency_ms,
                ttft_ms=None,
                ok=True,
                status_code=200,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cache_hit=False,
            )
        )
        return ChatResponse(
            answer=response.content,
            provider=provider,
            latency_ms=response.latency_ms,
            cost_yuan=response.cost_yuan,
            trace_id=trace_id,
        )

    @app.get("/healthz", response_model=HealthResponse)
    async def healthz() -> HealthResponse:
        """liveness：进程活着即可，不查下游，避免被模型故障拖死。"""
        return HealthResponse(status="ok")

    @app.get("/readyz", response_model=HealthResponse)
    async def readyz(
        service: Annotated[ServiceContainer, Depends(get_container)],
    ) -> HealthResponse:
        """readiness：任一 provider 熔断打开就不接流量。"""
        states = {name: breaker.state.value for name, breaker in service.breakers.items()}
        if any(state == "open" for state in states.values()):
            raise HTTPException(
                status_code=503,
                detail={"status": "not_ready", "breaker_states": states},
            )
        return HealthResponse(status="ready", breaker_states=states)

    @app.get("/metrics", response_model=MetricsResponse)
    async def metrics(
        service: Annotated[ServiceContainer, Depends(get_container)],
    ) -> MetricsResponse:
        snapshot = service.metrics.snapshot()
        return MetricsResponse(
            count=snapshot.count,
            success_rate=snapshot.success_rate,
            p95_latency_ms=snapshot.p95_latency_ms,
            error_429_ratio=snapshot.error_429_ratio,
            total_tokens=snapshot.total_tokens,
            cache_hit_rate=snapshot.cache_hit_rate,
        )

    @app.get("/v1/chat/stream")
    async def stream(question: str) -> StreamingResponse:
        """SSE 流式出口；用 async 生成器逐帧 yield，不先攒完整响应。"""
        trace_id = new_trace_id()

        async def frames() -> AsyncGenerator[str, None]:
            for char in question[:20]:
                yield encode_sse(
                    SSEEvent(data=char, event="delta", event_id=trace_id)
                )
                await asyncio.sleep(0.001)
            yield encode_sse(
                SSEEvent(data="[DONE]", event="done", event_id=trace_id)
            )

        return StreamingResponse(frames(), media_type="text/event-stream")

    return app
