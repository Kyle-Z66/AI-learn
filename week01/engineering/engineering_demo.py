"""
第 1 周 · 动作 2：工程规范的可运行示范
================================================================
【对应知识点】文档第 1 周「工程规范」：pyproject.toml / 虚拟环境 / ruff+mypy / pytest / uv

【周次学习要点】
  - 模块（.py 文件）与包（含 __init__.py 的目录）对应 Java 的 package；
    跨包引用用**绝对导入** `from week01.xxx import ...`，包内相对导入用 `from . import ...`。
  - `if __name__ == "__main__"` 让文件既能被 import（不执行演示），又能当脚本运行。
  - 完整类型注解 + mypy 静态检查，是"工程级 Python"与"脚本级 Python"的分界线。

【易忽略细节】
  1. 本文件用绝对导入，因此**必须从仓库根目录**以模块方式运行：
     `python -m week01.engineering.engineering_demo`（或 uv run -m ...）。
     若直接 `python week01/engineering/engineering_demo.py`，sys.path[0] 会变成该子目录，
     导致找不到 week01 包 —— 这是 Java 程序员转 Python 最常见的导入痛点。
  2. ruff 的 I 规则会自动排序 import；B/UP/SIM 规则会把"能跑但不规范"的写法揪出来。
  3. pytest 只收集 test_*.py； asyncio_mode=auto 让 async 测试无需手写装饰器。

【示例用途】可运行：`python -m week01.engineering.engineering_demo`
"""
from __future__ import annotations

import sys
from pathlib import Path

# 绝对导入：从项目根包 week01 出发。对应 Java 的 import com.xxx.yyy.Zzz。
from week01.pitfalls.extra_gotchas import late_binding_good


def typed_add(a: int, b: int) -> int:
    """带完整类型注解的函数：mypy 能在运行前检查出传参类型错误。"""
    return a + b


def main() -> None:
    print("=== 动作 2：工程规范示范 ===")
    print(f"  当前模块 __name__     : {__name__}")
    print(f"  Python 版本           : {sys.version.split()[0]}")
    print(f"  项目根目录（推导）    : {Path(__file__).resolve().parents[2]}")
    print(f"  绝对导入调用结果      : {late_binding_good()}")
    print(f"  类型注解函数          : typed_add(1, 2) = {typed_add(1, 2)}")
    print("  运行三件套：ruff check . / mypy / pytest（配置均在 pyproject.toml）")


if __name__ == "__main__":
    main()
