"""
第 6 周单元测试 · 可交付项目静态检查（镜像/编排/文档）
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from week06.p1_fastapi.main import app

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "week06" / "p1_fastapi"


def read(relative: str) -> str:
    return (PROJECT / relative).read_text(encoding="utf-8")


def test_main_exposes_fastapi_app() -> None:
    assert isinstance(app, FastAPI)
    assert app.title == "P1 LLM Gateway"


def test_dockerfile_is_runtime_ready() -> None:
    dockerfile = read("Dockerfile")
    assert "FROM python:3.12-slim" in dockerfile
    assert "uv sync --frozen --no-dev" in dockerfile
    assert "USER 10001" in dockerfile
    assert "week06.p1_fastapi.main:app" in dockerfile


def test_compose_uses_env_and_healthcheck() -> None:
    compose = read("docker-compose.yml")
    assert "services:" in compose
    assert "context: ../.." in compose
    assert "healthcheck:" in compose
    assert "${DASHSCOPE_API_KEY:-}" in compose


def test_project_readme_has_diagram_endpoints_decisions() -> None:
    readme = read("README.md")
    assert "## 架构图" in readme and "flowchart" in readme
    assert "## 接口列表" in readme and "/v1/chat" in readme
    assert "## 关键设计决策" in readme
    assert "## 快速开始" in readme


def test_blog_and_stage_review_exist() -> None:
    blog = read("BLOG.md")
    assert "从 Java AI 能力中心到 Python LLM 网关" in blog
    assert "面试叙事" in blog
    review = (ROOT / "week06" / "STAGE_REVIEW.md").read_text(encoding="utf-8")
    assert "阶段验收卡" in review
    assert "复盘模板四问" in review
    assert "23/30" in review
