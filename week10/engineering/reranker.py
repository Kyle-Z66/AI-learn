"""
第 10 周 · 工程层：确定性 reranker（教学版 cross-encoder）
================================================================
【对应知识点】文档第 10 周：cross-encoder 对 (query, doc) 联合打分

【周次学习要点】
  - 真实 cross-encoder 需下载模型；这里用确定性打分函数模拟"联合编码"的精度优势。
  - 打分复用第 9 周 tokenizer：同一套分词贯穿召回与精排，避免 token 漂移。
  - 可控延迟与故障注入让超时/异常分支可被单测稳定覆盖，不用真等 800ms。

【易忽略细节 / 对照文档补足】
  1. 首阶段用 bi-encoder（query/doc 分开编码）才快；rerank 是二阶段，不能当召回。
  2. 专名精确命中给显式加成：模拟 cross-encoder 能细看字面细节的能力。
  3. fail 注入抛 RuntimeError，fallback 层必须捕获并保持首阶段顺序。

【示例用途】被 fallback.py / engineering_demo.py / rerank_lab 引用；
             测试见 tests/week10/test_engineering.py
"""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from week09.engineering.bm25_index import tokenize

from week10.engineering.models import RerankCandidate

_PROPER_NOUN_RE = re.compile(r"[a-z]+[-_][0-9]+|[a-z0-9_]{4,}")


@dataclass(frozen=True)
class RerankerConfig:
    """教学参数：延迟、故障注入、批大小并发上限。"""

    delay_ms: float = 0.0
    fail: bool = False
    concurrency: int = 4

    def __post_init__(self) -> None:
        if self.delay_ms < 0 or self.concurrency < 1:
            raise ValueError("延迟必须 >= 0，并发数必须 >= 1")


def proper_nouns(text: str) -> set[str]:
    """抽取含数字的字母数字串（型号/错误码），作为精排的精确匹配信号。"""
    tokens = _PROPER_NOUN_RE.findall(text.lower())
    return {token for token in tokens if any(char.isdigit() for char in token)}


class DeterministicReranker:
    """离线可复现的精排器：score 是纯函数，score_async 可注入延迟/故障。"""

    def __init__(self, config: RerankerConfig | None = None) -> None:
        self.config = config if config is not None else RerankerConfig()

    def score(self, query: str, text: str) -> float:
        """联合打分：词项覆盖率 + 专名精确命中加成，结果落在 [0, 1]。"""
        query_tokens = set(tokenize(query))
        if not query_tokens:
            return 0.0
        text_tokens = set(tokenize(text))
        coverage = len(query_tokens & text_tokens) / len(query_tokens)
        exact = proper_nouns(query) & proper_nouns(text)
        bonus = 0.3 if exact else 0.0
        return min(1.0, coverage + bonus)

    async def score_async(self, query: str, text: str) -> float:
        """带可控延迟与故障注入的异步打分，供超时降级测试使用。"""
        if self.config.delay_ms > 0:
            await asyncio.sleep(self.config.delay_ms / 1000)
        if self.config.fail:
            raise RuntimeError("rerank 服务故障（教学注入）")
        return self.score(query, text)

    async def rerank(
        self,
        query: str,
        candidates: list[RerankCandidate],
    ) -> list[tuple[RerankCandidate, float]]:
        """并发打分后按精排分降序返回；同分按 chunk_id 兜底。"""
        scores = await asyncio.gather(
            *(self.score_async(query, candidate.text) for candidate in candidates)
        )
        pairs = list(zip(candidates, scores, strict=True))
        return sorted(pairs, key=lambda item: (-item[1], item[0].chunk_id))


__all__ = ["DeterministicReranker", "RerankerConfig", "proper_nouns"]
