"""
第 5 周 · 工程层：可观测指标（TTFT / 分位数 / 成功率 / 429 比例）
================================================================
【对应知识点】文档第 5 周可观测指标清单：延迟、成本、可靠性、用量

【周次学习要点】
  - TTFT（首 token 延迟）体现"用户多久看到第一个字"，总延迟体现"多久拿全答案"。
  - p50/p95/p99 看尾延迟，不能只看平均值：平均值会被大量快请求掩盖慢请求。
  - 可靠性相关比率都从同一批请求算，分母必须一致才能对齐监控大盘。

【易忽略细节 / 对照文档补足】
  1. 文档列了指标名没给口径 → 这里明确 p95 用 nearest-rank：ceil(0.95*n)-1。
  2. 流式请求才有 TTFT；非流式请求的 ttft_ms 为 None，不参与分位数。
  3. 缓存命中的请求 token 用量低，统计用量分布时要单独标注命中率。

【示例用途】被 core_mechanisms/10、audit_lab、engineering_demo 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestMetric:
    """单个请求的观测样本。"""

    provider: str
    latency_ms: float
    ttft_ms: float | None
    ok: bool
    status_code: int | None
    input_tokens: int
    output_tokens: int
    cache_hit: bool


@dataclass(frozen=True)
class MetricsSnapshot:
    """给报表/监控的聚合快照。"""

    count: int
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    ttft_p50_ms: float | None
    error_429_ratio: float
    total_tokens: int
    cache_hit_rate: float


def percentile(values: Sequence[float], p: float) -> float:
    """nearest-rank 分位数；空样本返回 0.0，p 需在 (0, 1] 内。"""
    if not values:
        return 0.0
    if not 0 < p <= 1:
        raise ValueError("p 必须在 (0, 1] 区间")
    ordered = sorted(values)
    index = min(math.ceil(p * len(ordered)) - 1, len(ordered) - 1)
    return ordered[max(index, 0)]


class MetricsCollector:
    """收集样本并输出快照；不依赖 prometheus，便于单测。"""

    def __init__(self) -> None:
        self._items: list[RequestMetric] = []

    def record(self, metric: RequestMetric) -> None:
        self._items.append(metric)

    def snapshot(self) -> MetricsSnapshot:
        count = len(self._items)
        if count == 0:
            return MetricsSnapshot(0, 0.0, 0.0, 0.0, 0.0, None, 0.0, 0, 0.0)
        latencies = [item.latency_ms for item in self._items]
        ttfts = [item.ttft_ms for item in self._items if item.ttft_ms is not None]
        return MetricsSnapshot(
            count=count,
            success_rate=sum(item.ok for item in self._items) / count,
            p50_latency_ms=percentile(latencies, 0.50),
            p95_latency_ms=percentile(latencies, 0.95),
            p99_latency_ms=percentile(latencies, 0.99),
            ttft_p50_ms=percentile(ttfts, 0.50) if ttfts else None,
            error_429_ratio=sum(
                item.status_code == 429 for item in self._items
            ) / count,
            total_tokens=sum(item.input_tokens + item.output_tokens for item in self._items),
            cache_hit_rate=sum(item.cache_hit for item in self._items) / count,
        )

    def by_provider(self) -> dict[str, int]:
        """按 provider 统计请求数，便于定位哪家模型拖慢整体。"""
        result: dict[str, int] = {}
        for item in self._items:
            result[item.provider] = result.get(item.provider, 0) + 1
        return result


__all__ = [
    "MetricsCollector",
    "MetricsSnapshot",
    "RequestMetric",
    "percentile",
]
