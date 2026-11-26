"""
第 11 周 · 核心机制 02：上下文预算截断与 cited sources 同步
================================================================
【对应知识点】文档第 11 周上下文组装细节：max_tokens 预算耗尽就 break

【周次学习要点】
  - 预算控制的是"送进模型的证据量"，直接决定成本与答案可引用的范围。
  - 截断后 cited sources 必须只剩真正入选的片段，否则答案会引用不存在的证据。
  - truncated / omitted_count 让"证据被切掉"变成可观测事件，而不是静默事故。

【易忽略细节】
  1. 计划原文返回 (text, cited) 两个值；本工程把二者与 chunks 绑进 ContextBundle，
     因为调用的守卫与引用映射都需要同一份快照，拆开返回迟早会漂移。
  2. 估算 token 不等于真实 tokenizer：生产要按目标模型校准，估算偏小会被服务端截断。
  3. Java 里常把"预算检查"放进 for 循环外部；这里每轮都算一次并 break，
     顺序即优先级——最相关的片段必须排在前面。

【示例用途】可运行：`python -m week11.core_mechanisms.02_context_budget`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from week11.engineering.context import build_context, count_tokens
from week11.engineering.models import SourceChunk

CHUNKS: tuple[SourceChunk, ...] = (
    SourceChunk("DOC-A", "值班规范", 1, "系统 cyclone 级别为 2 级，影响 30 名用户。"),
    SourceChunk("DOC-A", "值班规范", 2, "负责人为张伟，备用联系人李娜。"),
    SourceChunk("DOC-B", "值班手册", 9, "值班热线 400-000-0000，入口在内网 portal。"),
)


def demo() -> None:
    for budget in (1000, 25):
        bundle = build_context(list(CHUNKS), max_tokens=budget)
        print(f"预算={budget}: 入选 {len(bundle.chunks)}/{len(CHUNKS)}，"
              f"截断={bundle.truncated}，省略={bundle.omitted_count}")
        print("  text =", bundle.text)
        print("  sources =", bundle.sources)
    print("单段 token 估算：", [count_tokens(chunk.content) for chunk in CHUNKS])
    print("结论：sources 只列入选片段；预算切掉证据时必须让守卫知道。")


if __name__ == "__main__":
    demo()
