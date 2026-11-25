"""
第 4 周 · 核心机制 09：asyncio.TaskGroup 与错误传播
================================================================
【对应知识点】文档验收标准第 4 条：掌握 Semaphore / gather / TaskGroup 区别与用法

【周次学习要点】
  - TaskGroup（3.11+）用 `async with` 管理一组任务，退出时自动等待全部完成。
  - 与 gather 最大差异：任一任务抛异常，TaskGroup 会取消其余兄弟任务，
    并以 ExceptionGroup 形式一次性上报，不会静默丢错。
  - 适合"要么全成功、要么整体失败"的批量调用场景。

【易忽略细节】
  1. 捕获 TaskGroup 的异常要用 `except*`，普通 `except Exception` 抓不到 ExceptionGroup。
  2. gather 默认遇到异常会向外传播，但其他任务**继续在后台跑**，不会自动取消。
  3. TaskGroup 内创建任务用 `tg.create_task()`，不要在外面先 gather 再塞进去。

【示例用途】可运行：`python -m week04.core_mechanisms.09_taskgroup`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio


async def may_fail(index: int) -> int:
    if index == 2:
        raise ValueError(f"第 {index} 个任务失败")
    await asyncio.sleep(0.05)
    return index


async def demo_gather() -> None:
    """gather：异常立即传播，但其余任务不会自动取消。"""
    try:
        await asyncio.gather(*(may_fail(i) for i in range(5)))
    except ValueError as exc:
        print("gather 捕获到：", exc)
        await asyncio.sleep(0.06)  # 给剩余任务一点时间，观察它们仍在运行


async def demo_taskgroup() -> None:
    """TaskGroup：首个异常取消兄弟任务，以 ExceptionGroup 上报。"""
    try:
        async with asyncio.TaskGroup() as group:
            for index in range(5):
                group.create_task(may_fail(index))
    except* ValueError as group_error:
        print("TaskGroup 捕获到：", [str(e) for e in group_error.exceptions])


async def demo() -> None:
    print("=== gather ===")
    await demo_gather()
    print("=== TaskGroup ===")
    await demo_taskgroup()


if __name__ == "__main__":
    asyncio.run(demo())
