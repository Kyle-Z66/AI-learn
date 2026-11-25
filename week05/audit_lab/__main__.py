"""
第 5 周 · 动手项目入口：全链路审计 + 成本日报表
================================================================
【对应知识点】文档第 5 周周末任务：审计 + 成本核算

【周次学习要点】
  - 三条 trace 演示三类真实场景：主模型失败降级、429 重试成功、缓存命中。
  - 同一 trace 的记录用 request_id 串起来，验收时可按 trace 直接查。
  - 成本报表按实际 provider 计价；指标快照从同一批审计记录聚合。

【易忽略细节】
  1. 降级链路里失败记录也要落库，否则"为什么换模型"无从追溯。
  2. 缓存命中示例 token 为 0，成本为 0，但请求数仍要计入。
  3. SQLite 用内存库，进程结束数据即消失；生产换成文件/远端库。

【示例用途】可运行：`python -m week05.audit_lab`
             测试见 tests/week05/test_audit_lab.py
"""
from __future__ import annotations

from week05.audit_lab.models import LabCase, to_audit_record
from week05.audit_lab.reporter import build_metrics, print_cost_report, print_trace_chain
from week05.engineering.audit import SQLiteAuditStore, new_trace_id


def build_cases() -> list[LabCase]:
    """构造三条 trace：降级、重试、缓存命中。"""
    fallback_trace = new_trace_id()
    retry_trace = new_trace_id()
    cache_trace = new_trace_id()
    return [
        LabCase(
            fallback_trace, "ticket_extract", "qwen", "error", 0, 0, 120.0,
            http_status=503, error_type="ServiceUnavailable", error_message="qwen 挂了",
        ),
        LabCase(
            fallback_trace, "ticket_extract", "deepseek", "success_after_fallback",
            1000, 200, 780.0, fallback_used=True,
        ),
        LabCase(
            retry_trace, "ticket_extract", "deepseek", "error", 0, 0, 60.0,
            http_status=429, error_type="HttpStatusError", error_message="限流",
        ),
        LabCase(
            retry_trace, "ticket_extract", "deepseek", "success_after_retry",
            900, 180, 640.0, retry_count=1,
        ),
        LabCase(
            cache_trace, "ticket_extract", "glm", "success_from_cache", 0, 0, 12.0,
        ),
    ]


def demo() -> None:
    store = SQLiteAuditStore()
    cases = build_cases()
    for index, case in enumerate(cases, start=1):
        store.append(to_audit_record(case, index))

    print("=== 验收 1：按 trace 查完整链路 ===")
    print(print_trace_chain(store, cases[0].trace_id))
    print("\n=== 验收 2：按天 / provider 聚合成本 ===")
    print(print_cost_report(store))

    records = store.all_records()
    ttfts = {
        f"{case.trace_id}-{index:02d}": 120.0
        for index, case in enumerate(cases, start=1)
        if case.status.startswith("success")
    }
    metrics = build_metrics(records, ttfts)
    print("\n=== 可观测快照 ===")
    print(
        f"请求数={metrics.count} 成功率={metrics.success_rate:.0%} "
        f"429比例={metrics.error_429_ratio:.0%} "
        f"p95延迟={metrics.p95_latency_ms:.0f}ms "
        f"TTFT-p50={metrics.ttft_p50_ms:.0f}ms "
        f"缓存命中率={metrics.cache_hit_rate:.0%}"
    )


if __name__ == "__main__":
    demo()
