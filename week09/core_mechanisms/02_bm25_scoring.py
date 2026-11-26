"""
第 9 周 · 核心机制 02：BM25 打分与中英文分词差异
================================================================
【对应知识点】文档第 9 周：BM25 路召回（rank_bm25 / ES 封装）

【周次学习要点】
  - BM25 = 词频饱和 × 逆文档频率 × 长度归一化；稀有词（专名）权重天然更高。
  - 中文要补单字 + 二元组；英文/型号/错误码按连续 token 整体保留。
  - 你做过的 ES 全文检索封装可直接平移：ES 的 analyzer 就是这里的 tokenizer。

【易忽略细节】
  1. 同一个 tokenizer 必须同时用于建索引和查询，否则专名永远召不回来。
  2. 全小写归一化后再分词，SGCC-4012 与 sgcc-4012 才能命中同一词条。
  3. 分数没有上界、量纲与 cosine 完全不同，这点在第 06 个样例展开。

【示例用途】可运行：`python -m week09.core_mechanisms.02_bm25_scoring`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.bm25_index import BM25Index, tokenize
from week09.engineering.models import Candidate

CORPUS: list[Candidate] = [
    Candidate("b1", "SGCC-4012 断路器巡检周期", "manual"),
    Candidate("b2", "SGCC-5200 隔离开关检修周期", "manual"),
    Candidate("b3", "ERR_4012 错误码表示通信链路超时", "error_codes"),
    Candidate("b4", "断路器巡检的通用注意事项", "manual"),
]


def show_tokens(text: str) -> list[str]:
    """打印并返回分词结果，便于对照 ES analyzer 的行为。"""
    tokens = tokenize(text)
    print(f"  {text!r} → {tokens}")
    return tokens


def bm25_top(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    """BM25 召回：专名 query 会把精确命中的文档顶到前面。"""
    return BM25Index(CORPUS).search(query, top_k=top_k)


def demo() -> None:
    print("中英文混合分词（与 ES analyzer 同思路）：")
    show_tokens("SGCC-4012 断路器巡检")
    show_tokens("ERR_4012 错误码")
    print("BM25 召回（查询：SGCC-4012 巡检）：")
    for doc_id, score in bm25_top("SGCC-4012 巡检"):
        print(f"  {doc_id}: {score:.4f}")
    print("稀有专名词条 IDF 高 → 精确命中文档排最前")


if __name__ == "__main__":
    demo()
