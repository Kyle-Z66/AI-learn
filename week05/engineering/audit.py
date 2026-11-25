"""
第 5 周 · 工程层：19 字段调用审计（对齐 AiExecuteLogs 思路）
================================================================
【对应知识点】文档第 5 周「请求/响应/耗时/token/成本/状态 全量落库」

【周次学习要点】
  - 一次调用一行记录；trace_id 把重试、降级、失败串成完整链路。
  - 用标准库 sqlite3 内存库演示，无外部服务；生产换成同一个表结构的正式库。
  - 审计字段固定为 19 个，字段清单由 dataclass 自动生成，避免文档与代码漂移。

【易忽略细节 / 对照文档补足】
  1. 文档说"对齐 19 字段"但没列字段 → 这里给出可执行的 19 字段定义。
  2. 请求/响应原文可能含 api_key / token / 手机号，落库前必须脱敏。
  3. fallback_used 用 bool，SQLite 存 INTEGER，读回时要转正 bool。
  4. 降级后的 provider 才是真实账单主体，审计里的 provider 记实际模型厂商。

【示例用途】被 core_mechanisms/08、audit_lab、engineering_demo 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import re
import sqlite3
import uuid
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class AuditRecord:
    """每次调用一行，共 19 个字段（顺序即落库列顺序）。"""

    trace_id: str
    request_id: str
    timestamp: str
    user_id: str
    scenario: str
    provider: str
    model: str
    status: str
    http_status: int | None
    error_type: str
    error_message: str
    retry_count: int
    fallback_used: bool
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_yuan: float
    request_digest: str
    response_digest: str


AUDIT_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(AuditRecord))


def new_trace_id() -> str:
    """一次业务请求一个 trace；重试与降级共用同一个 trace。"""
    return uuid.uuid4().hex[:16]


def sanitize(text: str, limit: int = 200) -> str:
    """脱敏 + 截断：密钥、手机号、身份证号不得进审计库。"""
    masked = re.sub(
        r"(?i)(api[_-]?key|token|secret)\s*[=:]\s*[A-Za-z0-9_-]+",
        "***",
        text,
    )
    masked = re.sub(r"\b1[3-9]\d{9}\b", "***", masked)
    masked = re.sub(r"\b\d{17}[\dXx]\b", "***", masked)
    if len(masked) > limit:
        return masked[:limit] + "…"
    return masked


class SQLiteAuditStore:
    """最小审计存储：内存库即可跑通查询与报表。"""

    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        int_fields = {
            "http_status",
            "retry_count",
            "fallback_used",
            "input_tokens",
            "output_tokens",
        }
        real_fields = {"latency_ms", "cost_yuan"}
        columns = ", ".join(
            f"{name} "
            + (
                "INTEGER"
                if name in int_fields
                else "REAL"
                if name in real_fields
                else "TEXT"
            )
            for name in AUDIT_FIELDS
        )
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS audit_log ({columns})")
        self.conn.commit()

    def append(self, record: AuditRecord) -> None:
        values: dict[str, object] = {
            name: getattr(record, name) for name in AUDIT_FIELDS
        }
        values["fallback_used"] = int(record.fallback_used)
        placeholders = ", ".join("?" for _ in AUDIT_FIELDS)
        names = ", ".join(AUDIT_FIELDS)
        self.conn.execute(
            f"INSERT INTO audit_log ({names}) VALUES ({placeholders})",
            tuple(values[name] for name in AUDIT_FIELDS),
        )
        self.conn.commit()

    def find_by_trace(self, trace_id: str) -> list[AuditRecord]:
        """验收用：按 trace 查到完整链路（含失败与降级记录）。"""
        rows = self.conn.execute(
            "SELECT * FROM audit_log WHERE trace_id = ? ORDER BY timestamp, rowid",
            (trace_id,),
        ).fetchall()
        return [self._to_record(row) for row in rows]

    def find_by_date(self, day: str) -> list[AuditRecord]:
        rows = self.conn.execute(
            "SELECT * FROM audit_log WHERE timestamp LIKE ? ORDER BY timestamp, rowid",
            (f"{day}%",),
        ).fetchall()
        return [self._to_record(row) for row in rows]

    def all_records(self) -> list[AuditRecord]:
        rows = self.conn.execute("SELECT * FROM audit_log ORDER BY timestamp, rowid").fetchall()
        return [self._to_record(row) for row in rows]

    @staticmethod
    def _to_record(row: sqlite3.Row) -> AuditRecord:
        return AuditRecord(
            trace_id=row["trace_id"],
            request_id=row["request_id"],
            timestamp=row["timestamp"],
            user_id=row["user_id"],
            scenario=row["scenario"],
            provider=row["provider"],
            model=row["model"],
            status=row["status"],
            http_status=row["http_status"],
            error_type=row["error_type"],
            error_message=row["error_message"],
            retry_count=row["retry_count"],
            fallback_used=bool(row["fallback_used"]),
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            latency_ms=row["latency_ms"],
            cost_yuan=row["cost_yuan"],
            request_digest=row["request_digest"],
            response_digest=row["response_digest"],
        )


__all__ = [
    "AUDIT_FIELDS",
    "AuditRecord",
    "SQLiteAuditStore",
    "new_trace_id",
    "sanitize",
]
