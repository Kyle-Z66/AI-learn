"""
第 12 周 · 核心机制 07：Answer Relevance（答案是否回答问题）
================================================================
【对应知识点】文档第 12 周：生成侧 Answer Relevance 指标

【周次学习要点】
  - 教学版用"问题实词被答案覆盖的比例"近似相关性，无需向量模型。
  - 拒答答案覆盖率天然低：这提示"拒答率与相关性要分开看"，不能只看一个总分。
  - 与 Faithfulness 正交：忠实但答非所问、相关但编造，是两类不同失败。

【易忽略细节】
  1. 停用词已在第 11 周 content_terms 中过滤；不过滤会让"的/多少"把分数抬高。
  2. 同义改写无法识别（"级别"vs"严重度"），所以真实项目要换语义相似度模型。
  3. 分母是问题实词数而非答案长度：答案再长，没覆盖问题关键词也拿不到分。

【示例用途】可运行：`python -m week12.core_mechanisms.07_answer_relevance`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.metrics import answer_relevance

QUESTION = "系统 cyclone 影响多少名用户？"


def demo() -> None:
    answers = (
        "系统 cyclone 影响 30 名用户。",
        "系统 cyclone 的负责人为张伟。",
        "信息不足，无法基于给定上下文回答。",
    )
    for answer in answers:
        print(f"{answer_relevance(QUESTION, answer):.3f} ← {answer}")
    print("拒答得分低是预期现象：用拒答率单独衡量，别把它混进质量均值。")


if __name__ == "__main__":
    demo()
