"""
第 7 周 · 核心机制 10：小块检索 + 大块返回
================================================================
【对应知识点】文档第 7 周：策略 D（实验设计）—— small-to-big

【周次学习要点】
  - 大块负责保留上下文，小块负责精确命中；命中小块后返回它的 parent_text。
  - 父块编号写进 metadata.parent_chunk_id，便于去重与引用合并。
  - 这是"检索粒度 ≠ 生成粒度"的典型工程手法，不依赖任何模型。

【易忽略细节】
  1. 小块太短会丢失主谓宾，太长又退化成普通切分，96/160 都是教学起点。
  2. 同一父块命中多个小块时要按父块去重，否则 Prompt 里塞满重复上下文。
  3. parent_text 进 metadata 会增加索引体积，生产上可只存 parent_chunk_id 再回表。

【示例用途】可运行：`python -m week07.core_mechanisms.10_small_to_big`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import estimate_tokens, small_to_big


def small_to_big_stats() -> tuple[int, float, int]:
    """返回 (小块数, 小块平均 token, 唯一父块数)。"""
    chunks = small_to_big(build_corpus_document(), small_size=96, big_size=512)
    if not chunks:
        return 0, 0.0, 0
    average = sum(estimate_tokens(chunk.text) for chunk in chunks) / len(chunks)
    parents = {chunk.metadata["parent_chunk_id"] for chunk in chunks}
    return len(chunks), average, len(parents)


def demo() -> None:
    count, average, parents = small_to_big_stats()
    print(f"small-to-big：小块数={count} 小块平均 token={average:.1f} 父块数={parents}")
    print("命中小块后返回 metadata.parent_text，而不是小块本身。")


if __name__ == "__main__":
    demo()
