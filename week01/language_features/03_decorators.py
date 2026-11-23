"""
第 1 周 · 语言差异点 03：装饰器
================================================================
【对应知识点】文档第 1 周「语言差异点」第 2 项：装饰器

【周次学习要点】
  - 装饰器本质是高阶函数：接收函数、返回新函数，用 @语法糖套在被装饰函数上。
  - functools.wraps 保留原函数的 __name__ / __doc__，是工程级装饰器的必备写法。
  - 带参装饰器是"返回装饰器的工厂"，多一层闭包。

【易忽略细节】
  1. 不用 wraps 会让被装饰函数的名字变成 wrapper，破坏日志、依赖注入、FastAPI 路由签名
     （FastAPI 在第 6 周会用到，这里先把习惯立好）。
  2. 多个装饰器叠加时，离函数最近的先执行包装：@A @B def f 等价于 A(B(f))。
  3. 装饰器在模块导入（函数定义）时就运行，不是每次调用时运行。
  4. Python 3.12 的 PEP 695 允许 `def timer[T](...)` 直接声明类型参数，
     等价于旧写法 `T = TypeVar("T")` + `def timer(func: Callable[..., T])`。

【示例用途】可运行：`python week01/language_features/03_decorators.py`
"""
from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, cast


def timer[T](func: Callable[..., T]) -> Callable[..., T]:
    """计时装饰器：保留原函数签名元信息（wraps）。"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        cost_ms = (time.perf_counter() - start) * 1000
        print(f"    [timer] {func.__name__} 耗时 {cost_ms:.2f} ms")
        return result

    return wrapper


def repeat[T](n: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """带参装饰器工厂：调用 repeat(2) 返回一个真正的装饰器。"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result: T | None = None
            for _ in range(n):
                result = func(*args, **kwargs)
            # 若 n=0 result 仍为 None，这里用 cast 告知 mypy（教学：泛型返回的边界情况）
            return cast(T, result)

        return wrapper

    return decorator


@timer
@repeat(2)
def greet(name: str) -> str:
    """被装饰的业务函数。"""
    return f"hello, {name}"


def main() -> None:
    print("=== 03 装饰器 ===")
    print(f"  调用结果      : {greet('Kyle')}")
    print(f"  wraps 保留名字: {greet.__name__}（没有 wraps 会显示 wrapper）")
    print(f"  wraps 保留文档: {greet.__doc__}")
    print("  叠加顺序：@timer @repeat(2) → timer(repeat(2)(greet))，先 repeat 再 timer")


if __name__ == "__main__":
    main()
