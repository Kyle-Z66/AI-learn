"""
第 1 周 · 语言差异点 08：__slots__
================================================================
【对应知识点】文档第 1 周「语言差异点」第 8 项：__slots__

【周次学习要点】
  - 默认情况下，每个 Python 实例都有一个 __dict__ 字典存属性，查询快但占内存。
  - 定义 __slots__ = ("x", "y") 后，实例不再有 __dict__，属性存在紧凑的固定槽位里，
    大量创建对象时（如百万级数据行）能显著省内存。
  - dataclass(slots=True)（Python 3.10+）是声明式写法，见 02_dataclass.py。

【易忽略细节】
  1. 定义 __slots__ 后**不能动态添加新属性**（除了 __slots__ 里声明的）—— 与 Java 对象固定字段类似。
  2. 子类若不想重新获得 __dict__，必须也声明 __slots__（可写 __slots__ = ()）。
  3. 不要为了几个对象盲目加 slots：可读性 / 动态性损失可能大于收益；它主要服务大批量对象。
  4. mypy 对动态添加的属性会报 attr-defined，需用 `# type: ignore[attr-defined]` 标注。

【示例用途】可运行：`python week01/language_features/08_slots.py`
"""
from __future__ import annotations

from dataclasses import dataclass


class PointWithDict:
    """普通类：每个实例都有 __dict__，可动态添加属性。"""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class PointWithSlots:
    """slots 类：无 __dict__，只能存 x / y 两个槽位。"""

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass(slots=True)
class PointDataclassSlots:
    """现代写法：dataclass(slots=True) 自动生成带 slots 的数据类。"""

    x: int
    y: int


def create_many(cls: type, n: int) -> list[object]:
    """批量创建对象，用于观察内存差异。"""
    return [cls(i, i) for i in range(n)]


def main() -> None:
    print("=== 08 __slots__ ===")
    a = PointWithDict(1, 2)
    b = PointWithSlots(1, 2)
    c = PointDataclassSlots(1, 2)

    print(f"  普通类有 __dict__      : {hasattr(a, '__dict__')}")
    print(f"  slots 类有 __dict__    : {hasattr(b, '__dict__')}")
    print(f"  dataclass(slots) 有dic : {hasattr(c, '__dict__')}")

    # 普通类可以动态加属性（mypy 静态检查会拦截，需用 ignore 标注这是故意的）
    a.tag = "dynamic"  # type: ignore[attr-defined]
    print(f"  普通类动态加属性       : {a.tag}")  # type: ignore[attr-defined]
    try:
        b.tag = "dynamic"  # type: ignore[attr-defined]
    except AttributeError as e:
        print(f"  slots 类动态加属性失败 : {type(e).__name__}（符合预期）")

    many_dict = create_many(PointWithDict, 100_000)
    many_slots = create_many(PointWithSlots, 100_000)
    dict_mb = many_dict[0].__sizeof__() * len(many_dict) / 1024 / 1024
    slots_mb = many_slots[0].__sizeof__() * len(many_slots) / 1024 / 1024
    print(f"  10 万个对象占用(近似)   : dict 版 {dict_mb:.1f} MB / slots 版 {slots_mb:.1f} MB")
    print("  说明：真实节省还包括每个实例省掉的 __dict__ 字典本身，此处仅作量级示意")


if __name__ == "__main__":
    main()
