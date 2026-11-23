"""
第 1 周 · 语言差异点 02：dataclass
================================================================
【对应知识点】文档第 1 周「语言差异点」第 3 项：dataclass

【周次学习要点】
  - dataclass 自动生成的 __init__ / __repr__ / __eq__ 等方法，等价于 Java 的 Lombok @Data。
  - field(default_factory=...) 是处理可变默认值（坑 #1）的标准手段。
  - 常用开关：frozen=True（不可变）、order=True（可排序）、slots=True（省内存，见 08_slots.py）。

【易忽略细节】
  1. 不能写 `tags: list[str] = []`：Python 3.11+ 的 dataclass 会直接抛 ValueError，
     比普通函数的可变默认参数（坑 #1）更严格。
  2. frozen=True 的对象不可改属性，但内部的可变容器仍可变（浅冻结）。
  3. asdict() 是深拷贝转换，astuple() 同理；大量调用有性能成本。

【示例用途】可运行：`python week01/language_features/02_dataclass.py`
"""
from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field, replace


@dataclass
class User:
    """普通数据类：对应 Java 的 POJO / Lombok @Data。"""

    name: str
    age: int = 0
    # 正确做法：用 default_factory 为每个实例创建独立的空列表。
    # 错误做法：tags: list[str] = []  →  dataclass 直接抛 ValueError。
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True, order=True, slots=True)
class Point:
    """frozen=不可变（类似 Java record）；order=支持 < > 比较；slots=无 __dict__ 省内存。"""

    x: int
    y: int


def demo_mutable_default() -> None:
    """证明每个 User 实例拥有独立的 tags 列表，不会互相污染。"""
    u1 = User("Kyle")
    u2 = User("Alice")
    u1.tags.append("vip")
    print(f"  u1.tags={u1.tags}, u2.tags={u2.tags} —— 互不共享（坑 #1 的正确写法）")


def main() -> None:
    print("=== 02 dataclass ===")
    u = User("Kyle", 32, ["java", "python"])
    print(f"  自动 repr     : {u}")
    print(f"  自动 eq       : {u == User('Kyle', 32, ['java', 'python'])}")
    print(f"  asdict        : {asdict(u)}")
    print(f"  astuple       : {astuple(u)}")
    print(f"  replace(改名) : {replace(u, name='Kyle.Z')}")
    demo_mutable_default()

    p1, p2 = Point(1, 2), Point(1, 3)
    print(f"  order 排序    : {p1 < p2}")
    print(f"  frozen 不可变 : {p1}（修改 p1.x 会抛 FrozenInstanceError）")


if __name__ == "__main__":
    main()
