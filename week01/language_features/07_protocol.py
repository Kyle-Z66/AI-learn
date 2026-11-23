"""
第 1 周 · 语言差异点 07：Protocol（对应 Java 接口）
================================================================
【对应知识点】文档第 1 周「语言差异点」第 7 项：Protocol（对应 Java 接口）

【周次学习要点】
  - Protocol 是 Python 的"结构化子类型"（structural typing）：只要方法有相同的名字和签名，
    就视为实现了接口，**无需显式继承**。Java 的 implements 是"名义子类型"（nominal typing）。
  - @runtime_checkable 让 isinstance() 在运行时检查"是否存在对应方法"。
  - Protocol 与坑 #4「鸭子类型」是同一件事的两种表达：鸭子类型是运行时的潜规则，
    Protocol 把它变成静态类型检查器（mypy）也能理解的显式契约。

【易忽略细节】
  1. @runtime_checkable 的 isinstance 只检查方法名是否存在，**不检查签名/返回类型**。
  2. 非 runtime_checkable 的 Protocol 不能用于 isinstance，只能给 mypy 看。
  3. Python 惯用 EAFP（先做再捕获异常）而非 Java 常见的 LBYL（先检查再做），二者对比见下文。

【示例用途】可运行：`python week01/language_features/07_protocol.py`
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    """通知接口：任何拥有 send(str) -> bool 方法的类都自动满足。"""

    def send(self, message: str) -> bool: ...


class EmailNotifier:
    """注意：没有继承 Notifier —— 这就是结构化子类型与 Java 的根本差异。"""

    def send(self, message: str) -> bool:
        print(f"    [Email] 发送：{message}")
        return True


class SmsNotifier:
    def send(self, message: str) -> bool:
        print(f"    [SMS] 发送：{message}")
        return True


def notify(notifier: Notifier, message: str) -> bool:
    """参数类型是 Protocol：mypy 静态检查通过即可，运行时靠鸭子类型工作。"""
    return notifier.send(message)


def parse_int_lbyl(value: str) -> int | None:
    """LBYL（Look Before You Leap）：先检查再操作 —— Java 程序员习惯的写法。"""
    if value.lstrip("-").isdigit():
        return int(value)
    return None


def parse_int_eafp(value: str) -> int | None:
    """EAFP（Easier to Ask Forgiveness than Permission）：先操作，失败再捕获 —— Pythonic 写法。"""
    try:
        return int(value)
    except ValueError:
        return None


def main() -> None:
    print("=== 07 Protocol ===")
    email, sms = EmailNotifier(), SmsNotifier()
    print(f"  isinstance(email, Notifier): {isinstance(email, Notifier)} —— 无需继承也成立")
    print(f"  notify(email)              : {notify(email, '系统告警')}")
    print(f"  notify(sms)                : {notify(sms, '系统告警')}")
    print("  对比 Java：这里没有 implements Notifier，靠方法签名自动匹配（鸭子类型）")

    print("  EAFP vs LBYL：")
    print(f"    LBYL '123'  → {parse_int_lbyl('123')}, 'abc' → {parse_int_lbyl('abc')}")
    print(f"    EAFP '123'  → {parse_int_eafp('123')}, 'abc' → {parse_int_eafp('abc')}")
    print("    Python 更推荐 EAFP：少一次检查、避免 TOCTOU 竞态、代码更短")


if __name__ == "__main__":
    main()
