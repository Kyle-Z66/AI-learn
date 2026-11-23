"""
第 1 周 · 对照文档补足的遗漏坑（严格限定在 Python 语法速成范畴）
================================================================
【对应知识点】文档第 1 周只列了 6 个坑，本文件补足两类 Java 程序员高频踩坑：

  A. 闭包 late-binding（循环变量捕获）—— 文档未列，但属于"语言差异点"范畴，
     与坑 #4 鸭子类型、装饰器（03_decorators.py）的闭包机制直接相关。
  B. 浅拷贝 vs 深拷贝 / 列表别名 —— 文档未列，但与坑 #1 可变默认参数、切片（10_slicing.py）
     同源：都是"共享引用"问题。

【周次学习要点】
  - Python 闭包捕获的是变量的**引用**而非定义时的值；循环结束后变量已是最终值。
  - list.copy() / 切片 [:] 都是浅拷贝：只复制最外层容器，内层对象仍共享。
  - copy.deepcopy() 递归复制所有层级；对不可变对象（int/str/tuple）浅深拷贝无差别。

【易忽略细节】
  1. 修复 late-binding 的最简写法：默认参数绑定 lambda i=i: i（ruff B023 会提示绑定循环变量）。
  2. 另一个修复是用 functools.partial（见 03_decorators.py 的闭包思想）。
  3. 深拷贝有性能成本且对含锁/文件句柄的对象可能失败，不要无脑用。

【示例用途】可运行：`python week01/pitfalls/extra_gotchas.py`
"""
from __future__ import annotations

import copy
from collections.abc import Callable


def late_binding_bad() -> list[int]:
    """❌ 错误：三个 lambda 都捕获同一个变量 i，循环结束后 i=2。"""
    funcs: list[Callable[[], int]] = []
    for i in range(3):
        funcs.append(lambda: i)  # noqa: B023 —— 故意保留错误写法作教学对照
    return [f() for f in funcs]


def late_binding_good() -> list[int]:
    """✅ 正确：用默认参数 i=i 在定义时把当前值绑定到闭包。"""
    funcs: list[Callable[[], int]] = []
    for i in range(3):
        # 用默认参数 i=i 把当前循环变量值绑定到局部作用域
        def make_fn(i: int = i) -> int:
            return i

        funcs.append(make_fn)
    return [f() for f in funcs]


def shallow_vs_deep() -> None:
    """对比浅拷贝与深拷贝对嵌套可变对象的影响。"""
    original = [[1, 2], [3, 4]]

    shallow = original.copy()  # 等价 original[:]
    shallow[0].append(99)
    print(f"    浅拷贝后 original = {original} —— 内层被改了（共享内层引用）")

    original = [[1, 2], [3, 4]]
    deep = copy.deepcopy(original)
    deep[0].append(99)
    print(f"    深拷贝后 original = {original} —— 原对象不受影响")


def main() -> None:
    print("=== 第 1 周：文档未展开的补足坑 ===")
    print("  [A. 闭包 late-binding]")
    print(f"    ❌ 错误写法输出：{late_binding_bad()} —— 全是最后一个值 2")
    print(f"    ✅ 默认参数绑定：{late_binding_good()} —— [0, 1, 2]")
    print("  [B. 浅拷贝 vs 深拷贝]")
    shallow_vs_deep()


if __name__ == "__main__":
    main()
