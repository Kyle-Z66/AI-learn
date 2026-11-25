"""
第 4 周 · 动手项目：并发压测数据模型
================================================================
【对应知识点】文档第 4 周验收标准：并发 N 相比串行的耗时对比表

【周次学习要点】
  - 一次压测结果用 dataclass（第 1 周已掌握）封装，便于排序与打印表格。
  - QPS = 请求数 / 耗时，是对比并发收益最直观的指标。

【易忽略细节】
  - frozen dataclass 里不要放可变默认字段（第 1 周可变默认参数坑）。
  - 耗时用 perf_counter 测量，不用 time.time，避免系统时钟调整干扰。

【示例用途】被 benchmark.py / __main__.py 引用，不单独运行。
             测试见 tests/week04/test_concurrency_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkResult:
    """一次压测结果：模式、请求数、耗时、峰值并发。"""

    mode: str
    count: int
    elapsed: float  # 秒
    peak: int

    @property
    def qps(self) -> float:
        """每秒请求数。"""
        return self.count / self.elapsed if self.elapsed > 0 else 0.0
