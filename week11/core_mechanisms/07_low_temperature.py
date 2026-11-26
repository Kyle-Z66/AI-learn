"""
第 11 周 · 核心机制 07：低温度 + 结构化输出（复用第 2 周，不重复讲原理）
================================================================
【对应知识点】文档第 11 周幻觉抑制③：低温度（0~0.2）+ 结构化输出

【周次学习要点】
  - 生成侧统一用 0.1：降低采样随机性，让同类问题的答案形态稳定。
  - 低温度只压分布，不改变模型"知不知道"：证据不足时照样会自信地编。
  - 因此低温度必须和结构化输出、守卫组合起来，才构成完整可靠性方案。

【易忽略细节】
  1. temperature 缩放 logits 的原理见第 2 周 03_sampling_params.py，
     这里直接 importlib 复用该函数，只讲工程用法，不重复公式。
  2. 第 2 周 09_non_determinism.py 已说明 temperature=0 也不保证 100% 复现；
     所以结果仍要 schema 校验 + 重试兜底，不能"设 0 就完事"。
  3. FakeGenerator 把 temperature 记录在 GeneratedAnswer 里，便于实验对比。

【示例用途】可运行：`python -m week11.core_mechanisms.07_low_temperature`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

import importlib
from typing import Any

from week11.engineering.generator import DEFAULT_TEMPERATURE

LOGITS = [2.0, 1.0, 0.1]


def demo() -> None:
    # 动态 import 是因为文件名以数字开头，不能用普通点号写法。
    module: Any = importlib.import_module("week02.api_fundamentals.03_sampling_params")
    for temperature in (DEFAULT_TEMPERATURE, 1.0):
        probs = module.softmax_with_temperature(LOGITS, temperature)
        print(f"temperature={temperature:<4} → 首候选概率={probs[0]:.3f}")
    print("结论：低温度让输出更集中，但不提供事实证据；必须叠加守卫与 schema 校验。")


if __name__ == "__main__":
    demo()
