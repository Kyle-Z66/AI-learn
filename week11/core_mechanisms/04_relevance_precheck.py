"""
第 11 周 · 核心机制 04：检索相关性预检（不相关直接拒答）
================================================================
【对应知识点】文档第 11 周幻觉抑制①：上下文相关性预检

【周次学习要点】
  - 问题与上下文没有实词交集时，生成环节再强也只是"优雅地编"，应在调用前挡住。
  - 预检发生在生成之前：省掉一次模型调用，也省掉一轮无效的后校验。
  - 判断依据可解释：交集词集合能打印出来，便于排查是检索错还是问题本身超范围。

【易忽略细节】
  1. 中文不能用 split() 分词；content_terms() 用单字 + 二元组并过滤停用词。
     预检只算长度>=2 的词：单字会在"预算"与"成本计算"间制造假相关，
     让本该拒答的问题被放行。
  2. min_overlap=1 是宽松起点；业务上可调高，但调太高会把同义改写误杀，
     需要配合第 12 周的 golden set 验证阈值。
  3. Java 里常用 if/throw 提前返回；这里返回 GuardResult 值对象，
     调用方统一处理，不会漏掉"被拒答"分支的指标记录。

【示例用途】可运行：`python -m week11.core_mechanisms.04_relevance_precheck`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from week11.engineering.context import build_context
from week11.engineering.guards import content_terms, relevance_precheck
from week11.engineering.models import SourceChunk

CHUNK = SourceChunk(
    "DOC-A", "值班规范", 1, "系统 cyclone 级别为 2 级，影响 30 名用户。"
)


def demo() -> None:
    bundle = build_context([CHUNK])
    for question in ("系统 cyclone 级别是多少？", "公司火星基地的预算是多少？"):
        result = relevance_precheck(question, bundle)
        overlap = {
            term for term in content_terms(question) & content_terms(bundle.text)
            if len(term) >= 2
        }
        print(f"问题：{question}")
        print(f"  交集实词（长度>=2）={sorted(overlap)}")
        print(f"  预检通过={result.passed} 原因={result.reason}")


if __name__ == "__main__":
    demo()
