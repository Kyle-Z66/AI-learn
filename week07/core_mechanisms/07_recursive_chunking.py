"""
第 7 周 · 核心机制 07：递归字符切分
================================================================
【对应知识点】文档第 7 周：策略 B —— RecursiveCharacterTextSplitter 512/64

【周次学习要点】
  - 按 "\\n\\n" → "\\n" → "。" → "；" 的优先级递归拆，尽量在自然边界断句。
  - 拆出的小片段再打包到 token 预算内，超预算时从上一段尾部取 overlap。
  - 与固定切分相比，断点更可读，但仍是"长度驱动"而非"语义驱动"。

【易忽略细节】
  1. 分隔符顺序决定断点质量：把句号放在换行之前会把段落切得支离破碎。
  2. 递归时保留分隔符本身，否则中文句号丢失，chunk 读起来不像完整句子。
  3. overlap 只在片段打包阶段加，重复的是"上一结尾"，不是整段文档。

【示例用途】可运行：`python -m week07.core_mechanisms.07_recursive_chunking`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import DEFAULT_SEPARATORS, estimate_tokens, recursive


def recursive_chunk_stats() -> tuple[int, float, int]:
    """返回 (chunk 数, 平均 token, 使用的分隔符数量)。"""
    document = build_corpus_document()
    chunks = recursive(document, chunk_size=512, overlap=64, separators=DEFAULT_SEPARATORS)
    if not chunks:
        return 0, 0.0, 0
    average = sum(estimate_tokens(chunk.text) for chunk in chunks) / len(chunks)
    return len(chunks), average, len(DEFAULT_SEPARATORS)


def demo() -> None:
    count, average, separators = recursive_chunk_stats()
    print(f"递归切分：chunk 数={count} 平均 token={average:.1f}")
    print(f"分隔符优先级共 {separators} 级：段落 > 换行 > 句号 > 分号")
    print("人工检查点：断点是否落在条款边界，而不是条款中间。")


if __name__ == "__main__":
    demo()
