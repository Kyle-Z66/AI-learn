"""
第 1 周 · 语言差异点 01：类型注解（Type Hints）
================================================================
【对应知识点】文档第 1 周「语言差异点」第 1 项：类型注解 Optional[str] / list[str]

【周次学习要点】
  - Java 是静态强类型，类型在编译期强制；Python 注解只是"给阅读者和工具看的标签"，
    运行时不强制。这是 Java 程序员最大的认知误区。
  - Python 3.12+ 现代写法：用 `X | None` 代替 `Optional[X]`，用 `list[str]` 代替 `List[str]`。
  - mypy 才是让注解产生约束力的工具（配置见根目录 pyproject.toml 的 [tool.mypy]）。

【易忽略细节】
  1. 注解在函数定义时求值（除非 from __future__ import annotations）；引用未定义的类需加引号。
  2. 注解不是普通表达式，`list[str]` 里的 str 是类型而非值。
  3. `type` 语句（3.12+）/ `Callable` / PEP 695 泛型是写工程级代码的基础工具。

【示例用途】可运行：`python week01/language_features/01_type_annotations.py`
             测试见 tests/week01/test_language_features.py
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

# 类型别名：Python 3.12 的 `type` 语句（对应 Java 的 typedef 思路）。
# 旧写法是 `UserId: TypeAlias = int`，ruff 的 UP 规则会推动升级。
type UserId = int
type Headers = dict[str, str]


def normalize_username(name: str | None) -> str:
    """现代写法：`str | None` 表达"可能是 None 的字符串"。"""
    return name.strip() if name is not None else "anonymous"


# 教学对比：文档原文写的 Optional[str] 是旧写法（Python 3.10 之前的主流）。
# ruff 的 UP 规则会主动建议改成 str | None，这里用 noqa 保留以作对照。
def normalize_username_legacy(name: Optional[str]) -> str:  # noqa: UP007, UP045
    return name.strip() if name is not None else "anonymous"


def make_list(value: int, count: int) -> list[int]:
    """注解声明"只接受 int"，但运行时并不阻止传入 str —— 见下面的演示。"""
    return [value] * count


def apply_transform(value: int, fn: Callable[[int], int]) -> int:
    """Callable[[参数类型], 返回类型]：把函数当作参数传递时的注解写法。"""
    return fn(value)


class Box[T]:
    """泛型容器：对应 Java 的 Box<T>。

    Python 3.12 用 PEP 695 的 `class Box[T]`；旧写法是 `class Box(Generic[T])`
    配合 TypeVar("T") —— ruff 的 UP 规则会推动升级到新写法。
    """

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


def describe(value: Any) -> str:
    """Any 表示放弃类型检查，等效于 Java 的 Object —— 工程代码里应尽量避免滥用。"""
    return f"{type(value).__name__}: {value!s}"


def demo_annotations_not_enforced() -> None:
    """关键演示：注解不强制类型，只有 mypy 这类静态检查器才会报错。"""
    # mypy 会报 arg-type；这里忽略以演示"运行时仍照常执行"
    got = make_list("x", 3)  # type: ignore[arg-type]
    print(f"  运行时传入 str 也执行了：{got}（注解不强制；mypy 报 arg-type）")


def main() -> None:
    print("=== 01 类型注解 ===")
    print(f"  现代写法 str | None : {normalize_username('  Kyle  ')} / {normalize_username(None)}")
    print(f"  旧写法 Optional[str]: {normalize_username_legacy('  Kyle  ')}")
    print(f"  泛型容器 Box[int]   : {Box[int](42).get()}")
    print(f"  Callable 作为参数   : {apply_transform(5, lambda x: x * x)}")
    headers: Headers = {"X-Token": "abc"}
    print(f"  类型别名 Headers    : {headers}")
    print(f"  Any 描述            : {describe([1, 2])}")
    demo_annotations_not_enforced()


if __name__ == "__main__":
    main()
