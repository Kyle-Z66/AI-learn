"""
第 9 周 · 核心机制 07：查询扩写救专名召回
================================================================
【对应知识点】文档第 9 周：专有名词（型号/错误码/缩写）的混合召回

【周次学习要点】
  - 对型号/错误码/缩写补同义说法，可以同时提升 BM25 与向量两路的命中率。
  - 扩写是"加词"不是"改写意图"：原词必须保留，否则专名本身丢了。
  - 规则表是确定性教学实现；生产可换成术语词典或 LLM 改写（第 11 周再讲生成）。

【易忽略细节】
  1. 扩写词要进同一 tokenizer 能识别的形态，别把 SGCC-4012 写成"sgcc4012"。
  2. 已经出现过的扩写词不要重复追加，否则 query 越长 IDF 越失真。
  3. 扩写后两路都要重跑；只改其中一路等于没改。

【示例用途】可运行：`python -m week09.core_mechanisms.07_query_rewrite`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

# 教学术语表：key 是原始写法，value 是可追加的同义说法。
TERM_EXPANSIONS: dict[str, str] = {
    "sgcc-4012": "国网型号 4012 断路器",
    "err_4012": "错误码 4012 通信超时",
    "api": "接口",
}


def rewrite_query(query: str) -> str:
    """按术语表追加同义说法，保留原词且不重复追加。"""
    lowered = query.lower()
    extras = [
        expansion
        for term, expansion in TERM_EXPANSIONS.items()
        if term in lowered and expansion not in query
    ]
    return f"{query} {' '.join(extras)}".strip()


def demo() -> None:
    for query in (
        "SGCC-4012 怎么处理",
        "ERR_4012 排查",
        "API 调用失败",
        "断路器巡检周期",
    ):
        print(f"原查询：{query}")
        print(f"扩写后：{rewrite_query(query)}")
    print("扩写后再跑双路召回：专名字面命中 + 语义近邻同时增强")


if __name__ == "__main__":
    demo()
