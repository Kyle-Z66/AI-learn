"""
第 9 周 · 工程层：BM25 稀疏检索索引
================================================================
【对应知识点】文档第 9 周：BM25 路（rank_bm25 或 ES 封装）召回

【周次学习要点】
  - rank_bm25 是教学替身；生产上换成你熟悉的 ES，查询接口保持一致即可。
  - 中文按"单字 + 相邻二元组"切，英文/型号/错误码按连续字母数字整体保留。
  - query 与 doc 必须走同一个 tokenizer，否则专名永远召不回来。

【易忽略细节 / 对照文档补足】
  1. 文档只说"用 rank_bm25"，没说分词；纯 regex 会把中文整段当一个词，召回几乎为 0。
  2. SGCC-4012 / ERR_4012 若被拆散，BM25 的优势就没了 → 数字与字母前缀整体保留。
  3. 空语料时 BM25Okapi 会除零；这里显式返回空结果，让上层走纯向量分支。

【示例用途】被 hybrid_retriever.py / core_mechanisms/02、08 引用；
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from week09.engineering.models import Candidate

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+")


def tokenize(text: str) -> list[str]:
    """中英文混合分词：中文出单字+二元组，英文/型号/错误码整体保留。"""
    tokens: list[str] = []
    for segment in _TOKEN_RE.findall(text.lower()):
        if "\u4e00" <= segment[0] <= "\u9fff":
            tokens.extend(segment)
            tokens.extend(segment[i : i + 2] for i in range(len(segment) - 1))
        else:
            tokens.append(segment)
    return tokens


class BM25Index:
    """基于 rank_bm25 的稀疏索引；构造函数即建索引，过滤后需重建。"""

    def __init__(
        self,
        candidates: list[Candidate],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self._candidates = list(candidates)
        self._ids = [candidate.chunk_id for candidate in self._candidates]
        corpus = [tokenize(candidate.text) for candidate in self._candidates]
        self._model = BM25Okapi(corpus, k1=k1, b=b) if corpus else None

    def score_map(self, query: str) -> dict[str, float]:
        """返回 chunk_id → BM25 原始分，只保留正分。"""
        query_tokens = tokenize(query)
        if self._model is None or not query_tokens:
            return {}
        scores = self._model.get_scores(query_tokens)
        return {
            chunk_id: float(score)
            for chunk_id, score in zip(self._ids, scores, strict=True)
            if score > 0.0
        }

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """按分数降序返回 (chunk_id, score)；同分按 id 排序保证确定性。"""
        items = sorted(
            self.score_map(query).items(),
            key=lambda item: (-item[1], item[0]),
        )
        return items[:top_k]


__all__ = ["BM25Index", "tokenize"]
