"""
第 4 周 · 核心机制 02：过期时间预留安全边界
================================================================
【对应知识点】文档第 4 周 Token 缓存：过期时间预留安全边界（Java 侧 expireIn - 1000）

【周次学习要点】
  - 通用公式：有效 TTL = 官方过期时间 - 安全余量。
  - 你 Java 侧的 `expireIn - 1000` 就是这个思想，数字不同、原理完全一致。
  - 余量太小：请求正好撞上过期；余量太大：频繁刷新，浪费认证服务配额。

【易忽略细节】
  1. 余量不能大于官方有效期：否则 TTL 会被压到 0，代码用 max(1.0, ...) 兜底。
  2. 安全余量应大于"刷新 token 的网络耗时 + 时钟误差"，生产环境通常几十秒。
  3. 短有效期凭证尤其要注意：30 秒的 token 留 60 秒余量会退化成每次都刷新。

【示例用途】可运行：`python -m week04.core_mechanisms.02_safety_margin`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

from week04.engineering.token_cache import MemoryBackend, TokenCache


def demo() -> None:
    cache = TokenCache(MemoryBackend(), safety_margin=60)
    print(f"{'官方有效期':<12}{'无余量':<12}{'留 60 秒余量'}")
    for expires_in in (3600, 300, 90, 30):
        no_margin = max(1.0, expires_in - 0)
        with_margin = cache.effective_ttl(expires_in)
        print(f"{expires_in:<12}{no_margin:<12}{with_margin}")

    print("\n结论：短凭证要按比例设余量，否则每次请求都会触发刷新。")


if __name__ == "__main__":
    demo()
