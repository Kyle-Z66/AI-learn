"""
第 7 周 · 核心机制 09：语义切分（词汇重合度近似）
================================================================
【对应知识点】文档第 7 周：策略 D —— 语义切分

【周次学习要点】
  - 第 7 周不引入 embedding，用相邻行的 Jaccard 词重合度近似"主题漂移"。
  - 相似度骤降或超出 token 预算就断段，得到一个语义相对集中的组。
  - 第 8 周拿到向量后可把这里的 lexical_similarity 换成余弦相似度，接口不变。

【易忽略细节】
  1. 短行之间共同的"第/条"会抬高相似度，所以阈值要低（这里 0.05）。
  2. 语义切分结果不稳定：换一份语料就要重调阈值，不要当成万能方案。
  3. 它仍是长度 + 相似度的组合，超长组还会回退到递归切分兜底。

【示例用途】可运行：`python -m week07.core_mechanisms.09_semantic_chunking`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import lexical_similarity, lexical_tokens, semantic


def semantic_chunk_stats() -> tuple[int, float]:
    """返回 (chunk 数, 相邻行平均词重合度)。"""
    document = build_corpus_document()
    lines = [line.strip() for line in document.text.splitlines() if line.strip()]
    pairs = [
        lexical_similarity(lexical_tokens(left), lexical_tokens(right))
        for left, right in zip(lines, lines[1:], strict=False)
    ]
    average = sum(pairs) / len(pairs) if pairs else 0.0
    return len(semantic(document, chunk_size=512, threshold=0.05)), average


def demo() -> None:
    count, average = semantic_chunk_stats()
    print(f"语义切分：chunk 数={count} 相邻行平均词重合度={average:.3f}")
    print("提示：重合度低并非一定换主题，短条款行天然词少；阈值需按语料调。")


if __name__ == "__main__":
    demo()
