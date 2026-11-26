"""
第 7 周 · 工程层：五种可对比的切分策略
================================================================
【对应知识点】文档第 7 周：固定 / 递归 / 标题 / 语义 / small-to-big 切分

【周次学习要点】
  - 统一入口都是 (Document) -> list[Chunk]，只有参数不同，便于同语料对照。
  - token 估算用"ASCII 词或单个汉字算 1"，比 len(text) 更接近中文 embedding 口径。
  - small-to-big 把大块放进 metadata.parent_text：检索小块，返回大块上下文。

【易忽略细节 / 对照文档补足】
  1. overlap 不是越大越好：重复内容会稀释 Top-K 多样性，也放大索引体积。
  2. 标题前缀必须拼进每个子 chunk，否则脱离标题的条款无法独立检索。
  3. 语义切分在第 7 周只能用词汇重合度近似，不调用 embedding（那是第 8 周）。
  4. 多页 PDF 用换页符定位 chunk 页码，切分后仍能回查来源页。

【示例用途】core_mechanisms/06~10、chunking_lab/evaluate.py 与测试共用
"""
from __future__ import annotations

import re

from week07.engineering.models import PAGE_SEPARATOR, Chunk, Document

DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", "。", "；", "，", " ")
_UNIT_RE = re.compile(r"[A-Za-z0-9_]+|\s+|.", re.DOTALL)
_TOKEN_SET_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def token_units(text: str) -> list[str]:
    """把文本切成"ASCII 词 / 空白 / 单字符"单元，空白单独保留以便还原原文。"""
    return _UNIT_RE.findall(text)


def estimate_tokens(text: str) -> int:
    """粗估 token 数：非空白单元各算 1，中文按字计、英文按词计。"""
    return sum(1 for unit in token_units(text) if not unit.isspace())


def page_for_offset(document: Document, offset: int) -> int:
    """按换页符数量回推 chunk 所在页码。"""
    return document.page + document.text.count(PAGE_SEPARATOR, 0, max(0, offset))


def _locate(document: Document, fragment: str) -> int:
    """在原文中定位片段，用于给递归/语义切分产生的 chunk 标页码。"""
    probe = fragment[:24]
    if not probe:
        return 0
    position = document.text.find(probe)
    return position if position >= 0 else 0


def _make_chunk(
    document: Document,
    index: int,
    text: str,
    *,
    offset: int = 0,
    title_path: str = "",
    strategy: str,
    extras: dict[str, str] | None = None,
) -> Chunk:
    metadata = {"strategy": strategy}
    if extras:
        metadata.update(extras)
    return Chunk(
        chunk_id=f"{document.doc_id}-c{index:03d}",
        doc_id=document.doc_id,
        text=text,
        title_path=title_path,
        page=page_for_offset(document, offset),
        source=document.path,
        metadata=metadata,
    )


def _sliding_windows(text: str, size: int, overlap: int) -> list[tuple[str, int]]:
    """按 token 预算滑动窗口，返回 (窗口文本, 原文字符偏移)。"""
    units = token_units(text)
    if not units:
        return []
    if size <= 0:
        raise ValueError("chunk_size 必须为正整数")
    overlap = max(0, min(overlap, size - 1))
    offsets: list[int] = []
    position = 0
    for unit in units:
        offsets.append(position)
        position += len(unit)

    windows: list[tuple[str, int]] = []
    start = 0
    while start < len(units):
        end = start
        used = 0
        while end < len(units) and used < size:
            if not units[end].isspace():
                used += 1
            end += 1
        window = "".join(units[start:end]).strip()
        if window:
            windows.append((window, offsets[start]))
        if end >= len(units):
            break
        back = 0
        cursor = end
        while cursor > start and back < overlap:
            cursor -= 1
            if not units[cursor].isspace():
                back += 1
        start = max(cursor, start + 1)
    return windows


def fixed_size(
    document: Document, *, chunk_size: int = 512, overlap: int = 64
) -> list[Chunk]:
    """策略 A：纯滑窗，不理会使文本语义断裂。"""
    windows = _sliding_windows(document.text, chunk_size, overlap)
    return [
        _make_chunk(document, index, text, offset=offset, strategy="fixed_size")
        for index, (text, offset) in enumerate(windows, start=1)
    ]


def _recursive_parts(text: str, size: int, separators: tuple[str, ...]) -> list[str]:
    """按分隔符优先级递归拆到每段不超过 size 个 token。"""
    if estimate_tokens(text) <= size:
        return [text] if text.strip() else []
    if not separators:
        return [window for window, _ in _sliding_windows(text, size, 0)]
    separator = separators[0]
    if separator not in text:
        return _recursive_parts(text, size, separators[1:])
    pieces = [piece.strip() for piece in text.split(separator) if piece.strip()]
    if len(pieces) == 1:
        return _recursive_parts(text, size, separators[1:])
    restored = [piece + separator for piece in pieces[:-1]] + [pieces[-1]]
    result: list[str] = []
    for piece in restored:
        result.extend(_recursive_parts(piece, size, separators[1:]))
    return result


def _tail_tokens(text: str, count: int) -> str:
    """取文本末尾 count 个 token 作为 overlap 前缀。"""
    units = token_units(text)
    kept: list[str] = []
    cursor = len(units) - 1
    while cursor >= 0 and len(kept) < count:
        kept.append(units[cursor])
        cursor -= 1
    return "".join(reversed(kept)).strip()


