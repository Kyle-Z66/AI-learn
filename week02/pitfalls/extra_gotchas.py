"""
第 2 周 · 对照文档补足的遗漏点（严格限定第 2 周范畴）
================================================================
【对应知识点】文档第 2 周未展开、但工程实践中高频的 4 个细节：

  A. 浮点非确定性：temperature=0 仍非绝对确定（与 09_non_determinism.py 呼应）。
  B. SSE 跨包/粘包：一帧可能跨多个 TCP 包，也可能一包含多帧。
  C. prompt cache 前缀被动态内容破坏：时间戳放开头 → 永不命中。
  D. 降级不记录成本：账单对不上，无法归因到具体模型。

【周次学习要点】
  - 这些都不是"语法坑"，而是"把 LLM 当可靠系统组件"时必须建立的工程直觉。
  - 与第 1 周 pitfalls/extra_gotchas.py 同名同定位：补足文档一笔带过的内容。

【易忽略细节】
  - 4 个补足点都能在本周其它样例里找到对应实现，这里只做认知层对照。

【示例用途】可运行：`python -m week02.pitfalls.extra_gotchas`
             （动态加载包内模块，须从仓库根以 -m 运行）
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, cast

# 数字前缀脚本只能用 importlib 动态加载（同第 1 周测试文件的做法）
_cache = cast(Any, importlib.import_module("week02.api_fundamentals.07_prompt_caching"))
_nd = cast(Any, importlib.import_module("week02.api_fundamentals.09_non_determinism"))
cache_key = _cache.cache_key
split_cached_prefix = _cache.split_cached_prefix
sample_outputs = _nd.sample_outputs


@dataclass(frozen=True)
class UsageRecord:
    """降级链上的一次调用记录：实际模型 + 估算 token，用于成本对账。"""

    model: str
    input_tokens: int
    output_tokens: int


def demo_float_nondeterminism() -> None:
    outputs = sample_outputs("同一 prompt", n=30, temperature=0.0, seed=7)
    print(f"    temperature=0 跑 30 次 → 出现 {len(set(outputs))} 种结果（浮点/批处理差异）")
    print("    应对：把输出当候选，用 schema 校验决定接受或重试")


def demo_sse_chunking() -> None:
    raw = 'data: {"a":1}\n\ndata: {"a":2}\n\ndata: [DONE]\n\n'
    # 真实网络可能把这段拆成任意多个 TCP 包；客户端应维护缓冲区按 \n\n 分帧
    chunks = [raw[:12], raw[12:30], raw[30:]]
    buffer = ""
    frames: list[str] = []
    for chunk in chunks:
        buffer += chunk
        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", maxsplit=1)
            frames.append(frame.strip())
    print(f"    模拟 3 个不完整 TCP 包 → 正确还原 {len(frames)} 帧：{frames[:2]}...")


def demo_cache_prefix() -> None:
    good = "固定 system 指令很长……{{USER_INPUT}}"
    bad = "{{TIMESTAMP}}" + good
    good_key = cache_key(split_cached_prefix(good)[0])
    bad_key = cache_key(split_cached_prefix(bad)[0])
    print(f"    稳定前缀 key：{good_key}")
    print(f"    时间戳放开头 key：{bad_key}（每次不同 → 缓存永不命中）")


def demo_fallback_cost() -> None:
    records = [UsageRecord("deepseek-chat", 900, 200), UsageRecord("qwen-plus", 900, 200)]
    print(f"    降级调用记录：{[(r.model, r.input_tokens + r.output_tokens) for r in records]}")
    print("    必须记录实际命中的模型，否则无法解释成本突增")


def main() -> None:
    print("=== 第 2 周：文档未展开的补足点 ===")
    print("  [A. 浮点非确定性]")
    demo_float_nondeterminism()
    print("  [B. SSE 跨包/粘包]")
    demo_sse_chunking()
    print("  [C. prompt cache 前缀]")
    demo_cache_prefix()
    print("  [D. 降级成本记录]")
    demo_fallback_cost()


if __name__ == "__main__":
    main()
