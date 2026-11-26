"""
第 7 周 · 核心机制 06：固定长度切分
================================================================
【对应知识点】文档第 7 周：策略 A —— 固定 512 token，overlap 64

【周次学习要点】
  - 滑窗按 token 预算推进，overlap 从上一段尾部取，保证上下文不断得太突兀。
  - 实现最简单、成本最低，但会在条款编号与表格中间硬切。
  - 作为基线存在：其他策略是否更好，要和它比才知道。

【易忽略细节】
  1. overlap 太大时相邻 chunk 高度重复，Top-K 里全是近似内容，有效信息变少。
  2. chunk_size 超过 reranker 输入上限时，检索再准也会被截断。
  3. 中文不宜直接用 len(text) 当 token 数；这里用"汉字 1 / 英文词 1"的近似。

【示例用途】可运行：`python -m week07.core_mechanisms.06_fixed_chunking`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import estimate_tokens, fixed_size


def fixed_chunk_stats() -> tuple[int, float, float]:
    """返回 (chunk 数, 平均 token, overlap 占比)。"""
    document = build_corpus_document()
    chunks = fixed_size(document, chunk_size=512, overlap=64)
    if not chunks:
        return 0, 0.0, 0.0
    average = sum(estimate_tokens(chunk.text) for chunk in chunks) / len(chunks)
    overlapped = sum(
        1
        for previous, current in zip(chunks, chunks[1:], strict=False)
        if current.text[:16] in previous.text
    )
    return len(chunks), average, overlapped / max(1, len(chunks) - 1)


def demo() -> None:
    count, average, ratio = fixed_chunk_stats()
    print(f"固定切分：chunk 数={count} 平均 token={average:.1f}")
    print(f"相邻块存在重复前缀的比例={ratio:.0%}（overlap 64 的直接代价）")
    print("人工检查点：表格行与第 N 条是否被切断。")


if __name__ == "__main__":
    demo()
