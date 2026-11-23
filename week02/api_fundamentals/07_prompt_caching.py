"""
第 2 周 · 模型 API 原理 07：cache prompt（提示词缓存）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 7 项：cache prompt

【周次学习要点】
  - Prompt Caching：把长且不变的 system prompt / 文档片段缓存起来，重复请求时只传增量部分。
  - 命中条件是**前缀完全匹配**：从第一个 token 开始逐字一致，任何改动都会让后续缓存失效。
  - 命中后：首 token 延迟下降、成本降低（缓存部分通常按折扣计费）。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足最关键的一点：**动态内容必须放末尾**。
     如果把时间戳/用户 ID 放在 system prompt 开头，缓存永远不命中。
  2. 缓存有最小长度要求（各厂商不同，通常几百 token），短 prompt 不必惦记。
  3. 不同模型/不同厂商的缓存机制不通用，切换供应商要重新验证。
  4. 缓存命中率需要观测，不能假设它一定生效。

【示例用途】可运行：`python week02/api_fundamentals/07_prompt_caching.py`
"""
from __future__ import annotations


def split_cached_prefix(
    full_prompt: str, dynamic_marker: str = "{{USER_INPUT}}"
) -> tuple[str, str]:
    """把完整 prompt 拆成"可缓存静态前缀"和"动态尾部"。

    关键：动态内容必须在末尾，才能保证前缀稳定命中缓存。
    """
    if dynamic_marker not in full_prompt:
        return full_prompt, ""
    prefix, suffix = full_prompt.split(dynamic_marker, maxsplit=1)
    return prefix, suffix


def cache_key(prefix: str) -> str:
    """用前缀生成缓存键的示意（真实 API 由服务端管理，这里仅演示"前缀决定键"）。"""
    import hashlib

    return hashlib.sha256(prefix.encode("utf-8")).hexdigest()[:12]


def main() -> None:
    print("=== 02 模型 API 原理 07：prompt caching ===")
    template = (
        "你是一名资深技术文档分析助手，熟悉分布式系统与可观测性领域。\n"
        "请从用户输入中抽取系统名称、严重级别、受影响用户数，只输出 JSON。\n"
        "字段规则：system_name 为字符串；severity 为 1-5 的整数；affected_users 为非负整数。\n"
        "{{USER_INPUT}}"
    )
    prefix, suffix = split_cached_prefix(template)
    print(f"  静态前缀长度 : {len(prefix)} 字符 → cache_key={cache_key(prefix)}")
    print(f"  动态尾部     : {suffix!r}")

    bad_template = "{{TIMESTAMP}}" + template
    bad_prefix, _ = split_cached_prefix(bad_template)
    print(f"  错误示范：动态时间戳放开头 → 前缀 key={cache_key(bad_prefix)}（每次都变，永不命中）")
    print("  结论：长 system prompt 固定不变 + 用户输入放最后，才是可缓存的结构")


if __name__ == "__main__":
    main()
