"""
第 1 周 · 语言差异点 05：asyncio / await（本周最重要，面试必问）
================================================================
【对应知识点】文档第 1 周「语言差异点」第 5 项 + 「坑提醒」：必须用异步

【周次学习要点】
  - LLM 调用是 IO 密集型（等网络返回），同步写法会让并发直接崩 —— 这是文档强调的必问点。
  - await 只能在 async def 内使用；调用 async 函数只会得到 coroutine 对象，
    **必须 await（或交给事件循环调度）才会真正执行**。
  - asyncio.gather：并发调度多个协程；TaskGroup（3.11+）：结构化并发，异常会统一传播。
  - asyncio.to_thread：把阻塞型同步库（如 openpyxl / 文件 IO）丢进线程池，
    不阻塞事件循环 —— 这正是周末 Excel 导出器里 asyncio + ThreadPoolExecutor 的协作方式。

【易忽略细节】
  1. 只创建 coroutine 不 await → 什么都不会发生，还会收到 RuntimeWarning，需 .close()。
  2. CPU 密集任务（大量计算）用 asyncio / 多线程都受 GIL 限制，不会提速；
     要用多进程。asyncio 的主场是 IO 密集。
  3. TaskGroup 退出时会等待所有子任务；其中一个抛异常会取消其余任务（结构化并发）。

【示例用途】可运行：`python week01/language_features/05_asyncio_await.py`
"""
from __future__ import annotations

import asyncio
import time


async def fake_llm_call(request_id: int, delay: float = 0.1) -> str:
    """模拟一次 LLM API 调用：asyncio.sleep 代表网络等待（IO 密集）。"""
    await asyncio.sleep(delay)
    return f"resp-{request_id}"


async def run_sequential() -> list[str]:
    """串行：每个请求都等前一个完成 —— 同步写法的问题就在这里。"""
    return [await fake_llm_call(i) for i in range(4)]


async def run_with_gather() -> list[str]:
    """并发：gather 把 4 个协程交给事件循环，等待时间约等于最慢的那个。"""
    return list(await asyncio.gather(*(fake_llm_call(i) for i in range(4))))


async def run_with_task_group() -> list[str]:
    """结构化并发：TaskGroup 保证退出前所有任务完成，异常可统一处理。"""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fake_llm_call(i)) for i in range(4)]
    return [task.result() for task in tasks]


def blocking_work(n: int) -> int:
    """模拟阻塞型同步库（如 openpyxl 写 Excel）：用 time.sleep 占用线程。"""
    time.sleep(0.05)
    return n * n


async def run_with_to_thread() -> list[int]:
    """把阻塞操作放进线程池，避免卡住事件循环（对应周末导出器的做法）。"""
    return list(await asyncio.gather(*(asyncio.to_thread(blocking_work, i) for i in range(4))))


def demo_coroutine_lazy() -> None:
    """关键演示：创建 coroutine 而不 await，函数体一行都不会执行。"""
    coro = fake_llm_call(99)
    print(f"  只创建 coroutine：{coro} —— 没有发出任何调用")
    coro.close()  # 主动关闭，避免 "coroutine was never awaited" 警告


async def main() -> None:
    print("=== 05 asyncio / await ===")
    demo_coroutine_lazy()

    start = time.perf_counter()
    seq = await run_sequential()
    seq_cost = time.perf_counter() - start

    start = time.perf_counter()
    par = await run_with_gather()
    par_cost = time.perf_counter() - start

    print(f"  串行 4 个请求 : {seq}  耗时 {seq_cost:.3f}s")
    print(f"  gather 并发   : {par}  耗时 {par_cost:.3f}s —— 快了约 {seq_cost / par_cost:.1f} 倍")
    print(f"  TaskGroup     : {await run_with_task_group()}")
    print(f"  to_thread     : {await run_with_to_thread()} —— 阻塞库也能并发")
    print("  结论：LLM/网络/文件 IO 用 asyncio；CPU 密集用多进程（GIL 限制）")


if __name__ == "__main__":
    asyncio.run(main())
