"""
第 12 周 · 工程层：评测数据模型（golden case / 逐案分数 / 配置结果）
================================================================
【对应知识点】文档第 12 周：每条标注"标准答案 + 相关文档片段 ID"；四配置对比表

【周次学习要点】
  - GoldenCase 是评测的最小资产：问题、参考答案、相关片段 ID、标注元数据缺一不可。
  - EvalScores 是一组可比较的标量；ConfigResult 额外保留逐案 recall 用于看分布。
  - 数据模型用 frozen dataclass：一次评测产出的结果不应被后续配置悄悄改写。

【易忽略细节】
  1. metadata 用 dict[str, str] 保存"来源 / 标注规则 / 难度"，
     面试被问"评测集怎么来的"时能直接给出证据，而不是临场编。
  2. p95_latency_ms 由真实计时聚合，不是拍脑袋填的示意值（报告里必须注明本地测量）。
  3. Java 里常用嵌套 DTO + BeanUtils 拷贝；这里 from_dict/to_dict 显式转换，
     字段增删时编译期（mypy）与测试都能发现，不靠反射猜测。

【示例用途】被 golden_set.py / metrics.py / runner.py / report.py / ci_gate.py 引用；
             测试见 tests/week12/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True, slots=True)
class GoldenCase:
    """一条标注样本：question / answer / relevant_chunk_ids / metadata。"""

    question: str
    answer: str
    relevant_chunk_ids: tuple[str, ...]
    metadata: dict[str, str]

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> GoldenCase:
        """从 JSON 对象构造；显式 cast 让类型检查器校验字段形状。"""
        ids = cast(list[object], raw["relevant_chunk_ids"])
        meta = cast(dict[str, object], raw["metadata"])
        return cls(
            question=str(raw["question"]),
            answer=str(raw["answer"]),
            relevant_chunk_ids=tuple(str(item) for item in ids),
            metadata={str(key): str(value) for key, value in meta.items()},
        )

    def to_dict(self) -> dict[str, object]:
        """回写为 JSON 可序列化结构，便于导出/扩充评测集。"""
        return {
            "question": self.question,
            "answer": self.answer,
            "relevant_chunk_ids": list(self.relevant_chunk_ids),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class CaseEvaluation:
    """单条样本在某配置下的指标与真实耗时，供聚合与分布分析。"""

    recall_at_k: float
    context_precision: float
    context_recall: float
    faithfulness: float
    answer_relevance: float
    latency_ms: float
    retrieved_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvalScores:
    """一个配置的汇总分数；字段与报告表列一一对应。"""

    recall_at_k: float
    mrr: float
    context_precision: float
    context_recall: float
    faithfulness: float
    answer_relevance: float
    p95_latency_ms: float


@dataclass(frozen=True, slots=True)
class ConfigResult:
    """四配置之一的结果：汇总分数 + 逐案 recall（看分布）+ 样本数。"""

    config: str
    scores: EvalScores
    per_case_recall: tuple[float, ...]
    case_count: int
