"""
第 1 周单元测试 · 6 个坑 + 补足的遗漏项
"""
from __future__ import annotations

import importlib
from typing import Any, cast

pitfalls = cast(Any, importlib.import_module("week01.pitfalls.six_pitfalls"))
extra = cast(Any, importlib.import_module("week01.pitfalls.extra_gotchas"))


def test_mutable_default_pitfall() -> None:
    # 错误写法：共享同一个默认列表
    first = pitfalls.bad_mutable_default(1)
    second = pitfalls.bad_mutable_default(2)
    assert first is second
    assert first == [1, 2]

    # 正确写法：每次独立
    assert pitfalls.good_mutable_default(1) == [1]
    assert pitfalls.good_mutable_default(2) == [2]

    # 文档 or 写法的缺陷：传入空列表时不会修改调用者对象
    caller: list[int] = []
    pitfalls.legacy_or_trick(1, caller)
    assert caller == []  # 缺陷复现

    caller = []
    pitfalls.good_mutable_default(1, caller)
    assert caller == [1]  # 正确写法修改了传入对象


def test_is_none_and_late_binding() -> None:
    assert pitfalls.make_quack(pitfalls.Duck()) == "嘎嘎"
    assert pitfalls.make_quack(pitfalls.RobotDuck()) == "电子嘎嘎"

    assert extra.late_binding_bad() == [2, 2, 2]  # late-binding 陷阱复现
    assert extra.late_binding_good() == [0, 1, 2]  # 默认参数绑定修复


def test_shallow_vs_deep_copy() -> None:
    original = [[1, 2], [3, 4]]
    shallow = original.copy()
    shallow[0].append(99)
    assert original == [[1, 2, 99], [3, 4]]  # 浅拷贝共享内层引用
