"""
第 12 周 · P2 项目：服务编排（检索 → 生成 → 引用）
================================================================
【对应知识点】文档第 12 周：P2 项目可运行、有 API、有评测报告

【周次学习要点】
  - RAGService.query() 是唯一业务入口：把检索配置、生成、引用串成一次调用。
  - self_check() 验证"相关问题有引用、无关问题拒答"，供 __main__ 与测试共用。
  - 计时用 perf_counter 而不是 time.time：后者受系统时钟调整影响。

【易忽略细节】
  1. 检索配置在 retrieve() 里校验，未知配置抛 ValueError；HTTP 层负责转成 422。
  2. 服务不保存跨请求状态：第 6 周的容器单例是审计/指标，这里由 app.py 单独维护。
  3. Java 里常用 @Service 单例 + 注入；这里用普通类，构造依赖直接传参，
     Java→Python 的思维差异是"少用容器，多用显式参数"。

【示例用途】被 app.py / __main__.py / tests/week12/test_p2_rag.py 引用。
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from week11.engineering.models import GeneratedAnswer

from week12.p2_rag.generation import generate_answer
from week12.p2_rag.retrieval import get_chunks, retrieve


@dataclass(frozen=True, slots=True)
class QueryOutcome:
    """一次查询的内部结果：答案 + 检索到的片段 ID + 真实耗时。"""

    answer: GeneratedAnswer
    retrieved_ids: tuple[str, ...]
    latency_ms: float


class RAGService:
    """P2 业务服务：配置在构造时固定，便于评测与部署时分流。"""

    def __init__(self, config: str = "hybrid", top_k: int = 5) -> None:
        self.config = config
        self.top_k = top_k

    def query(self, question: str) -> QueryOutcome:
        """检索 Top-K → 生成带引用答案 → 记录耗时。"""
        started = perf_counter()
        ids = retrieve(question, self.config, top_k=self.top_k)
        answer = generate_answer(question, get_chunks(ids))
        latency_ms = (perf_counter() - started) * 1000
        return QueryOutcome(answer, tuple(ids), latency_ms)

    def self_check(self) -> bool:
        """自检：相关问题有引用且守卫通过；无关问题被拒答。"""
        relevant = self.query("系统 cyclone 影响多少人？")
        irrelevant = self.query("公司火星基地的预算是多少？")
        return bool(
            relevant.answer.citations
            and relevant.answer.guard.passed
            and not relevant.answer.refused
            and irrelevant.answer.refused
        )
