"""
第 6 周 · 本周特有坑：FastAPI 交付阶段常见翻车点
================================================================
【对应知识点】文档第 6 周 P1 收尾（FastAPI / Docker / 文档）

【周次学习要点】
  - `async def` 里调用阻塞函数会拖住整个事件循环，第 1 周 asyncio 知识在此最易丢。
  - 流式接口先把内容攒完再返回，本质是伪流式，首字节延迟并不低。
  - 密钥写进 Dockerfile/镜像是最常见的安全事故，必须走环境变量。

【易忽略细节】
  1. 同步 `def` 路由会被 FastAPI 放进线程池，但 `async def` 里的 time.sleep 不会被搬走。
  2. 重复定义 Pydantic 模型会让边界契约与内部模型漂移，直接 import 既有模型。
  3. compose 里的 `${VAR:-}` 是占位符，不是密钥本体。

【示例用途】可运行：`python -m week06.pitfalls.fastapi_pitfalls`
             测试见 tests/week06/test_pitfalls.py
"""
from __future__ import annotations

import asyncio
import time

from week06.engineering.schemas import ChatRequest


async def _task(name: str, blocking: bool) -> str:
    if blocking:
        time.sleep(0.1)  # 错误示范：阻塞事件循环
    else:
        await asyncio.sleep(0.1)
    return name


async def demo_blocking_sleep() -> None:
    started = time.perf_counter()
    await asyncio.gather(_task("a", False), _task("b", False))
    good = time.perf_counter() - started
    started = time.perf_counter()
    await asyncio.gather(_task("a", True), _task("b", True))
    bad = time.perf_counter() - started
    print(f"两个各 0.1s 的任务：await asyncio.sleep → {good:.3f}s，"
          f"time.sleep → {bad:.3f}s（后者串行化了）")


def demo_schema_boundary() -> None:
    request = ChatRequest(question="系统 cyclone")
    print("直接复用既有边界模型：", type(request).__name__, request.model_dump())
    print("不要在每个路由里复制一份字段定义，否则校验规则会漂移")


def demo_pseudo_streaming() -> None:
    content = "运维响应示例"
    buffered = [content]  # 错误：一次性返回
    streamed = list(content)  # 正确：逐块 yield
    print(f"伪流式首块长度={len(buffered[0])}（整段），真流式首块长度={len(streamed[0])}")


def demo_docker_secret() -> None:
    bad = "ENV DASHSCOPE_API_KEY=FAKE-KEY-0001  # 错误：密钥进镜像层"
    good = "environment: - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY:-}  # 正确：运行时注入"
    print("错误写法：", bad)
    print("正确写法：", good)


async def demo() -> None:
    await demo_blocking_sleep()
    demo_schema_boundary()
    demo_pseudo_streaming()
    demo_docker_secret()


if __name__ == "__main__":
    asyncio.run(demo())
