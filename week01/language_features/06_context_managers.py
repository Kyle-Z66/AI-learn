"""
第 1 周 · 语言差异点 06：上下文管理器
================================================================
【对应知识点】文档第 1 周「语言差异点」第 6 项：上下文管理器

【周次学习要点】
  - with 语句等价于 Java 的 try-with-resources：进入时获取资源，离开时自动释放。
  - 两种实现方式：① 类的 __enter__ / __exit__ 协议；② contextlib.contextmanager 装饰器。
  - __exit__ 返回 True 会抑制（吞掉）异常，返回 False 则异常继续抛出。

【易忽略细节】
  1. 即使 with 代码块抛异常，__exit__ / finally 仍会执行 —— 这是"自动释放"的价值。
  2. 用 @contextmanager 时必须用 try/finally 包住 yield，否则异常时清理逻辑不会执行。
  3. 一个 with 可以同时管理多个资源（逗号分隔），或用 ExitStack 动态管理不定数量资源。
  4. mypy 要求"总是返回 False"的 __exit__ 标注为 Literal[False]，而不是宽泛的 bool。

【示例用途】可运行：`python week01/language_features/06_context_managers.py`
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Literal


class ManagedResource:
    """方式一：实现 __enter__ / __exit__ 协议（对应 Java AutoCloseable）。"""

    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> ManagedResource:
        print(f"    [enter] 打开资源 {self.name}")
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Literal[False]:
        exc_name = exc_type.__name__ if exc_type else None
        print(f"    [exit] 关闭资源 {self.name}（异常类型：{exc_name}）")
        return False  # 不抑制异常


@contextmanager
def managed(name: str) -> Iterator[str]:
    """方式二：@contextmanager 把生成器包装成上下文管理器，更轻量。"""
    print(f"    [enter] 打开资源 {name}")
    try:
        yield name
    finally:
        # 必须 try/finally：代码块抛异常时才会走到这里执行清理
        print(f"    [exit] 关闭资源 {name}")


@contextmanager
def swallow_value_error() -> Iterator[None]:
    """演示异常抑制：吞掉 ValueError（谨慎使用，生产代码别乱吞异常）。"""
    try:
        yield
    except ValueError:
        print("    [suppress] ValueError 被 __exit__ 吞掉了")


def main() -> None:
    print("=== 06 上下文管理器 ===")
    print("  [类实现] 正常流程：")
    with ManagedResource("DB连接") as res:
        print(f"    使用 {res.name} 中...")

    print("  [类实现] 异常流程（注意 exit 仍执行）：")
    try:
        with ManagedResource("文件句柄"):
            raise RuntimeError("模拟业务异常")
    except RuntimeError as e:
        print(f"    捕获异常：{e}")

    print("  [@contextmanager]：")
    with managed("HTTP连接") as name:
        print(f"    使用 {name} 中...")

    print("  [异常抑制]：")
    with swallow_value_error():
        raise ValueError("这个异常会被吞掉")
    print("    程序继续运行，未崩溃")


if __name__ == "__main__":
    main()
