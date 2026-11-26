"""
第 9 周 · 补足要点：混合检索的定位、经验平移与稳定性
================================================================
【对应知识点】文档第 9 周：为什么混合是必需项；RRF k=60 的取值

【周次学习要点】
  - 混合不是"锦上添花"：专名召回是硬需求，纯向量在型号/错误码上有系统性盲区。
  - 你做过的 ES 全文检索封装几乎是直接平移：analyzer → tokenizer，filter → 前置过滤。
  - RRF 的 k 越大，排名差距被压得越平，结果更稳；k 太小会退化成只看第一名。

【易忽略细节】
  1. 第 7 周切分、第 8 周嵌入原理本周不重复，只做衔接与复用。
  2. 第 10 周才做 rerank；本周把"先召回准"这件事做扎实，别越界。
  3. ES 的 score 与 BM25 原始分也不是同一套绝对值，跨引擎比较同样要归一化。

【示例用途】可运行：`python -m week09.pitfalls.extra_gotchas`
             测试见 tests/week09/test_pitfalls.py
"""
from __future__ import annotations

from week09.engineering.fusion import reciprocal_rank_fusion

HYBRID_NECESSITY = [
    ("型号 / 错误码", "语义空间漂移，近似词占据排名", "BM25 字面精确命中"),
    ("同义问法", "字面不匹配，BM25 无能为力", "向量靠语义近邻命中"),
    ("部门 / 有效期", "两路都可能召回越权内容", "前置过滤统一拦截"),
]

ES_MAPPING = [
    ("ES analyzer", "week09.engineering.bm25_index.tokenize"),
    ("ES bool filter", "HybridRetriever._filter（召回前）"),
    ("ES _score", "BM25 score（仅本路内部可比）"),
    ("ES 多查询 RRF", "reciprocal_rank_fusion（k=60）"),
]

RANKING_A = ["c-01", "c-02", "c-03"]
RANKING_B = ["c-02", "c-01", "c-04"]


def demo_necessity() -> None:
    for scenario, weakness, remedy in HYBRID_NECESSITY:
        print(f"{scenario:<12} | 盲区：{weakness:<24} | 补位：{remedy}")


def demo_es_mapping() -> None:
    print("Java/ES 经验平移表：")
    for source, target in ES_MAPPING:
        print(f"  {source:<20} → {target}")


def demo_rrf_k_stability() -> None:
    for k in (5, 60):
        fused = reciprocal_rank_fusion([RANKING_A, RANKING_B], k=k)
        print(f"k={k:<3} 融合顺序：{fused}")
    print("k=60 时头部差距被压缩，单路第一名不再垄断结果")


def demo() -> None:
    demo_necessity()
    demo_es_mapping()
    demo_rrf_k_stability()


if __name__ == "__main__":
    demo()
