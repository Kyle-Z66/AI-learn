"""
第 5 周 · 核心机制 10：可观测指标与分位数
================================================================
【对应知识点】文档第 5 周指标清单：延迟 / 成本 / 可靠性 / 用量

【周次学习要点】
  - TTFT 看"多久看到第一个字"，总延迟看"多久拿全答案"，两者不能互相替代。
  - p50/p95/p99 用 nearest-rank 口径：ceil(p*n)-1，指标才能和监控对齐。
  - 429 比例、成功率、缓存命中率的分母都是同一批请求。

【易忽略细节】
  1. 平均值会被大量快请求掩盖尾延迟，这就是必须看 p95 的原因。
  2. 非流式请求没有 TTFT，不能拿总延迟冒充 TTFT。
  3. 缓存命中时 token 用量低，成本下降不等于模型变便宜。

【示例用途】可运行：`python -m week05.core_mechanisms.10_observability_metrics`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from week05.engineering.metrics import MetricsCollector, RequestMetric, percentile


def demo() -> None:
    print("nearest-rank 示例：", percentile([10, 20, 30, 40, 50], 0.95))
    collector = MetricsCollector()
    for index in range(1, 11):
        collector.record(
            RequestMetric(
                provider="qwen" if index % 2 else "deepseek",
                latency_ms=float(index * 10),
                ttft_ms=float(index * 2),
                ok=index != 9,
                status_code=429 if index == 9 else 200,
                input_tokens=100,
                output_tokens=50,
                cache_hit=index % 3 == 0,
            )
        )
    snapshot = collector.snapshot()
    print(
        f"样本数={snapshot.count} 成功率={snapshot.success_rate:.0%} "
        f"429 比例={snapshot.error_429_ratio:.0%}"
    )
    print(
        f"延迟 p50={snapshot.p50_latency_ms:.0f}ms "
        f"p95={snapshot.p95_latency_ms:.0f}ms "
        f"p99={snapshot.p99_latency_ms:.0f}ms"
    )
    print(f"TTFT p50={snapshot.ttft_p50_ms:.0f}ms 缓存命中率={snapshot.cache_hit_rate:.0%}")
    print(f"总 token={snapshot.total_tokens} 分厂商={collector.by_provider()}")


if __name__ == "__main__":
    demo()
