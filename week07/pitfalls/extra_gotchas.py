"""
第 7 周 · 补足要点：chunk 好坏的判据与调参顺序
================================================================
【对应知识点】文档第 7 周："什么样的 chunk 是好 chunk"与面试要点

【周次学习要点】
  - 好 chunk 的三条判据：语义完整、带上下文前缀、长度适配 reranker 输入限制。
  - overlap 是保险不是越多越好：它按块数线性放大索引体积与重复度。
  - "先修检索，再修生成"：rerank 调得再花，召回集合里没有答案也白搭。

【易忽略细节】
  1. 标题前缀的收益几乎零成本，却常被团队忽略，直接去调 rerank 是顺序错了。
  2. 表格行与条款编号是语义原子，切分时必须整块保留。
  3. chunk 好坏没有通用数值标准，必须在自己的语料上做人工 10 样本抽检。

【示例用途】可运行：`python -m week07.pitfalls.extra_gotchas`
             测试见 tests/week07/test_pitfalls.py
"""
from __future__ import annotations

GOOD_CHUNK_CRITERIA: tuple[tuple[str, str], ...] = (
    ("语义完整", "条款、表格行、专有名词不被切断"),
    ("上下文前缀", "标题路径拼进 chunk，独立可检索"),
    ("长度适配", "不超过 reranker 的输入 token 上限"),
)

DEBUG_ORDER: tuple[str, ...] = (
    "解析保真",
    "切分策略",
    "召回率",
    "重排",
    "Prompt",
    "生成",
)


def overlap_cost(chunk_size: int, overlap: int, chunk_count: int) -> int:
    """估算 overlap 带来的额外 token 总量（每块重复一次重叠部分）。"""
    if chunk_count <= 1:
        return 0
    return overlap * (chunk_count - 1)


def demo_chunk_criteria() -> None:
    for name, description in GOOD_CHUNK_CRITERIA:
        print(f"{name}：{description}")


def demo_overlap_cost() -> None:
    for overlap in (0, 64, 128):
        extra = overlap_cost(512, overlap, 20)
        print(f"chunk_size=512 overlap={overlap:>3} → 20 块多存 {extra:>5} token")


def demo_debug_order() -> None:
    print("调参顺序：" + " → ".join(DEBUG_ORDER))
    print("直接从 rerank 开始调，等于假设召回已经完美，通常并不成立。")


def demo() -> None:
    demo_chunk_criteria()
    demo_overlap_cost()
    demo_debug_order()


if __name__ == "__main__":
    demo()
