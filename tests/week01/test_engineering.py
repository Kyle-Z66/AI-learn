"""
第 1 周单元测试 · 动作 2：工程规范示范
"""
from __future__ import annotations

from week01.engineering.engineering_demo import typed_add


def test_typed_add() -> None:
    assert typed_add(1, 2) == 3
