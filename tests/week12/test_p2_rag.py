"""
第 12 周单元测试 · P2 可交付项目（接口 / 自检 / 静态检查）
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from week12.p2_rag.app import create_app
from week12.p2_rag.main import app
from week12.p2_rag.retrieval import CONFIGS, DOCUMENTS, get_chunks, retrieve
from week12.p2_rag.schemas import QueryRequest
from week12.p2_rag.service import RAGService

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "week12" / "p2_rag"


def read(relative: str) -> str:
    return (PROJECT / relative).read_text(encoding="utf-8")


def client_for(application: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=application), base_url="http://test")


def test_main_exposes_fastapi_app() -> None:
    assert isinstance(app, FastAPI)
    assert app.title == "P2 Enterprise RAG"


def test_service_self_check_and_configs() -> None:
    assert RAGService().self_check() is True
    assert len(DOCUMENTS) > 20
    for config in CONFIGS:
        ids = retrieve("系统 cyclone 影响多少人？", config)
        assert len(ids) == 5
        assert all("#p" in item for item in ids)
        assert all(chunk.source in ids for chunk in get_chunks(ids))


def test_query_request_schema() -> None:
    request = QueryRequest(question="系统 cyclone 影响多少人？")
    assert request.config == "hybrid"
    with pytest.raises(ValueError):
        QueryRequest.model_validate({"question": "q", "unexpected": 1})


async def test_query_with_citations_and_refusal() -> None:
    async with client_for(create_app()) as client:
        good = await client.post(
            "/v1/query", json={"question": "系统 cyclone 影响多少人？"}
        )
        refused = await client.post(
            "/v1/query", json={"question": "公司火星基地的预算是多少？"}
        )
        metrics = await client.get("/metrics")
    assert good.status_code == 200
    body = good.json()
    assert body["refused"] is False and body["guard_passed"] is True
    assert body["citations"] and "[1]" in body["answer"]
    assert refused.status_code == 200 and refused.json()["refused"] is True
    assert metrics.json()["count"] == 2
    assert metrics.json()["refusal_count"] == 1


async def test_invalid_requests_return_422() -> None:
    async with client_for(create_app()) as client:
        empty = await client.post("/v1/query", json={"question": ""})
        unknown = await client.post(
            "/v1/query", json={"question": "系统 cyclone", "config": "bogus"}
        )
        extra = await client.post(
            "/v1/query", json={"question": "系统 cyclone", "extra": "x"}
        )
    assert empty.status_code == unknown.status_code == extra.status_code == 422


async def test_healthz_and_eval() -> None:
    async with client_for(create_app()) as client:
        health = await client.get("/healthz")
        evaluation = await client.get("/eval")
    assert health.json() == {"status": "ok"}
    assert evaluation.status_code == 200
    body = evaluation.json()
    assert body["golden_set_count"] == 100
    assert body["configs"] == list(CONFIGS)
    assert len(body["recall_at_5"]) == 4


def test_docker_and_compose_static() -> None:
    dockerfile = read("Dockerfile")
    assert "FROM python:3.12-slim" in dockerfile
    assert "uv sync --frozen --no-dev" in dockerfile
    assert "USER 10001" in dockerfile
    assert "week12.p2_rag.main:app" in dockerfile
    compose = read("docker-compose.yml")
    assert "context: ../.." in compose
    assert "${DASHSCOPE_API_KEY:-}" in compose
    assert "healthcheck:" in compose


def test_golden_set_and_docs() -> None:
    import json

    payload = json.loads(read("golden_set.json"))
    assert len(payload) == 100
    assert all("question" in item and "metadata" in item for item in payload)
    assert all(item["metadata"]["source"] == "教学样例-非真实业务数据" for item in payload)

    readme = read("README.md")
    assert "flowchart" in readme and "/v1/query" in readme
    assert "## 关键设计决策" in readme and "golden set" in readme
    assert "## 与 engineering_demo" in readme
    blog = read("BLOG.md")
    assert "Java" in blog and "消融" in blog

    report = read("REPORT.md")
    assert "| 配置 |" in report and "Recall@5" in report
    assert all(config in report for config in CONFIGS)
    review = (ROOT / "week12" / "STAGE_REVIEW.md").read_text(encoding="utf-8")
    assert "阶段验收卡" in review and "复盘模板四问" in review
    assert "19/30" in review
