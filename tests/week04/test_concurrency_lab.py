"""
第 4 周单元测试 · 动手项目：100 请求并发压测
"""
from __future__ import annotations

from week04.concurrency_lab.benchmark import run_all, run_gather, run_semaphore, run_serial
from week04.concurrency_lab.models import BenchmarkResult


async def test_serial_baseline() -> None:
    result = await run_serial(count=5, delay=0.001)
    assert result.count == 5
    assert result.peak == 1
    assert result.elapsed > 0


async def test_gather_all_concurrent() -> None:
    result = await run_gather(count=10, delay=0.001)
    assert result.peak == 10
    assert result.mode == "gather"


async def test_semaphore_bounds_peak() -> None:
    result = await run_semaphore(count=20, delay=0.001, limit=3)
    assert result.peak <= 3
    assert result.mode == "Semaphore(3)"


async def test_run_all_returns_three_modes() -> None:
    results = await run_all(count=10, delay=0.001, limit=4)
    assert [result.mode for result in results] == ["串行", "gather", "Semaphore(4)"]


def test_qps_calculation() -> None:
    result = BenchmarkResult(mode="test", count=100, elapsed=2.0, peak=1)
    assert result.qps == 50.0


async def test_concurrent_faster_than_serial() -> None:
    serial = await run_serial(count=20, delay=0.002)
    concurrent = await run_gather(count=20, delay=0.002)
    assert concurrent.elapsed < serial.elapsed
