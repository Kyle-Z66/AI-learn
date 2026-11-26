"""
第 9 周 · 工程层：混合检索的候选项数据模型
================================================================
【对应知识点】文档第 9 周：BM25 + 向量双路召回，Top-50 候选输出

【周次学习要点】
  - 两路召回共用同一个 Candidate 结构，融合阶段只改分数与排名，不复制正文。
  - dept / valid 是元数据过滤字段，必须在进两路索引之前就生效。
  - bm25_score / dense_score 分开存，才能讲清"量纲不同不可直接相加"。

【易忽略细节 / 对照文档补足】
  1. 文档只写 Chunk，没区分首阶段分数与融合分数；这里拆成两路原始分 + fused_score。
  2. 用 dataclass 而不是 dict：Java 侧的 DTO 思维可以直接平移，字段类型一目了然。
  3. rank 初始为 None 表示"尚未融合"；误用 0 会把候选排到第一名。

【示例用途】被 week09/engineering/* 与 week09/hybrid_lab/* 引用；
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidate:
    """一条可检索的文本候选，两路召回与融合共用的最小单元。"""

    chunk_id: str
    text: str
    source: str
    dept: str = ""  # 部门/权限标签；空串表示不限
    valid: bool = True  # 有效期标记；False 表示已失效，过滤阶段剔除
    bm25_score: float | None = None  # 稀疏路原始分
    dense_score: float | None = None  # 稠密路原始分
    fused_score: float | None = None  # 融合后的分数
    rank: int | None = None  # 融合后排名，从 1 开始
    metadata: dict[str, str] = field(default_factory=dict)

    def copy_without_scores(self) -> Candidate:
        """复制条目但清空分数；避免把上一轮分数带进新一轮融合。"""
        return Candidate(
            chunk_id=self.chunk_id,
            text=self.text,
            source=self.source,
            dept=self.dept,
            valid=self.valid,
            metadata=dict(self.metadata),
        )


__all__ = ["Candidate"]
