"""
第 9 周 · 核心机制 10：三方消融对比（BM25 / 向量 / 混合）
================================================================
【对应知识点】文档第 9 周验收：纯向量 vs 混合的召回差异

【周次学习要点】
  - 消融 = 固定语料与查询，逐项去掉模块看指标掉多少。
  - 本周只做三方对比；完整评测体系（golden set / CI 门禁）是第 12 周。
  - 混合路用 RRF 融合；第 10 周会再加 rerank，形成第四组对照。

【易忽略细节】
  1. 三方必须用同一批 query 与同一个 K，否则数字不可比。
  2. 召回指标只说明"是否找到候选"，不说明答案质量，别过度解读。
  3. 教学语料是模拟知识库；报告只写程序真实跑出的数字。

【示例用途】可运行：`python -m week09.core_mechanisms.10_ablation`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

import importlib
from typing import Any

from week09.engineering.models import Candidate

# 模块名以数字开头，不能用普通 import 语句，和 week06 测试的做法一致。
_recall_module: Any = importlib.import_module("week09.core_mechanisms.09_recall_at_k")
CORPUS: list[Candidate] = _recall_module.CORPUS
QUERIES: list[tuple[str, set[str]]] = _recall_module.QUERIES
evaluate = _recall_module.evaluate


def ablation(k: int = 2) -> dict[str, float]:
    """返回三路在固定查询集上的平均 Recall@K。"""
    return {
        "bm25_only": evaluate("bm25", k=k),
        "dense_only": evaluate("dense", k=k),
        "hybrid_rrf": evaluate("hybrid", k=k),
    }


def demo() -> None:
    result = ablation()
    print(f"消融实验：{len(CORPUS)} 条候选 / {len(QUERIES)} 条查询 / RRF k=60")
    for name, score in result.items():
        print(f"  {name:<12} Recall@2 = {score:.3f}")
    best = max(result, key=lambda name: result[name])
    print(f"最优：{best}；混合检索把专名路与语义路的优势叠加")


if __name__ == "__main__":
    demo()
