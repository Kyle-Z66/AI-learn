"""
第 12 周 · 工程层：检索侧与生成侧指标（全部本地确定性计算）
================================================================
【对应知识点】文档第 12 周：Recall@k / MRR@10 / Context Precision / Context Recall /
              Faithfulness / Answer Relevance / p95 延迟

【周次学习要点】
  - 检索侧指标只看"片段 ID 列表"与标注 ID 的集合关系，与具体向量实现无关。
  - 生成侧复用第 11 周守卫的抽取与分词函数：Faithfulness 查可核验声明，
    Answer Relevance 查问题与答案的实词交集。
  - p95 用 nearest-rank（排序后取 ceil(0.95n)-1），小样本也不会凭空插值。

【易忽略细节】
  1. Recall@k 的分母是标注相关片段数，不是 k；Context Precision 的分母才是 k。
     两者混用是面试高频扣分点。
  2. MRR 只在第一个命中处记 1/rank；同一批 case 的检索列表与标注列表必须等长，
     zip(strict=True) 让错位当场暴露。
  3. 答案没有可核验声明时 Faithfulness 返回 1.0 并在文档注明"无可核验声明"，
     不能把"没数字"当成"完全忠实"。
  4. Java 常用 Stream + Collectors；Python 这里用生成器表达式 + sum，
     短小且 mypy 可推断类型，不必引入统计库。

【示例用途】被 runner.py / ci_gate.py / core_mechanisms 03~07 引用；
             测试见 tests/week12/test_engineering.py
"""
from __future__ import annotations

import math
import re
from collections.abc import Sequence

from week11.engineering.guards import content_terms, extract_answer_numbers


def recall_at_k(retrieved: Sequence[str], relevant: Sequence[str], k: int = 5) -> float:
    """Recall@k：Top-K 命中的标注片段数 / 标注片段总数。"""
    if not relevant:
        return 0.0
    hits = set(retrieved[:k]) & set(relevant)
    return len(hits) / len(relevant)


def reciprocal_rank(retrieved: Sequence[str], relevant: Sequence[str], k: int = 10) -> float:
    """单个查询的 RR：第一个命中位置的倒数，未命中为 0。"""
    for rank, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def mrr(
    retrieved_per_query: Sequence[Sequence[str]],
    relevant_per_query: Sequence[Sequence[str]],
    k: int = 10,
) -> float:
    """MRR@k：所有查询 RR 的均值；长度不一致直接报错，避免悄悄错位。"""
    if not retrieved_per_query:
        return 0.0
    total = sum(
        reciprocal_rank(found, expected, k)
        for found, expected in zip(retrieved_per_query, relevant_per_query, strict=True)
    )
    return total / len(retrieved_per_query)


def context_precision(retrieved: Sequence[str], relevant: Sequence[str], k: int = 5) -> float:
    """Context Precision：Top-K 中相关片段占比，衡量"送进去的证据有多纯"。"""
    top = list(retrieved[:k])
    if not top:
        return 0.0
    return sum(1 for doc_id in top if doc_id in relevant) / len(top)


def context_recall(retrieved: Sequence[str], relevant: Sequence[str]) -> float:
    """Context Recall：全部检索结果对标注片段的覆盖率（不设 k）。"""
    if not relevant:
        return 0.0
    return len(set(retrieved) & set(relevant)) / len(relevant)


def _supported(claim: str, context: str) -> bool:
    if claim.isdigit():
        return re.search(rf"(?<!\d){re.escape(claim)}(?!\d)", context) is not None
    return claim in context


def faithfulness(
    answer: str,
    context: str,
    entities: Sequence[str] = (),
) -> float:
    """Faithfulness：答案中的数字/实体能在上下文找到的比例；无可核验声明记 1.0。"""
    claims: list[str] = list(extract_answer_numbers(answer))
    claims.extend(entity for entity in entities if entity in answer)
    if not claims:
        return 1.0
    supported = sum(1 for claim in claims if _supported(claim, context))
    return supported / len(claims)


def answer_relevance(question: str, answer: str) -> float:
    """Answer Relevance：答案覆盖问题实词的比例（教学版，无真实语义向量）。"""
    question_terms = content_terms(question)
    if not question_terms:
        return 0.0
    overlap = question_terms & content_terms(answer)
    return min(1.0, len(overlap) / len(question_terms))


def p95_latency_ms(latencies: Sequence[float]) -> float:
    """nearest-rank p95：升序取第 ceil(0.95n) 个数，空样本返回 0。"""
    if not latencies:
        return 0.0
    ordered = sorted(latencies)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def mean(values: Sequence[float]) -> float:
    """算术平均；空序列返回 0，避免评测空集时抛异常。"""
    return sum(values) / len(values) if values else 0.0
