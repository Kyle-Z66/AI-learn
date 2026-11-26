"""
第 10 周 · 核心机制 01：Bi-encoder vs Cross-encoder
================================================================
【对应知识点】文档第 10 周：首阶段双塔快，二阶段联合编码准

【周次学习要点】
  - bi-encoder 把 query 和 doc 分开编码成向量，可离线建库、ANN 快查。
  - cross-encoder 把 (query, doc) 拼在一起过模型，能看细粒度交互但无法离线建库。
  - 正确链路：bi 召回 Top-50 → cross 精排 Top-5；不能让 cross 遍历全库。

【易忽略细节】
  1. "精度高"的代价是每条候选都要单独过一次模型，延迟与候选数线性相关。
  2. 第 9 周混合检索属于首阶段；第 10 周是在它之上加二阶段，不是替换。
  3. 教学版用确定性函数模拟联合打分，真实模型选型（bge-reranker / Cohere）不展开。

【示例用途】可运行：`python -m week10.core_mechanisms.01_bi_vs_cross`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

STAGE_COMPARISON: list[tuple[str, str, str, str]] = [
    ("bi-encoder", "query / doc 分开编码", "可预计算、ANN 快查", "召回 Top-50"),
    ("cross-encoder", "(query, doc) 联合编码", "逐条推理、精度高", "精排 Top-5"),
]


def stage_comparison() -> list[tuple[str, str, str, str]]:
    """返回两阶段对照表，供日志与测试复用。"""
    return [(name, encoding, feature, duty) for name, encoding, feature, duty in STAGE_COMPARISON]


def demo() -> None:
    print(f"{'阶段':<15}{'编码方式':<22}{'特点':<22}{'职责'}")
    for name, encoding, feature, duty in stage_comparison():
        print(f"{name:<15}{encoding:<22}{feature:<22}{duty}")
    print("链路：混合检索召回 50 条 → cross-encoder 逐条打分 → 取前 5 条")


if __name__ == "__main__":
    demo()
