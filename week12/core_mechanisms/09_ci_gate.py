"""
第 12 周 · 核心机制 09：CI 阈值比较与退出码语义
================================================================
【对应知识点】文档第 12 周：用 pytest / GitHub Actions 做评测回归

【周次学习要点】
  - 质量指标下降超容差即回归；延迟上升超容差也算回归，方向不能搞反。
  - GateResult.exit_code() 是唯一 CI 契约：0 通过、1 回归。
  - 门禁一次收齐所有退化项，避免"修一个再报下一个"的迭代。

【易忽略细节】
  1. 容差必须按数据集与机器标定；0.02 / 25ms 只是教学起点，不是线上 SLA。
  2. 门禁挡的是退化，不是给配置排名：分数低但没退化的配置同样能通过。
  3. Java 里常用抛异常终止构建；这里返回退出码，pytest 脚本与 CLI 可共用判定。

【示例用途】可运行：`python -m week12.core_mechanisms.09_ci_gate`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.ci_gate import compare_to_baseline, run_gate
from week12.engineering.models import EvalScores

BASELINE = EvalScores(0.90, 0.80, 0.70, 0.88, 0.85, 0.60, 40.0)
CURRENT = EvalScores(0.89, 0.79, 0.69, 0.87, 0.84, 0.59, 45.0)
BROKEN = EvalScores(0.80, 0.70, 0.62, 0.78, 0.75, 0.50, 70.0)


def demo() -> None:
    for label, scores in (("轻微波动", CURRENT), ("明显退化", BROKEN)):
        gate = compare_to_baseline(scores, BASELINE)
        print(f"{label}: passed={gate.passed} 退化项={gate.regressions} "
              f"exit_code={gate.exit_code()}")
    print(f"run_gate(明显退化) = {run_gate(BROKEN, BASELINE)}（CI 里非 0 即失败）")


if __name__ == "__main__":
    demo()
