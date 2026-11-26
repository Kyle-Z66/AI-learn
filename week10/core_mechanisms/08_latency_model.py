"""
第 10 周 · 核心机制 08：rerank 延迟模型（教学假设）
================================================================
【对应知识点】文档第 10 周：50 个 ~310ms，100 个 ~590ms

【周次学习要点】
  - 文档给的两个点可拟合成线性模型：latency ≈ 5.6 × n + 30 (ms)。
  - 这是教学假设，用于建立"候选数 × 延迟"的数量级直觉，不是 SLA 承诺。
  - 交互式预算 50 个对应 ~310ms；批处理 100+ 才会接受 ~590ms 以上。

【易忽略细节】
  1. 真实延迟还受模型大小、GPU/CPU、batch 策略影响，须实测校准。
  2. 线性外推到 1000 个会失真，超出实验区间不要随口引用。
  3. 延迟增长是线性的，而边际收益递减 → 候选预算需要上限。

【示例用途】可运行：`python -m week10.core_mechanisms.08_latency_model`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

# (候选数, 文档给出的经验延迟毫秒)；仅作教学示意。
BUDGET_TABLE: tuple[tuple[int, float], ...] = ((50, 310.0), (100, 590.0))


def estimate_latency_ms(candidates: int) -> float:
    """线性示意：通过 (50,310) 与 (100,590)，截距 30ms。"""
    if candidates < 0:
        raise ValueError("候选数不能为负")
    return 5.6 * candidates + 30.0


def demo() -> None:
    print("教学假设：latency ≈ 5.6 × n + 30 (ms)，非生产 SLA")
    for count, documented in BUDGET_TABLE:
        estimated = estimate_latency_ms(count)
        print(f"  {count:>3} 个候选：文档 ~{documented:.0f}ms，模型 {estimated:.0f}ms")
    print(f"  30 个候选（交互保守值）：{estimate_latency_ms(30):.0f}ms")


if __name__ == "__main__":
    demo()
