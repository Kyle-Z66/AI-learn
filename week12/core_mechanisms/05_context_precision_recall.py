"""
第 12 周 · 核心机制 05：Context Precision 与 Context Recall
================================================================
【对应知识点】文档第 12 周：Context Precision / Context Recall

【周次学习要点】
  - Precision 看送进模型的证据"纯不纯"：Top-K 中相关片段占比。
  - Recall 看证据"全不全"：标注相关片段被检索到的比例（与 Recall@K 同义但不限 k）。
  - 两者常常此消彼长：扩大 Top-K 提 Recall、降 Precision，也会推高成本。

【易忽略细节】
  1. Precision 的分母是 k，Recall 的分母是标注数——面试最容易混的一对公式。
  2. Top-K 为空时 Precision 返回 0；没有上下文却给高分是最危险的评测 bug。
  3. Java 里常用 Map<String, Double> 传指标；这里用明确函数名与返回 float，
     调用方少一次 key 拼错的机会。

【示例用途】可运行：`python -m week12.core_mechanisms.05_context_precision_recall`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.metrics import context_precision, context_recall

RETRIEVED = ["a", "x", "b", "y", "z"]
RELEVANT = ["a", "b", "c"]


def demo() -> None:
    for k in (1, 3, 5):
        precision = context_precision(RETRIEVED, RELEVANT, k)
        recall = context_recall(RETRIEVED[:k], RELEVANT)
        print(f"k={k}: Precision={precision:.3f} Recall={recall:.3f}")
    print("Precision 分母=Top-K 长度；Recall 分母=标注片段数（此处为 3）。")


if __name__ == "__main__":
    demo()
