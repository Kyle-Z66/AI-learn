"""
第 1 周 · 语言差异点 09：f-string 高级用法
================================================================
【对应知识点】文档第 1 周「语言差异点」第 9 项：f-string 高级用法

【周次学习要点】
  - f"{expr}" 在运行时求值并插入字符串；格式说明符写在冒号后：{value:格式}。
  - 常用格式：,.2f（千分位+2位小数）、>10（右对齐宽度）、04d（补零）、.1%（百分比）。
  - !r / !s 在格式化前先调用 repr() / str()；{var=}（3.8+）输出"变量名=值"，调试神器。

【易忽略细节】
  1. 格式说明符里的嵌套（如 {value:{width}.{precision}f}）在运行时求值，非常灵活。
  2. f-string 里的表达式不能包含反斜杠（Python 3.12 前）—— 先把值算好再放进 f-string。
  3. 日志场景优先用 logging 的 %s 惰性格式化，不要提前拼 f-string（避免无谓开销）。

【示例用途】可运行：`python week01/language_features/09_fstring.py`
"""
from __future__ import annotations


def main() -> None:
    print("=== 09 f-string 高级用法 ===")
    price = 12345.6789
    name = "Kyle"
    ratio = 0.1234

    print(f"  基础插值          : {name} 今年 32 岁")
    print(f"  千分位 + 2 位小数 : {price:,.2f}")
    print(f"  右对齐宽度 10     : |{name:>10}|")
    print(f"  左对齐宽度 10     : |{name:<10}|")
    print(f"  居中对齐宽度 10   : |{name:^10}|")
    print(f"  整数补零 4 位     : {7:04d}")
    print(f"  百分比 1 位小数   : {ratio:.1%}")
    print(f"  !r 调用 repr      : {name!r}")
    print(f"  调试 = 语法       : {name=}, {price=:,.1f}")

    width, precision = 12, 3
    print(f"  嵌套格式说明符    : |{price:{width}.{precision}f}|")
    print("  注意：3.12 前 f-string 表达式内不能有反斜杠，需先算好值再插入")


if __name__ == "__main__":
    main()
