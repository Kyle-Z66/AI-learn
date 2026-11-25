"""
第 6 周单元测试 · FastAPI 工程层：路由 / DI / 探测 / 流式
"""
from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from week04.engineering.sse import SSEDecoder
from week06.engineering.app import create_app
from week06.engineering.dependencies import (
    build_container,
    get_container,
    reset_container,
)
from week06.engineering.schemas import ChatRequest, ChatResponse


def client_for(app: FastAPI) -> AsyncClient:
    """无端口测试客户端；app 由 create_app 返回。"""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def test_schemas_validate_boundary() -> None:
    request = ChatRequest(question="系统 cyclone")
    assert request.user_id == "anonymous"
    response = ChatResponse(
        answer="ok", provider="qwen", latency_ms=1.0, cost_yuan=0.0, trace_id="t"
    )
    assert "trace_id" in response.model_dump()


def test_app_routes_registered() -> None:
    app = create_app()
    paths = {getattr(route, "path", "") for route in app.routes}
    assert {"/v1/chat", "/healthz", "/readyz", "/metrics", "/v1/chat/stream"} <= paths


async def test_chat_writes_audit_and_metrics() -> None:
    reset_container()
    service = get_container()
    async with client_for(create_app()) as client:
        response = await client.post(
            "/v1/chat",
            json={"question": "系统 cyclone 级别 2 影响 30 人", "user_id": "u-1"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] in {"qwen", "deepseek", "glm"}
    assert len(body["trace_id"]) == 16
    assert len(service.audit.find_by_trace(body["trace_id"])) == 1
    assert service.metrics.snapshot().count == 1


async def test_invalid_request_returns_422() -> None:
    reset_container()
    async with client_for(create_app()) as client:
        response = await client.post("/v1/chat", json={"question": ""})
    assert response.status_code == 422


async def test_liveness_and_readiness() -> None:
    reset_container()
    service = get_container()
    async with client_for(create_app()) as client:
        alive = await client.get("/healthz")
        ready = await client.get("/readyz")
        assert alive.json() == {"status": "ok", "breaker_states": {}}
        assert ready.status_code == 200
        assert ready.json()["status"] == "ready"

        breaker = service.breakers["qwen"]
        for _ in range(breaker.config.failure_threshold):
            await breaker.record_failure()
        not_ready = await client.get("/readyz")
        assert not_ready.status_code == 503
        assert not_ready.json()["detail"]["breaker_states"]["qwen"] == "open"


async def test_metrics_endpoint() -> None:
    reset_container()
    async with client_for(create_app()) as client:
        await client.post("/v1/chat", json={"question": "系统 cyclone"})
        response = await client.get("/metrics")
    assert response.status_code == 200
    assert response.json()["count"] == 1


async def test_stream_endpoint_emits_sse_frames() -> None:
    async with client_for(create_app()) as client:
        response = await client.get(
            "/v1/chat/stream", params={"question": "流式响应示例"}
        )
        decoder = SSEDecoder()
        events: list[str] = []
        async for chunk in response.aiter_text():
            events.extend(event.data for event in decoder.feed(chunk))
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert events[-1] == "[DONE]"


async def test_dependency_override_isolates_state() -> None:
    reset_container()
    original = get_container()
    fake = build_container()
    app = create_app()
    app.dependency_overrides[get_container] = lambda: fake
    async with client_for(app) as client:
        response = await client.post("/v1/chat", json={"question": "系统 cyclone"})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake.metrics.snapshot().count == 1
    assert original.metrics.snapshot().count == 0