def _pack(parts: list[str], size: int, overlap: int) -> list[str]:
    """把小片段打包到 token 预算内，并从上一块尾部取 overlap。"""
    groups: list[str] = []
    buffer = ""
    for part in parts:
        candidate = f"{buffer}\n{part}" if buffer else part
        if estimate_tokens(candidate) <= size:
            buffer = candidate
            continue
        if buffer:
            groups.append(buffer)
            prefix = _tail_tokens(buffer, overlap)
            buffer = f"{prefix}\n{part}" if prefix else part
        else:
            groups.append(part)
            buffer = ""
    if buffer:
        groups.append(buffer)
    return groups


def recursive(
    document: Document,
    *,
    chunk_size: int = 512,
    overlap: int = 64,
    separators: tuple[str, ...] = DEFAULT_SEPARATORS,
) -> list[Chunk]:
    """策略 B：优先在段落/句号等自然边界断开，再打包。"""
    parts = _recursive_parts(document.text, chunk_size, separators)
    groups = _pack(parts, chunk_size, overlap)
    return [
        _make_chunk(
            document,
            index,
            text,
            offset=_locate(document, text),
            strategy="recursive",
        )
        for index, text in enumerate(groups, start=1)
    ]


def markdown_heading(document: Document, *, chunk_size: int = 512) -> list[Chunk]:
    """策略 C：按标题层级切分，并把 title_path 拼进每个 chunk。"""
    known = set(document.sections)
    stack: dict[int, str] = {}
    title_path = ""
    buffer: list[str] = []
    material: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal buffer
        body = "\n".join(buffer).strip()
        buffer = []
        if not body:
            return
        allowance = max(32, chunk_size - estimate_tokens(title_path))
        for part in _recursive_parts(body, allowance, DEFAULT_SEPARATORS):
            material.append((title_path, part))

    for raw in document.text.splitlines():
        stripped = raw.strip()
        match = _HEADING_RE.match(stripped)
        level: int | None = None
        name: str | None = None
        if match:
            level, name = len(match.group(1)), match.group(2).strip()
        elif stripped in known and len(stripped) <= 60:
            level, name = 1, stripped
        if level is not None and name is not None:
            flush()
            for key in list(stack):
                if key > level:
                    del stack[key]
            stack[level] = name
            title_path = " / ".join(stack[key] for key in sorted(stack))
        else:
            buffer.append(raw)
    flush()

    result: list[Chunk] = []
    for index, (path, part) in enumerate(material, start=1):
        text = f"{path}\n{part}" if path else part
        result.append(
            _make_chunk(
                document,
                index,
                text,
                offset=_locate(document, part),
                title_path=path,
                strategy="markdown_heading",
            )
        )
    return result


def lexical_tokens(text: str) -> set[str]:
    """词集合：用于无 embedding 条件下的主题漂移近似。"""
    return set(_TOKEN_SET_RE.findall(text.lower()))


def lexical_similarity(left: set[str], right: set[str]) -> float:
    """Jaccard 相似度；空集合返回 0。"""
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def semantic(
    document: Document, *, chunk_size: int = 512, threshold: float = 0.05
) -> list[Chunk]:
    """策略 D：相邻行词汇重合度骤降处断段（教学版，不用 embedding）。"""
    lines = [line.strip() for line in document.text.splitlines() if line.strip()]
    groups: list[str] = []
    buffer = ""
    previous: set[str] = set()
    for line in lines:
        current = lexical_tokens(line)
        similarity = lexical_similarity(previous, current) if previous else 1.0
        candidate = f"{buffer}\n{line}" if buffer else line
        if buffer and (similarity < threshold or estimate_tokens(candidate) > chunk_size):
            groups.append(buffer)
            buffer = line
        else:
            buffer = candidate
        previous = current
    if buffer:
        groups.append(buffer)

    final: list[str] = []
    for group in groups:
        if estimate_tokens(group) <= chunk_size:
            final.append(group)
        else:
            final.extend(_pack(_recursive_parts(group, chunk_size, DEFAULT_SEPARATORS),
                               chunk_size, 0))
    return [
        _make_chunk(
            document,
            index,
            text,
            offset=_locate(document, text),
            strategy="semantic",
        )
        for index, text in enumerate(final, start=1)
    ]


def small_to_big(
    document: Document,
    *,
    small_size: int = 160,
    big_size: int = 512,
    overlap: int = 32,
) -> list[Chunk]:
    """策略 E：小块用于检索，metadata.parent_text 保存大块供返回。"""
    if small_size <= 0 or big_size <= 0:
        raise ValueError("small_size 与 big_size 必须为正整数")
    if small_size > big_size:
        raise ValueError("small_size 不能大于 big_size")
    # 父块优先沿用标题策略：保留 title_path 后，小块命中即可回答"属于哪一节"。
    parents = markdown_heading(document, chunk_size=big_size)
    result: list[Chunk] = []
    for parent in parents:
        windows = _sliding_windows(parent.text, small_size, min(overlap, small_size // 2))
        for window, _ in windows:
            result.append(
                _make_chunk(
                    document,
                    len(result) + 1,
                    window,
                    offset=_locate(document, window),
                    title_path=parent.title_path,
                    strategy="small_to_big",
                    extras={
                        "parent_chunk_id": parent.chunk_id,
                        "parent_text": parent.text,
                    },
                )
            )
    return result


__all__ = [
    "DEFAULT_SEPARATORS",
    "Chunk",
    "Document",
    "estimate_tokens",
    "fixed_size",
    "lexical_similarity",
    "lexical_tokens",
    "markdown_heading",
    "page_for_offset",
    "recursive",
    "semantic",
    "small_to_big",
    "token_units",
]
