"""
第 10 周 · 工程层：Rerank 候选项与结果模型
================================================================
【对应知识点】文档第 10 周：cross-encoder 精排 Top-50 → Top-5 与降级标记

【周次学习要点】
  - RerankCandidate 保留首阶段分数 stage_score，便于对比"精排前后顺序变化"。
  - RerankResult 显式带 degraded 与 reason，指标统计才知道哪些请求走了降级。
  - 模型只承载数据；打分、并发、超时分别放在 reranker.py / fallback.py。

【易忽略细节 / 对照文档补足】
  1. 文档只返回重排后的列表，没有降级标记 → 线上无法统计降级率，这里补上。
  2. Java 侧 DTO 思维可直接平移：不可变结果 + 明确字段，别用裸 dict 到处传。
  3. scores 用 chunk_id 索引而不是按下标，降级时也能对齐首阶段候选。

【示例用途】被 reranker.py / fallback.py / engineering_demo.py 引用；
             测试见 tests/week10/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RerankCandidate:
    """首阶段召回的一条候选；stage_score 是混合检索的融合分。"""

    chunk_id: str
    text: str
    stage_score: float = 0.0
    source: str = ""


@dataclass(frozen=True)
class RerankResult:
    """精排结果：候选列表 + 是否降级 + 降级原因 + 各候选精排分。"""

    candidates: list[RerankCandidate]
    degraded: bool = False
    reason: str = ""
    scores: dict[str, float] = field(default_factory=dict)


__all__ = ["RerankCandidate", "RerankResult"]
