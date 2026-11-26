"""
第 10 周 · 核心机制 02：确定性教学版 cross-encoder 打分
================================================================
【对应知识点】文档第 10 周：cross-encoder 对 (query, doc) 联合打分

【周次学习要点】
  - 用"查询词项覆盖率 + 专名精确命中加成"模拟联合编码的相对排序能力。
  - 同一个 query 对不同 doc 分别打分；不像向量检索那样/doc 独立预计算。
  - 打分是纯函数，无模型下载、无随机性，单测可精确断言。

【易忽略细节】
  1. 这是教学替身，不声称等同于真实 bge-reranker 的语义理解能力。
  2. 专名命中给加成，是为了复现 cross-encoder 能看字面细节这一点。
  3. 分数范围压在 [0,1] 仅为便于阅读；真实模型分数没有统一量纲。

【示例用途】可运行：`python -m week10.core_mechanisms.02_rerank_score`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

from week10.engineering.reranker import DeterministicReranker

TEXTS = [
    "断路器通用巡检流程",
    "SGCC-4012 型号说明书",
    "SGCC-4012 断路器巡检周期与温度阈值",
]


def score_pair(query: str, text: str) -> float:
    """教学打分：查询词覆盖率 + 专名精确匹配加成。"""
    return DeterministicReranker().score(query, text)


def rank_texts(query: str, texts: list[str]) -> list[tuple[str, float]]:
    """按精排分降序返回 (文本, 分数)，同分按文本字典序兜底。"""
    pairs = [(text, score_pair(query, text)) for text in texts]
    return sorted(pairs, key=lambda item: (-item[1], item[0]))


def demo() -> None:
    query = "SGCC-4012 断路器巡检"
    for text, score in rank_texts(query, TEXTS):
        print(f"  {score:.4f} :: {text}")
    print("专名 + 主题同时命中的文档被顶到第一：这就是二阶段精排的价值")


if __name__ == "__main__":
    demo()
