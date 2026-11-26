"""
第 8 周 · 核心机制 10：召回率基准
================================================================
【对应知识点】文档第 8 周：ANN 参数与召回率取舍

【周次学习要点】
  - recall@K = 近似结果在前 K 个里命中了多少精确 Top-K。
  - 必须有一套暴力精确结果作参照，否则"调参"只是自我感觉。
  - 本样例用候选子集模拟 ANN，只演示评估口径，不实现任何 ANN 算法。

【易忽略细节】
  1. 召回率的分母是精确 Top-K 大小，不是库的总记录数。
  2. 只调 ef_search/probes 不测召回，无法知道损失了多少正确答案。
  3. 第 7 周不做检索，本节是第 8 周"检索质量可度量"的落点。

【示例用途】可运行：`python -m week08.core_mechanisms.10_recall_benchmark`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

import importlib

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.vector_store import InMemoryVectorStore, similarity

STORE_MODULE = importlib.import_module("week08.core_mechanisms.08_vector_store")
QUERY = "ERR_4012 上游超时"


def recall_at_k(approximate: list[str], exact: list[str], k: int) -> float:
    """近似前 K 命中了精确前 K 的多少比例。"""
    expected = set(exact[:k])
    if not expected:
        return 0.0
    return len(set(approximate[:k]) & expected) / len(expected)


def simulated_ann_hits(
    store: InMemoryVectorStore,
    query: list[float] | tuple[float, ...],
    *,
    top_k: int,
    sample_ratio: float,
) -> list[str]:
    """模拟 ANN：只在部分候选里排序，用来观察召回损失。"""
    if not 0 < sample_ratio <= 1:
        raise ValueError("sample_ratio 必须在 (0, 1] 区间")
    records = store.records()
    sample_size = max(1, int(len(records) * sample_ratio))
    scored = [
        (record, similarity(query, record.vector, store.metric))
        for record in records[:sample_size]
    ]
    scored.sort(key=lambda item: (-item[1], item[0].id))
    return [record.id for record, _ in scored[:top_k]]


def benchmark() -> tuple[float, ...]:
    """返回 sample_ratio=0.3/0.6/1.0 时的 recall@3。"""
    store = STORE_MODULE.build_store()
    query = tuple(HashEmbedding(16).embed_query(QUERY))
    exact = [hit.record.id for hit in store.search(query, top_k=3)]
    return tuple(
        recall_at_k(
            simulated_ann_hits(store, query, top_k=3, sample_ratio=ratio),
            exact,
            3,
        )
        for ratio in (0.3, 0.6, 1.0)
    )


def demo() -> None:
    for ratio, recall in zip((0.3, 0.6, 1.0), benchmark(), strict=True):
        print(f"候选占比={ratio:.0%} → recall@3={recall:.0%}")
    print("候选越少延迟越低，但召回下降；生产上要画延迟-召回曲线再定参数。")


if __name__ == "__main__":
    demo()
