"""
第 12 周 · 工程层：CI 回归门禁（阈值比较 + 退出码语义）
================================================================
【对应知识点】文档第 12 周：用 pytest / GitHub Actions 做评测回归

【周次学习要点】
  - 门禁比较"当前 vs 基线"：质量指标下降超容差即回归，延迟上升超容差也算。
  - 退出码 0 = 通过、1 = 回归：这是 CI 能直接消费的唯一契约。
  - 门禁是护栏不是成绩单：它只挡退化，不代替人工看报告与分布。

【易忽略细节】
  1. 容差默认 0.02（质量）/ 25ms（延迟）；真实项目要按机器与数据集标定，
     不能拿示意数值当 SLA。
  2. 延迟与质量方向相反：质量 delta = 基线 - 当前（越大越差），
     延迟 delta = 当前 - 基线（越大越差），符号别写反。
  3. Java 里常用抛异常终止流程；这里返回 GateResult + exit_code()，
     CLI 与 pytest 都能复用同一判定，不必在两处复制阈值。

【示例用途】被 engineering_demo.py / core_mechanisms/09 / tests/week12 引用。
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass

from week12.engineering.models import EvalScores

QUALITY_KEYS: tuple[str, ...] = (
    "recall_at_k",
    "mrr",
    "context_precision",
    "context_recall",
    "faithfulness",
    "answer_relevance",
)
DEFAULT_THRESHOLDS: dict[str, float] = {
    **{key: 0.02 for key in QUALITY_KEYS},
    "p95_latency_ms": 25.0,
}


@dataclass(frozen=True, slots=True)
class GateResult:
    """门禁结论：是否通过、退化项、各指标有符号变化量。"""

    passed: bool
    regressions: tuple[str, ...]
    deltas: dict[str, float]

    def exit_code(self) -> int:
        """CI 契约：0 通过，1 回归。"""
        return 0 if self.passed else 1


def compare_to_baseline(
    current: EvalScores,
    baseline: EvalScores,
    thresholds: Mapping[str, float] | None = None,
) -> GateResult:
    """比较当前与基线；任一指标退化超容差即判失败，但收集全部退化项。"""
    rules = DEFAULT_THRESHOLDS if thresholds is None else thresholds
    current_values = asdict(current)
    baseline_values = asdict(baseline)
    deltas: dict[str, float] = {}
    regressions: list[str] = []
    for key, tolerance in rules.items():
        now = float(current_values[key])
        old = float(baseline_values[key])
        delta = old - now if key in QUALITY_KEYS else now - old
        deltas[key] = delta
        if delta > tolerance:
            regressions.append(key)
    return GateResult(not regressions, tuple(regressions), deltas)


def run_gate(
    current: EvalScores,
    baseline: EvalScores,
    thresholds: Mapping[str, float] | None = None,
) -> int:
    """CI 脚本入口：直接返回退出码。"""
    return compare_to_baseline(current, baseline, thresholds).exit_code()
