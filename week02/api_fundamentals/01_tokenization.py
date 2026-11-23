"""
第 2 周 · 模型 API 原理 01：tokenization（分词）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 1 项：tokenization

【周次学习要点】
  - 大模型不按"字符"读文本，而是按 token（子词单元）读。token 是模型的最小处理单位。
  - 主流分词算法是 BPE（Byte-Pair Encoding）：从字符开始，反复把最高频的相邻对合并成新词元。
  - token 数直接决定：① 是否超出上下文窗口 ② API 计费 ③ 输出长度上限。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足 BPE 的合并过程演示 —— 理解为什么 "unhappy" 可能拆成 un + happy。
  2. 中文 token 与字符不是 1:1：常见词可能 1 个 token，生僻字可能 2~3 个 token。
  3. 计费按 token 计，不按字符；"这个字多少钱"没有意义，要看 tokenizer 的实际切分。
  4. 不同模型的 tokenizer 不同，token 数不能跨模型直接套用。

【示例用途】可运行：`python week02/api_fundamentals/01_tokenization.py`
             测试见 tests/week02/test_api_fundamentals.py
"""
from __future__ import annotations


def bpe_merge_once(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    """模拟 BPE 的一次合并：把序列中所有相邻的 pair 合并成一个新 token。

    真实 tokenizer 会按频率选 pair 并迭代多轮；这里手动指定 pair，专注理解机制。
    """
    merged = pair[0] + pair[1]
    result: list[str] = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
            result.append(merged)
            i += 2
        else:
            result.append(tokens[i])
            i += 1
    return result


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（仅用于理解量级，生产请用对应模型的 tokenizer）。

    经验值：英文约 4 字符/token；中文约 1~2 字符/token，这里按 1.5 折算。
    """
    chinese = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    other = len(text) - chinese
    return other // 4 + int(chinese / 1.5) + 1


def estimate_cost(
    input_tokens: int, output_tokens: int, price_in: float, price_out: float
) -> float:
    """按每千 token 单价估算一次调用成本（单位：元）。

    价格不硬编码在代码里：由调用方传入，避免厂商调价后代码过时。
    """
    return input_tokens / 1000 * price_in + output_tokens / 1000 * price_out


def main() -> None:
    print("=== 02 模型 API 原理 01：tokenization ===")

    raw = list("unhappy")
    step1 = bpe_merge_once(raw, ("u", "n"))
    step2 = bpe_merge_once(step1, ("un", "h"))
    print(f"  原始字符切分     : {raw}")
    print(f"  BPE 合并 ('u','n'): {step1}")
    print(f"  BPE 再合并        : {step2} —— 高频组合逐步变成一个新 token")

    samples = ["hello world", "大模型应用开发", "你好，世界！"]
    for text in samples:
        print(f"  估算 token：{text!r} → 约 {estimate_tokens(text)} 个（{len(text)} 字符）")

    cost = estimate_cost(1200, 300, price_in=0.004, price_out=0.012)
    print(f"  成本示例：输入 1200 + 输出 300 token，按传入单价 → ¥{cost:.4f}")
    print("  注意：price_in/price_out 只是占位参数，真实价格请以厂商官网为准")


if __name__ == "__main__":
    main()
