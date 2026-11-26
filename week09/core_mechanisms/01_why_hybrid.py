"""
第 9 周 · 核心机制 01：为什么专有名词必须靠混合检索
================================================================
【对应知识点】文档第 9 周：纯向量对型号/错误码召回极差，混合是必需项

【周次学习要点】
  - 哈希/语义嵌入会把"型号数字"压成模糊维度：SGCC-4012 与 SGCC-5200 向量撞车。
  - BM25 恰好相反：字面精确匹配强，但同义改写召不回。
  - 本周的玩具向量是教学假设，用来复现"专名漂移"，不声称真实模型一定如此。

【易忽略细节】
  1. 漂移不是"向量算错"，而是嵌入空间本来就不为罕见标识符保留区分度。
  2. 用确定性玩具向量复现问题，单测可精确断言，不用下载任何模型。
  3. 第 7 周切分、第 8 周嵌入原理不重复；这里只接一句"向量路有盲区"。

【示例用途】可运行：`python -m week09.core_mechanisms.01_why_hybrid`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.bm25_index import BM25Index
from week09.engineering.dense_index import cosine_similarity
from week09.engineering.models import Candidate

TOY_DOCS: list[Candidate] = [
    Candidate("d1", "SGCC-4012 断路器型号说明", "manual"),
    Candidate("d2", "SGCC-5200 断路器型号说明", "manual"),
    Candidate("d3", "ERR_4012 错误码表示通信超时", "error_codes"),
    Candidate("d4", "断路器巡检流程与周期", "manual"),
]


def toy_embed(text: str) -> list[float]:
    """教学嵌入：只判断'有无型号位/断路器/巡检/错误'，数字被抹平。"""
    lowered = text.lower()
    return [
        1.0 if "4012" in lowered or "5200" in lowered else 0.0,
        1.0 if "断路器" in text else 0.0,
        1.0 if "巡检" in text else 0.0,
        1.0 if "err" in lowered or "错误" in text else 0.0,
    ]


def dense_scores(query: str) -> dict[str, float]:
    """玩具向量下的余弦分数；两个型号会得到完全相同的向量。"""
    query_vector = toy_embed(query)
    return {
        doc.chunk_id: cosine_similarity(query_vector, toy_embed(doc.text))
        for doc in TOY_DOCS
    }


def sparse_top(query: str) -> list[str]:
    """BM25 精确匹配：SGCC-4012 不会召回 SGCC-5200。"""
    return [doc_id for doc_id, _ in BM25Index(TOY_DOCS).search(query, top_k=2)]


def demo() -> None:
    query = "SGCC-4012 断路器"
    scores = dense_scores(query)
    print(f"查询：{query}")
    for doc_id, score in scores.items():
        print(f"  玩具向量 {doc_id}: cosine={score:.4f}")
    print("  → d1 / d2 型号不同却分数相同：专名在向量空间里漂移、撞车")
    print(f"  → BM25 Top-2：{sparse_top(query)}，字面专名被精确保留")
    print("结论：向量负责语义，BM25 负责专名；缺一路就有系统性盲区")


if __name__ == "__main__":
    demo()
