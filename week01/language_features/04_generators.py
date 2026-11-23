"""
第 1 周 · 语言差异点 04：生成器
================================================================
【对应知识点】文档第 1 周「语言差异点」第 4 项：生成器

【周次学习要点】
  - 生成器用 yield 暂停/恢复函数，按需产出值 → 惰性求值，内存占用 O(1)。
  - 生成器表达式 (x for x in ...) 与列表推导式 [x for x in ...] 语法相似，
    但前者返回一个迭代器，不会一次性把全部结果放进内存。
  - yield from 把子生成器的每个值透传出来，适合扁平化嵌套结构。

【易忽略细节】
  1. 生成器**只能消费一次**：遍历完后就耗尽，再遍历得到空（列表可以反复遍历）。
  2. 生成器函数在调用时不会执行任何代码，直到第一次 next()/遍历才运行函数体。
  3. big Data 场景优先生成器；需要随机访问/复用结果时才转成 list。

【示例用途】可运行：`python week01/language_features/04_generators.py`
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator


def fib(n: int) -> Iterator[int]:
    """产出前 n 个斐波那契数。"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def flatten(groups: Iterable[Iterable[int]]) -> Iterator[int]:
    """yield from 扁平化：等价于嵌套循环 yield。"""
    for group in groups:
        yield from group


def main() -> None:
    print("=== 04 生成器 ===")
    print(f"  生成器函数 fib(6)      : {list(fib(6))}")
    print(f"  yield from 扁平化      : {list(flatten([[1, 2], [3], [4, 5]]))}")

    gen = (x * x for x in range(3))
    print(f"  生成器表达式第一次消费 : {list(gen)}")
    print(f"  第二次消费（已耗尽）   : {list(gen)} —— 生成器只能消费一次")

    list_comp = [x * x for x in range(3)]
    print(f"  列表推导式可反复消费   : {list_comp}, {list_comp}")
    print("  内存差异：列表推导式一次性分配全部结果；生成器表达式每次只算一个")

    # next() 手动推进，观察 yield 的暂停/恢复语义
    g = fib(3)
    print(f"  next(g) 逐次          : {next(g)}, {next(g)}, {next(g)}")


if __name__ == "__main__":
    main()
