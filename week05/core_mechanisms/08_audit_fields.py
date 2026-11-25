"""
第 5 周 · 核心机制 08：19 字段审计落库与链路查询
================================================================
【对应知识点】文档第 5 周：请求/响应/耗时/token/成本/状态全量落库

【周次学习要点】
  - trace_id 把重试、降级串成一条链；request_id 标识链中的单次尝试。
  - 19 字段覆盖"谁、何时、调了谁、结果如何、花了多少"。
  - SQLite 内存库即可跑通；生产替换为同结构的正式表。

【易忽略细节】
  1. 文档说"对齐 AiExecuteLogs 的 19 字段"但没列，这里给出明确定义。
  2. 请求/响应原文含密钥与手机号时必须脱敏后再落库。
  3. fallback_used 存 INTEGER，读回要转回 bool，否则真值判断会出错。

【示例用途】可运行：`python -m week05.core_mechanisms.08_audit_fields`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from week05.engineering.audit import (
    AUDIT_FIELDS,
    AuditRecord,
    SQLiteAuditStore,
    new_trace_id,
    sanitize,
)


def demo() -> None:
    trace = new_trace_id()
    record = AuditRecord(
        trace_id=trace,
        request_id="req-0001",
        timestamp="2026-11-25T10:00:00",
        user_id="u-1024",
        scenario="ticket_extract",
        provider="deepseek",
        model="deepseek-chat",
        status="success_after_fallback",
        http_status=200,
        error_type="ConnectionError",
        error_message="qwen 不可用",
        retry_count=1,
        fallback_used=True,
        input_tokens=800,
        output_tokens=120,
        latency_ms=930.5,
        cost_yuan=0.52,
        request_digest=sanitize("api_key=FAKE-KEY-0001, phone=13800000000"),
        response_digest='{"system_name": "cyclone"}',
    )
    store = SQLiteAuditStore()
    store.append(record)
    found = store.find_by_trace(trace)
    print(f"审计字段数：{len(AUDIT_FIELDS)}（文档要求 19）")
    print("按 trace 查到：", len(found), "条")
    print("落库后 fallback_used 类型：", type(found[0].fallback_used).__name__)
    print("脱敏后的请求摘要：", found[0].request_digest)


if __name__ == "__main__":
    demo()
