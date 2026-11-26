"""
第 7 周 · 核心机制 01：RAG 九环节的输入输出再确认
================================================================
【对应知识点】文档第 7 周：RAG 全景，画出每一环的输入输出

【周次学习要点】
  - 沿用第 6 周 10_rag_preview 的九环节名称，这里只补"具体输入输出长什么样"。
  - 本周聚焦前两环（解析、切分），后七环在第 8~12 周逐步实装。
  - "检索质量决定答案质量上限"：上游丢的信息，后面任何生成技巧都补不回来。

【易忽略细节】
  1. 引用环节的输入必须带 source/page，否则第 7 周解析时就要把溯源字段留住。
  2. 嵌入的输入是 chunk 文本而非原始文件，所以切分错误会直接传导到向量。
  3. 从第 6 周预习到第 7 周实装，唯一变化是"名词 → 数据结构"，不是重新造概念。

【示例用途】可运行：`python -m week07.core_mechanisms.01_rag_pipeline`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

import importlib

# 数字前缀模块不能用普通 import 语法，动态导入沿用第 6 周测试的写法。
RAG_STAGES = importlib.import_module(
    "week06.core_mechanisms.10_rag_preview"
).RAG_STAGES

PIPELINE_IO: tuple[tuple[str, str, str], ...] = (
    ("解析", "incident.pdf", "Document(text, sections, page)"),
    ("切分", "Document.text", "list[Chunk(title_path, page)]"),
    ("嵌入", "Chunk.text", "list[float] 向量"),
    ("索引", "向量 + 元数据", "可检索的向量库"),
    ("检索", "query 向量 + where", "Top-K 候选 Chunk"),
    ("重排", "候选 + query", "少量高相关 Chunk"),
    ("组装", "Chunks + Prompt 模板", "带上下文的 Prompt"),
    ("生成", "Prompt", "答案草稿"),
    ("引用", "答案 + source/page", "可溯源答复"),
)


def stage_summary(index: int) -> str:
    """返回指定环节的一句话输入输出描述。"""
    if not 0 <= index < len(PIPELINE_IO):
        raise IndexError("环节下标越界")
    name, source, target = PIPELINE_IO[index]
    return f"{name}：{source} → {target}"


def demo() -> None:
    print("环节 | 输入示例                     | 输出示例")
    for name, source, target in PIPELINE_IO:
        print(f"{name:<4} | {source:<26} | {target}")
    print(f"\n共 {len(RAG_STAGES)} 个环节；第 7 周实装前两环，后七环按周推进。")
    print(stage_summary(0))


if __name__ == "__main__":
    demo()
