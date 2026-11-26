"""
第 7 周 · 工程层：解析与切分的统一数据模型
================================================================
【对应知识点】文档第 7 周：解析输出与切分输出的契约

【周次学习要点】
  - 五种解析器都返回 Document，五种切分器都接收 Document 返回 list[Chunk]。
  - 统一契约使"换解析器"与"换切分策略"互不污染，便于做对照实验。
  - Chunk 带 title_path / page / source，是第 8 周标量过滤与第 10 周引用的基础。

【易忽略细节 / 对照文档补足】
  1. 文档只说"解析文件"，没说要保留页码与标题路径；这里显式留字段，避免后续无法溯源。
  2. Document.sections 存标题层级而非全文，Chunk 的 metadata 存策略等扩展信息。
  3. PAGE_SEPARATOR 用换页符 \\f 标记多页文档边界，切分器据此回推 chunk 页码。

【示例用途】被 parsers.py / chunkers.py / chunking_lab 引用；
             测试见 tests/week07/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

PAGE_SEPARATOR = "\f"


@dataclass
class Document:
    """解析器统一输出：纯文本 + 标题层级 + 页码信息。"""

    doc_id: str
    title: str
    path: str
    text: str
    sections: list[str] = field(default_factory=list)
    page: int = 1


@dataclass
class Chunk:
    """切分器统一输出：可检索的文本片段 + 溯源信息。"""

    chunk_id: str
    doc_id: str
    text: str
    title_path: str = ""
    page: int = 1
    source: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


__all__ = ["PAGE_SEPARATOR", "Chunk", "Document"]
