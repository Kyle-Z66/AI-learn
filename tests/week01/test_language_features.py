"""
第 1 周单元测试 · 动作 1：10 个语言差异点
================================================================
用 importlib 动态导入数字前缀的样例脚本（Python 的 import 语句不支持数字开头的模块名，
但 importlib.import_module 可以），cast(Any, ...) 告诉 mypy 这是动态加载。
"""
from __future__ import annotations

import importlib
from typing import Any, cast

# 动态加载 10 个样例模块
m01 = cast(Any, importlib.import_module("week01.language_features.01_type_annotations"))
m02 = cast(Any, importlib.import_module("week01.language_features.02_dataclass"))
m03 = cast(Any, importlib.import_module("week01.language_features.03_decorators"))
m04 = cast(Any, importlib.import_module("week01.language_features.04_generators"))
m05 = cast(Any, importlib.import_module("week01.language_features.05_asyncio_await"))
m06 = cast(Any, importlib.import_module("week01.language_features.06_context_managers"))
m07 = cast(Any, importlib.import_module("week01.language_features.07_protocol"))
m08 = cast(Any, importlib.import_module("week01.language_features.08_slots"))
m09 = cast(Any, importlib.import_module("week01.language_features.09_fstring"))
m10 = cast(Any, importlib.import_module("week01.language_features.10_slicing"))


# 01 类型注解
def test_normalize_username() -> None:
    assert m01.normalize_username("  Kyle  ") == "Kyle"
    assert m01.normalize_username(None) == "anonymous"
    assert m01.normalize_username_legacy(None) == "anonymous"


def test_generic_and_callable() -> None:
    assert m01.Box[int](42).get() == 42
    assert m01.apply_transform(5, lambda x: x * x) == 25
    assert m01.make_list("x", 3) == ["x", "x", "x"]


# 02 dataclass
def test_dataclass_default_factory() -> None:
    u1, u2 = m02.User("Kyle"), m02.User("Alice")
    u1.tags.append("vip")
    assert u1.tags == ["vip"]
    assert u2.tags == []  # 每个实例独立，不共享


def test_dataclass_frozen_order() -> None:
    assert m02.Point(1, 2) < m02.Point(1, 3)
    assert m02.Point(1, 2) == m02.Point(1, 2)


# 03 装饰器
def test_decorator_preserves_metadata() -> None:
    assert m03.greet("Kyle") == "hello, Kyle"
    assert m03.greet.__name__ == "greet"  # functools.wraps 生效


# 04 生成器
def test_generators() -> None:
    assert list(m04.fib(5)) == [0, 1, 1, 2, 3]
    assert list(m04.flatten([[1, 2], [3], [4]])) == [1, 2, 3, 4]
    gen = (x for x in range(2))
    assert list(gen) == [0, 1]
    assert list(gen) == []  # 生成器一次性


# 05 asyncio（auto 模式下 async 测试无需装饰器）
async def test_asyncio_concurrency() -> None:
    assert await m05.run_sequential() == ["resp-0", "resp-1", "resp-2", "resp-3"]
    assert await m05.run_with_gather() == ["resp-0", "resp-1", "resp-2", "resp-3"]
    assert await m05.run_with_task_group() == ["resp-0", "resp-1", "resp-2", "resp-3"]
    assert await m05.run_with_to_thread() == [0, 1, 4, 9]


# 06 上下文管理器
def test_context_manager() -> None:
    with m06.managed("test") as name:
        assert name == "test"
    with m06.swallow_value_error():
        raise ValueError("should be swallowed")


# 07 Protocol
def test_protocol_and_eafp() -> None:
    email = m07.EmailNotifier()
    assert isinstance(email, m07.Notifier)  # runtime_checkable
    assert m07.notify(email, "msg") is True
    assert m07.parse_int_eafp("123") == 123
    assert m07.parse_int_eafp("abc") is None
    assert m07.parse_int_lbyl("-5") == -5


# 08 slots
def test_slots() -> None:
    obj = m08.PointWithSlots(1, 2)
    assert not hasattr(obj, "__dict__")
    assert obj.x == 1
    assert m08.PointDataclassSlots(3, 4).y == 4


# 09 f-string / 10 切片：验证样例能正常执行且不抛异常
def test_fstring_and_slicing(capsys: Any) -> None:
    m09.main()
    m10.main()
    out = capsys.readouterr().out
    assert "12,345.68" in out  # f-string 千分位格式
    assert "[2, 4, 6]" in out  # 切片步长
