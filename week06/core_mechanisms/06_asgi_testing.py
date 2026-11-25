"""
第 6 周 · 核心机制 06：ASGITransport 无端口异步测试
================================================================
【对应知识点】文档第 6 周验收卡：单测覆盖率 > 60%

【周次学习要点】
  - httpx.ASGITransport 把请求直接交给 ASGI app，不启动 uvicorn、不占端口。
  - 延迟、并发测试都稳定，CI 里不需要起服务或等待就绪。
  - 校验失败（422）与成功（200）都要测，接口契约才算完整。

【易忽略细节】
  1. base_url 只是 URL 拼接用，不会真的发起网络连接。
  2. 每次测试前 reset_container()，否则指标计数会跨用例累加。
  3. AsyncClient 要 async with 关闭，避免资源泄漏。

【示例用途】可运行：`python -m week06.core_mechanisms.06_asgi_testing`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from week06.engineering.app import create_app
from week06.engineering.dependencies import reset_container


async def demo() -> None:
    reset_container()
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        invalid = await client.post("/v1/chat", json={"question": ""})
        valid = await client.post("/v1/chat", json={"question": "系统 cyclone"})
        missing = await client.get("/not-exists")
    print("空问题：", invalid.status_code, "（Pydantic 边界校验）")
    print("合法请求：", valid.status_code, "trace=", valid.json()["trace_id"][:8])
    print("不存在路由：", missing.status_code)


if __name__ == "__main__":
    asyncio.run(demo())
