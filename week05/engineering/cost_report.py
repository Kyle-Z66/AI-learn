"""
第 5 周 · 工程层：按 provider 差异化计价 + 日成本聚合
================================================================
【对应知识点】文档第 5 周：成本按 provider 差异化计算、成本日聚合报表

【周次学习要点】
  - 单价来自配置（第 2 周"不硬编码价格"的延续），公式直接复用第 3 周 calculate_cost。
  - 审计记录已经带 cost_yuan，报表按 (日期, provider, 场景) 聚合即可。
  - 降级后的 provider 才是真实账单主体，不能用"首选模型单价"记账。

【易忽略细节 / 对照文档补足】
  1. 文档只说"差异化计算"没给单价表结构 → 这里用 PriceRule 表达每千 token 单价。
  2. 示意单价不是实时价格；生产必须从配置中心读，不能写死在代码里。
  3. 按 trace 的多条记录都要计入，否则重试与降级的成本会被漏掉。

【示例用途】被 core_mechanisms/09、audit_lab、engineering_demo 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from week03.engineering.gateway_protocol import calculate_cost

from week05.engineering.audit import AuditRecord


@dataclass(frozen=True)
class PriceRule:
    """每千 token 单价，单位元；仅教学示意值。"""

    input_per_1k: float
    output_per_1k: float


PRICING: dict[str, PriceRule] = {
    "qwen": PriceRule(0.8, 2.0),
    "deepseek": PriceRule(0.5, 1.0),
    "glm": PriceRule(0.5, 1.5),
}


@dataclass(frozen=True)
class CostRow:
    """报表一行：按天 / provider / 场景聚合的结果。"""

    day: str
    provider: str
    scenario: str
    requests: int
    input_tokens: int
    output_tokens: int
    cost_yuan: float


@dataclass
class _Aggregate:
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_yuan: float = 0.0

    def add(self, record: AuditRecord) -> None:
        self.requests += 1
        self.input_tokens += record.input_tokens
        self.output_tokens += record.output_tokens
        self.cost_yuan += record.cost_yuan


def estimate_cost(provider: str, input_tokens: int, output_tokens: int) -> float:
    """按 provider 单价估算成本；未知 provider 快速失败。"""
    rule = PRICING.get(provider)
    if rule is None:
        raise KeyError(f"未配置 provider 单价：{provider}")
    return calculate_cost(input_tokens, output_tokens, rule.input_per_1k, rule.output_per_1k)


def build_daily_report(
    records: Iterable[AuditRecord],
    *,
    provider: str | None = None,
    day: str | None = None,
) -> list[CostRow]:
    """按 (日期, provider, 场景) 聚合；可选按 provider / 日期过滤。"""
    buckets: dict[tuple[str, str, str], _Aggregate] = {}
    for record in records:
        if provider is not None and record.provider != provider:
            continue
        record_day = record.timestamp[:10]
        if day is not None and record_day != day:
            continue
        key = (record_day, record.provider, record.scenario)
        buckets.setdefault(key, _Aggregate()).add(record)
    return [
        CostRow(*key, agg.requests, agg.input_tokens, agg.output_tokens, agg.cost_yuan)
        for key, agg in sorted(buckets.items())
    ]


def format_report(rows: list[CostRow]) -> str:
    """打印成对齐表格，便于验收时直接看结果。"""
    lines = ["日期       | 厂商      | 场景       | 次数 | 输入token | 输出token | 成本(元)"]
    for row in rows:
        lines.append(
            f"{row.day} | {row.provider:<8} | {row.scenario:<8} | "
            f"{row.requests:>4} | {row.input_tokens:>9} | "
            f"{row.output_tokens:>9} | {row.cost_yuan:>8.4f}"
        )
    lines.append(f"合计 {sum(row.cost_yuan for row in rows):.4f} 元")
    return "\n".join(lines)


__all__ = [
    "CostRow",
    "PRICING",
    "PriceRule",
    "build_daily_report",
    "estimate_cost",
    "format_report",
]
