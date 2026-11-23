"""
第 2 周 · 模型 API 原理 09：非确定性（文档目标核心，正文未单列，本工程补足）
================================================================
【对应知识点】文档第 2 周学习目标："理解 LLM 的非确定性"。
              文档未列独立任务，本工程补足为第 9 个知识点。

【周次学习要点】
  - 同样的输入、同样的参数，LLM 的输出仍可能不同 —— 这是本周最重要的认知。
  - 来源：采样随机性（temperature/top_p）、浮点运算顺序、批处理调度、模型版本更新等。
  - 工程应对：temperature=0 降低随机性 + schema 校验兜底 + 失败重试 + 多版本 Prompt 对比实验。

【易忽略细节 / 对照文档补足】
  1. `temperature=0` 通常取 argmax，但底层浮点差异仍可能导致极小概率翻转，**不保证 100% 复现**。
  2. 不要用"跑一次结果对"来验证 Prompt，要在同一批样本上多次运行看稳定性（本周 Prompt 实验的意义）。
  3. 生产系统要把 LLM 当作"会犯错的组件"：校验、重试、降级、可观测性缺一不可。
  4. 模型供应商静默升级也会改变输出；对确定性要求高的场景要固定模型版本。

【示例用途】可运行：`python week02/api_fundamentals/09_non_determinism.py`
"""
from __future__ import annotations

import random
from collections import Counter


def sample_outputs(prompt: str, n: int, temperature: float, seed: int = 42) -> list[str]:
    """模拟同一 Prompt 多次调用的结果（用随机数演示非确定性，可设 seed 复现实验）。

    temperature 越高，候选分布越平坦 —— 用抽样权重粗略模拟这一效果。
    """
    rng = random.Random(seed)
    candidates = ["系统A|3|100", "系统A|4|100", "系统A|三|100", "系统 A，级别 3，影响 100 人"]
    weights = [8.0, 1.0, 0.5, 0.5] if temperature == 0 else [4.0, 3.0, 2.0, 2.0]
    return rng.choices(candidates, weights=weights, k=n)


def consistency_report(outputs: list[str]) -> tuple[str, float]:
    """统计最常见输出及其占比，作为"稳定性"的粗略度量。"""
    counts = Counter(outputs)
    most_common, hits = counts.most_common(1)[0]
    return most_common, hits / len(outputs)


def main() -> None:
    print("=== 02 模型 API 原理 09：非确定性 ===")
    prompt = "从技术文档中抽取系统名、严重级别、受影响用户数"

    for temp in (0.0, 0.8):
        outputs = sample_outputs(prompt, n=20, temperature=temp)
        common, ratio = consistency_report(outputs)
        print(f"  temperature={temp:<4} → 最常见结果出现率 {ratio:.0%}，样例：{common}")
        print(f"    20 次调用产生了 {len(set(outputs))} 种不同结果")

    print("  结论：即使 temperature=0，也不能假设输出恒定。")
    print("  应对：Pydantic schema 校验 + 错误回灌重试（见 structured_output/）")
    print("       + 多版本 Prompt 对比（见 prompt_lab/）")


if __name__ == "__main__":
    main()
