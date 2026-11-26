"""
第 11 周 · 工程层：上下文预算与引用编号
================================================================
【对应知识点】文档第 11 周 build_context()：max_tokens 截断 + cited sources 同步

【周次学习要点】
  - 预算耗尽就停止追加，并标记 truncated：宁可少答，也不要悄悄把证据丢掉再编答案。
  - sources / chunks 与 text 必须来自同一轮循环，截断后三者天然同步。
  - 编号在"入选"时才分配，避免"答案引用 [3] 但上下文只有 [1][2]"的引用漂移。

【易忽略细节】
  1. count_tokens 是教学用近似估算（CJK 约 1 字/token，ASCII 约 4 字符/token），
     生产要换成目标模型的真实 tokenizer；估算偏小会导致上下文超限被服务端截断。
  2. 计划原文用 list 返回 cited，这里改 tuple： ContextBundle 是不可变值对象，
     避免调用方 append 造成 sources 与 text 不一致。
  3. Java 里常用 StringBuilder 逐段 append；Python 这里先收集 parts 再 join，
     一次性产出不可变文本，更适合做缓存与哈希。

【示例用途】被 generator.py / guards.py / core_mechanisms 02、03、09 引用；
             测试见 tests/week11/test_engineering.py
"""
from __future__ import annotations

from week11.engineering.models import Citation, ContextBundle, SourceChunk


def count_tokens(text: str) -> int:
    """估算 token 数：CJK 逐字计 1，其余按 4 字符 1 token 向上取整。"""
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f")
    other = len(text) - cjk
    return cjk + (other + 3) // 4


def build_context(
    chunks: list[SourceChunk],
    max_tokens: int = 4000,
) -> ContextBundle:
    """按预算顺序组装带编号上下文；截断时同步收窄 sources 与 chunks。"""
    parts: list[str] = []
    kept: list[SourceChunk] = []
    used = 0
    for chunk in chunks:
        cost = count_tokens(chunk.content)
        if used + cost > max_tokens:
            break  # 预算耗尽：后面的片段不进 Prompt，也不能进 cited sources
        number = len(kept) + 1
        parts.append(f"[{number}] {chunk.content}")
        kept.append(chunk)
        used += cost
    truncated = len(kept) < len(chunks)
    return ContextBundle(
        text="\n\n---\n\n".join(parts),
        sources=tuple(chunk.source for chunk in kept),
        chunks=tuple(kept),
        truncated=truncated,
        omitted_count=len(chunks) - len(kept),
    )


def citation_from_chunk(number: int, chunk: SourceChunk) -> Citation:
    """把编号与片段元数据打包成引用；出处从 chunk 派生，不另传字符串。"""
    return Citation(
        number=number,
        doc_id=chunk.doc_id,
        title=chunk.title,
        page=chunk.page,
        source=chunk.source,
    )


def citation_map(bundle: ContextBundle) -> dict[int, Citation]:
    """编号 → 引用 的映射表，供答案里的 [n] 后处理回查原文。"""
    return {
        number: citation_from_chunk(number, chunk)
        for number, chunk in enumerate(bundle.chunks, start=1)
    }
