"""
第 6 周 · 核心机制 01：FastAPI 应用与路由清单
================================================================
【对应知识点】文档第 6 周：FastAPI 暴露 REST 接口

【周次学习要点】
  - 应用工厂 create_app() 每次返回独立 app，测试之间不会互相污染。
  - 路由分三组：调用(/v1/chat)、探测(/healthz,/readyz)、观测(/metrics)。
  - OpenAPI 文档由 FastAPI 自动生成，响应模型就是文档契约。

【易忽略细节】
  1. 路由函数必须是 async def 才能直接 await 网关；同步函数会被丢进线程池。
  2. response_model 不是装饰：它会过滤掉未声明的内部字段，避免泄漏。
  3. /docs 是自动生成的接口文档，交付时比手写接口表更不容易漂移。

【示例用途】可运行：`python -m week06.core_mechanisms.01_fastapi_routes`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

from week06.engineering.app import create_app


def demo() -> None:
    app = create_app()
    print(f"应用标题：{app.title} 版本：{app.version}")
    for route in app.routes:
        methods: set[str] = getattr(route, "methods", set())
        path: str = getattr(route, "path", "")
        print(f"  {','.join(sorted(methods)):<12} {path}")


if __name__ == "__main__":
    demo()
