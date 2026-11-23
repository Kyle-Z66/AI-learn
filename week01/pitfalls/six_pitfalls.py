"""
第 1 周 · 6 个 Python 特有"坑"（文档原文全部覆盖，并补足描述不足之处）
================================================================
【对应知识点】文档第 1 周「必须掌握的 6 个 Python 特有坑」

【周次学习要点】
  文档列出 6 个坑：① 可变默认参数 ② None 用 is 检查 ③ 缩进即语法
  ④ 鸭子类型 ⑤ 列表推导式 ⑥ 字符串 += 性能陷阱。
  本文件对每坑都给出"错误写法 vs 正确写法"的可运行对照。

【易忽略细节 / 对文档的补足】
  - 坑 1：文档给的 `items = items or []` 有语义缺陷 —— 调用者传入空列表 [] 时，
    `[]` 为假值，会被替换成新列表，导致调用者持有的列表不会被修改。
    正确写法是 `if items is None: items = []`（只在真正省略参数时新建）。
  - 坑 2：补足 `is`（对象身份）vs `==`（值相等）的原理，以及小整数缓存陷阱。
  - 坑 3：补足具体异常类型 IndentationError / TabError 与"统一 4 空格"的工程约定。
  - 坑 4：补足与 Protocol（07_protocol.py）的联动 —— 鸭子类型是运行时，Protocol 是静态契约。
  - 坑 5：补足与生成器表达式的内存差异、以及"嵌套过深时别硬用推导式"。
  - 坑 6：补足 str.join() 的正确写法与"字符串不可变 → 每次 += 都新建对象"的原理。

【示例用途】可运行：`python week01/pitfalls/six_pitfalls.py`
"""
from __future__ import annotations

import time
from typing import Any


# ---------------------------------------------------------------- 坑 1
def bad_mutable_default(item: int, items: list[int] = []) -> list[int]:  # noqa: B006
    """❌ 错误：默认列表在函数定义时创建一次，所有调用共享同一个对象。"""
    items.append(item)
    return items


def good_mutable_default(item: int, items: list[int] | None = None) -> list[int]:
    """✅ 正确：默认值用 None，在函数体内按需新建。"""
    if items is None:
        items = []
    items.append(item)
    return items


def legacy_or_trick(item: int, items: list[int] | None = None) -> list[int]:
    """文档原写法 items = items or []：能防共享，但传入 [] 时会被替换。"""
    items = items or []
    items.append(item)
    return items


def pitfall_1() -> None:
    print("  [坑1 可变默认参数]")
    print(f"    ❌ 连续调用共享同一列表：{bad_mutable_default(1)}, {bad_mutable_default(2)}")
    print(f"    ✅ 每次调用独立       ：{good_mutable_default(1)}, {good_mutable_default(2)}")
    caller_list: list[int] = []
    legacy_or_trick(1, caller_list)
    print(f"    文档 or 写法传入 [] 后：caller_list={caller_list} —— 仍是空的！调用者列表未被修改")
    caller_list = []
    good_mutable_default(1, caller_list)
    print(f"    is None 写法传入 [] 后：caller_list={caller_list} —— 正确修改了传入对象")


# ---------------------------------------------------------------- 坑 2
def pitfall_2() -> None:
    print("  [坑2 None 检查用 is]")
    value: str | None = None
    print(f"    ❌ value == None : {value == None}  # noqa: E711 能跑但不规范")  # noqa: E711
    print(f"    ✅ value is None : {value is None}")
    print("    原理：is 比较两个对象的身份(id)，== 调用 __eq__ 比较值；")
    print("    None 是单例，用 is 更快更安全")
    a, b = 1000, 1000
    print(f"    小整数缓存陷阱：a is b = {a is b}（CPython 会缓存小整数，别依赖 is 比较数字）")


# ---------------------------------------------------------------- 坑 3
def pitfall_3() -> None:
    print("  [坑3 缩进即语法]")
    bad_code = "def f():\nprint('缩进错了')\n"
    try:
        exec(bad_code)
    except IndentationError as e:
        print(f"    ❌ 缩进错误抛出：{type(e).__name__}: {e}")
    print("    ✅ 统一用 4 个空格缩进（不要混用 Tab，否则抛 TabError）；IDE 里开启 show whitespace")


# ---------------------------------------------------------------- 坑 4
class Duck:
    def quack(self) -> str:
        return "嘎嘎"


class RobotDuck:
    def quack(self) -> str:
        return "电子嘎嘎"


def make_quack(duck: Any) -> str:
    """运行时只看对象有没有 quack 方法 —— 鸭子类型。静态检查请用 07_protocol.py 的 Protocol。"""
    return duck.quack()


def pitfall_4() -> None:
    print("  [坑4 鸭子类型]")
    print(f"    真鸭子   : {make_quack(Duck())}")
    print(f"    机器鸭子 : {make_quack(RobotDuck())} —— 不需要共同父类，传对方法就行")
    print("    Java 要显式 implements；Python 靠方法名匹配（运行时）+ Protocol（静态）")


# ---------------------------------------------------------------- 坑 5
def pitfall_5() -> None:
    print("  [坑5 列表推导式]")
    items = [1, -2, 3, -4, 5]
    result = [x * x for x in items if x > 0]
    print(f"    ✅ Pythonic 写法：[x*x for x in items if x>0] = {result}")
    print("    等价 for 循环要 3 行且多次 append；推导式更短且通常更快")
    print("    补足：生成器表达式 (x for x in items) 惰性求值省内存（见 04_generators.py）")
    print("    补足：嵌套超过 2 层时别硬塞推导式，可读性优先")


# ---------------------------------------------------------------- 坑 6
def pitfall_6() -> None:
    print("  [坑6 字符串 += 性能陷阱]")
    n = 20_000
    start = time.perf_counter()
    s = ""
    for i in range(n):
        s += str(i)
    plus_cost = time.perf_counter() - start

    start = time.perf_counter()
    s2 = "".join(str(i) for i in range(n))
    join_cost = time.perf_counter() - start

    print(f"    循环 += 耗时  : {plus_cost:.4f}s —— 字符串不可变，每次 += 都新建对象")
    print(f"    ''.join() 耗时: {join_cost:.4f}s —— 一次分配，快约 {plus_cost / join_cost:.1f} 倍")
    print(f"    结果一致：{s == s2}")


def main() -> None:
    print("=== 第 1 周：6 个 Python 特有坑 ===")
    pitfall_1()
    pitfall_2()
    pitfall_3()
    pitfall_4()
    pitfall_5()
    pitfall_6()


if __name__ == "__main__":
    main()
