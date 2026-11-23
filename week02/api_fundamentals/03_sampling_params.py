"""
第 2 周 · 模型 API 原理 03：temperature / top_p / max_tokens
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 3 项：temperature/top_p/max_tokens

【周次学习要点】
  - temperature 缩放 logits：越低概率分布越尖锐（确定），越高越平坦（随机）。
  - top_p（nucleus sampling）只保留累积概率达到 p 的最小候选集，再重新归一化。
  - max_tokens 限制**输出**长度；输出达到上限时 `finish_reason="length"`，内容可能被截断。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足两个参数同时生效的实际效果：先 temperature 缩放，再 top_p 截断。
  2. 抽取类任务设 temperature=0 只是"尽量确定"，仍可能因浮点/批处理差异波动，故需重试兜底。
  3. max_tokens 截断**不会抛异常**，必须检查 finish_reason —— 这是生产环境最常见的隐性 bug。
  4. top_p 与 temperature 一般只调一个；同时调会让行为难以预测。

【示例用途】可运行：`python week02/api_fundamentals/03_sampling_params.py`
"""
from __future__ import annotations

import math


def softmax_with_temperature(logits: list[float], temperature: float) -> list[float]:
    """按 temperature 缩放 logits 后做 softmax；temperature<=0 时退化为贪婪取最大值。"""
    if temperature <= 0:
        max_index = logits.index(max(logits))
        return [1.0 if i == max_index else 0.0 for i in range(len(logits))]
    scaled = [x / temperature for x in logits]
    max_scaled = max(scaled)
    exps = [math.exp(x - max_scaled) for x in scaled]  # 减最大值防数值溢出
    total = sum(exps)
    return [e / total for e in exps]


def top_p_filter(probs: list[float], top_p: float) -> list[float]:
    """nucleus sampling：保留累积概率达到 top_p 的最小候选集，再重新归一化。"""
    order = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    cumulative = 0.0
    kept: set[int] = set()
    for i in order:
        cumulative += probs[i]
        kept.add(i)
        if cumulative >= top_p:
            break
    filtered = [probs[i] if i in kept else 0.0 for i in range(len(probs))]
    total = sum(filtered)
    return [p / total for p in filtered]


def check_finish_reason(finish_reason: str, max_tokens: int) -> str:
    """演示如何识别输出被 max_tokens 截断（真实响应里 finish_reason 在 choice 中）。"""
    if finish_reason == "length":
        return f"警告：输出达到 max_tokens={max_tokens} 被截断，需增大上限或分段输出"
    if finish_reason == "stop":
        return "正常结束"
    return f"其他结束原因：{finish_reason}"


def main() -> None:
    print("=== 02 模型 API 原理 03：采样参数 ===")
    logits = [2.0, 1.0, 0.1, 0.0]

    for temp in (0.0, 0.5, 1.5):
        probs = softmax_with_temperature(logits, temp)
        print(f"  temperature={temp:<4}: {[round(p, 3) for p in probs]}")

    probs = softmax_with_temperature(logits, 1.0)
    filtered = top_p_filter(probs, top_p=0.8)
    print(f"  top_p=0.8 过滤后 : {[round(p, 3) for p in filtered]}（小概率候选被归零）")
    print("  实践建议：抽取/分类只调 temperature；creative 写作再考虑 top_p，别同时调两个")

    for reason in ("stop", "length", "tool_calls"):
        print(f"  finish_reason={reason:<10} → {check_finish_reason(reason, max_tokens=200)}")


if __name__ == "__main__":
    main()
