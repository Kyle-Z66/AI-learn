"""
第 12 周 · 工程层：四配置本地确定性评测
================================================================
【对应知识点】文档第 12 周：同一套查询集跑 BM25-only / dense-only / hybrid /
              hybrid+rerank，画对比表；必须跑出自己的真实数字

【周次学习要点】
  - 所有配置共享同一 golden set、同一语料、同一生成器，只换检索排序函数。
  - 逐案保存 retrieved_ids 与 recall：既能算 MRR，也能看分布而非只看平均分。
  - p95 延迟由 perf_counter 对每次真实调用计时得到，报告里注明"本地教学测量"。

【易忽略细节】
  1. 不能把参考答案塞给生成器：那是测试集泄漏，指标会虚高且无法复现。
  2. 计时包含检索 + 生成 + 引用组装，和线上真实请求边界一致；
     机器负载会造成毫秒级波动，所以报告数字从本次实跑输出抄写。
  3. Faithfulness 的实体清单固定为 "张伟/李娜"：这是教学语料里的专有名词，
     换真实数据时随 golden set 一起替换（见 p2_rag/README.md）。

【示例用途】被 engineering_demo.py / core_mechanisms/08 / tests/week12 引用；
             实跑结果抄入 p2_rag/REPORT.md
"""
from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter

from week12.engineering.metrics import (
    answer_relevance,
    context_precision,
    context_recall,
    faithfulness,
    mean,
    mrr,
    p95_latency_ms,
    recall_at_k,
)
from week12.engineering.models import CaseEvaluation, ConfigResult, EvalScores, GoldenCase
from week12.p2_rag.generation import generate_answer
from week12.p2_rag.retrieval import CONFIGS, get_chunks, retrieve

WATCH_ENTITIES: tuple[str, ...] = ("张伟", "李娜")
TOP_K = 5


def evaluate_case(case: GoldenCase, config: str) -> CaseEvaluation:
    """跑一条样本：真实计时 + 检索 + 生成 + 五项指标，不接触参考答案。"""
    started = perf_counter()
    ids = retrieve(case.question, config, top_k=TOP_K)
    chunks = get_chunks(ids)
    answer = generate_answer(case.question, chunks)
    latency_ms = (perf_counter() - started) * 1000
    context = "\n".join(chunk.content for chunk in chunks)
    return CaseEvaluation(
        recall_at_k=recall_at_k(ids, case.relevant_chunk_ids, k=TOP_K),
        context_precision=context_precision(ids, case.relevant_chunk_ids, k=TOP_K),
        context_recall=context_recall(ids, case.relevant_chunk_ids),
        faithfulness=faithfulness(answer.text, context, WATCH_ENTITIES),
        answer_relevance=answer_relevance(case.question, answer.text),
        latency_ms=latency_ms,
        retrieved_ids=tuple(ids),
    )


def run_evaluation(cases: Sequence[GoldenCase], config: str) -> ConfigResult:
    """跑一个配置：聚合成 EvalScores，并保留逐案 recall 供分布分析。"""
    per_case = [evaluate_case(case, config) for case in cases]
    recalls = tuple(item.recall_at_k for item in per_case)
    scores = EvalScores(
        recall_at_k=mean(recalls),
        mrr=mrr(
            [item.retrieved_ids for item in per_case],
            [case.relevant_chunk_ids for case in cases],
        ),
        context_precision=mean([item.context_precision for item in per_case]),
        context_recall=mean([item.context_recall for item in per_case]),
        faithfulness=mean([item.faithfulness for item in per_case]),
        answer_relevance=mean([item.answer_relevance for item in per_case]),
        p95_latency_ms=p95_latency_ms([item.latency_ms for item in per_case]),
    )
    return ConfigResult(config, scores, recalls, len(cases))


def run_all_configs(cases: Sequence[GoldenCase]) -> list[ConfigResult]:
    """按固定顺序跑四种配置，顺序稳定便于报告与 CI 对比。"""
    return [run_evaluation(cases, config) for config in CONFIGS]
