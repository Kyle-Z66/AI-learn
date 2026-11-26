"""
第 10 周 · 核心机制 03：候选预算（交互式 30~50 / 离线 100+）
================================================================
【对应知识点】文档第 10 周：50 个 ~310ms，100 个 ~590ms

【周次学习要点】
  - 交互式对话用户等不起：rerank 30~50 个候选，超时就降级。
  - 批处理没有用户盯着：可以 rerank 100+，用延迟换召回质量。
  - 候选预算是"首阶段给多少"与"二阶段看多少"之间的明确分工。

【易忽略细节】
  1. 首阶段仍要召回足够多；预算限制的是 rerank 的条数，不是召回条数。
  2. 延迟数字来自文档的工程经验，本工程用线性模型示意（第 08 个样例）。
  3. 预算不是越大越好：边际收益递减，延迟线性增长。

【示例用途】可运行：`python -m week10.core_mechanisms.03_candidate_budget`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

from typing import Literal

Mode = Literal["interactive", "batch"]

BUDGETS: dict[Mode, int] = {"interactive": 50, "batch": 120}


def candidate_budget(mode: Mode) -> int:
    """返回该场景下 rerank 的候选上限。"""
    return BUDGETS[mode]


def demo() -> None:
    for mode in ("interactive", "batch"):
        budget = candidate_budget(mode)  # type: ignore[arg-type]
        print(f"{mode:<12} rerank 候选上限={budget}")
    print("交互式优先保延迟，批处理优先保质量；两者共用同一套降级链")


if __name__ == "__main__":
    demo()
