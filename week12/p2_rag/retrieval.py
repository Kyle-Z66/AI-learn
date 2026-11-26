"""
第 12 周 · P2 项目：本地确定性检索（四配置共用的语料与排序）
================================================================
【对应知识点】文档第 12 周：BM25-only / dense-only / hybrid / hybrid+rerank 四配置

【周次学习要点】
  - 语料 = 20 个知识点片段 + 4 个干扰片段；干扰片段模拟真实知识库的噪声。
  - BM25 用词法召回；dense-only 用教学版 TF-IDF 余弦作为真实向量的确定性替身；
    hybrid 用 RRF（常数 60）融合两路名次；rerank 在 Top10 内按实词覆盖重排。
  - 四配置共用同一 corpus 与同一 golden set，消融对比才有意义。

【易忽略细节】
  1. 这里**不是**真实稠密向量或真实 Rerank 模型：不接网络、不需要 Key。
     生产替换时只换排序函数，指标与 CI 门禁代码不用改（README 已明确标注）。
  2. 所有排序都带 doc_id 兜底比较，保证同分结果稳定可复现——否则 CI 会假阳性抖动。
  3. 第 9/10 周的 BM25/RRF/重排思路在此复用，但不修改那两周的文件
     （本周开始时那些目录尚未落盘，因此工程保持自包含）。

【示例用途】被 service.py / week12.engineering.runner.py 引用；不单独运行。
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

from rank_bm25 import BM25Okapi
from week11.engineering.guards import content_terms
from week11.engineering.models import SourceChunk

_CORE_DOCUMENTS: tuple[SourceChunk, ...] = (
    SourceChunk("DOC-001", "值班规范", 3, "系统 cyclone 的严重级别为 2 级，影响 30 名用户。"),
    SourceChunk("DOC-001", "值班规范", 4, "cyclone 的负责人为张伟，备用联系人李娜。"),
    SourceChunk("DOC-001", "值班规范", 5, "cyclone 事件需在 15 分钟内响应，超时自动升级。"),
    SourceChunk("DOC-002", "网关手册", 1, "降级链顺序为 qwen、deepseek、glm，依序尝试。"),
    SourceChunk("DOC-002", "网关手册", 2, "令牌桶容量为 100，补充速率为每秒 10 个。"),
    SourceChunk(
        "DOC-002", "网关手册", 3,
        "access_token 在过期前 1000 秒刷新，并发首次只刷新一次。",
    ),
    SourceChunk("DOC-003", "稳定性手册", 1, "熔断器失败阈值为 5 次，恢复窗口为 30 秒。"),
    SourceChunk("DOC-003", "稳定性手册", 2, "每次调用写入 19 字段审计记录，trace_id 串联全链路。"),
    SourceChunk(
        "DOC-003", "稳定性手册", 3,
        "成本等于输入 token 除以 1000 乘输入单价，加输出 token 除以 1000 乘输出单价。",
    ),
    SourceChunk("DOC-004", "交付手册", 1, "SSE 流式响应以 DONE 帧结束，逐块 yield 不攒整段。"),
    SourceChunk(
        "DOC-004", "交付手册", 2,
        "缓存命中率按命中次数除以总请求数统计，降级调用单独记账。",
    ),
    SourceChunk(
        "DOC-005", "RAG 手册", 1,
        "RAG 九环节为解析、切分、嵌入、索引、检索、重排、组装、生成、引用。",
    ),
    SourceChunk("DOC-005", "RAG 手册", 2, "切分策略设置 overlap 为 200 字符，避免语义边界丢失。"),
    SourceChunk("DOC-005", "RAG 手册", 3, "BM25 词法召回与向量召回组成双路混合检索。"),
    SourceChunk("DOC-005", "RAG 手册", 4, "RRF 融合常数为 60，按名次倒数累加两路得分。"),
    SourceChunk("DOC-006", "评测手册", 1, "rerank 取 Top10 候选重排为 Top3，牺牲延迟换精度。"),
    SourceChunk("DOC-006", "评测手册", 2, "Recall 等于 Top5 命中片段数除以标注片段总数。"),
    SourceChunk("DOC-006", "评测手册", 3, "MRR 取首个命中名次倒数，再对全部问题取平均。"),
    SourceChunk(
        "DOC-006", "评测手册", 4,
        "Faithfulness 检查答案中的数字与实体是否在上下文中出现。",
    ),
    SourceChunk(
        "DOC-006", "评测手册", 5,
        "CI 回归比较基线与当前分数，质量下降超阈值即返回退出码 1。",
    ),
    SourceChunk("DOC-X", "归档", 1, "cyclone 的历史版本归档在文档库，最旧版本为 1.0。"),
    SourceChunk("DOC-X", "归档", 2, "缓存的旧规范已作废，请勿继续引用。"),
    SourceChunk("DOC-X", "归档", 3, "RAG 是检索增强生成的缩写，与 RRF 无关。"),
    SourceChunk("DOC-X", "归档", 4, "CI 流水线的通用说明，与质量门禁无关。"),
)

# 每个知识点配一条"旧版归档"干扰片段：真实知识库里大量同主题旧文档是召回噪声来源。
_OLD_LABELS: tuple[str, ...] = (
    "cyclone 严重级别与影响人数", "cyclone 负责人", "cyclone 响应时限",
    "降级链顺序", "令牌桶参数", "access_token 刷新策略",
    "熔断器阈值", "审计字段数", "成本计算规则", "SSE 结束帧",
    "缓存命中率口径", "RAG 九环节", "切分 overlap", "BM25 双路召回",
    "RRF 融合常数", "rerank 候选数", "Recall 定义", "MRR 定义",
    "Faithfulness 定义", "CI 回归退出码",
)
DOCUMENTS: tuple[SourceChunk, ...] = _CORE_DOCUMENTS + tuple(
    SourceChunk(
        "DOC-X", "归档", 10 + index,
        f"{label}的旧版记录已归档，数值以新规范为准。",
    )
    for index, label in enumerate(_OLD_LABELS)
)

CONFIGS: tuple[str, ...] = ("bm25_only", "dense_only", "hybrid", "hybrid_rerank")
RRF_CONSTANT = 60


def _ordered_ids(corpus: Sequence[SourceChunk], scores: Sequence[float]) -> list[str]:
    """按分数降序、片段 ID 升序排；同分稳定，避免 CI 抖动。

    片段 ID 用 source（doc_id#p页码）而不是 doc_id：同一文档不同页是不同证据，
    golden set 的 relevant_chunk_ids 也按这个粒度标注。
    """
    ranked = sorted(
        zip((chunk.source for chunk in corpus), scores, strict=True),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return [chunk_id for chunk_id, _ in ranked]


def _bm25_terms(text: str) -> list[str]:
    """BM25 用中文单字切分（无词典）：第 7 周切分实验的直接后果。

    单字召回宽但噪声大；dense 替身用单字 + 二元组，区分度更高。
    这是切分粒度差异，不是给某个配置"放水"。
    """
    return sorted(term for term in content_terms(text) if len(term) == 1 or term.isalnum())


def bm25_rank(question: str, corpus: Sequence[SourceChunk] = DOCUMENTS) -> list[str]:
    """词法召回：rank-bm25 实现，输入是中文单字 + ASCII 词。"""
    tokenized = [_bm25_terms(chunk.content) for chunk in corpus]
    scores = BM25Okapi(tokenized).get_scores(_bm25_terms(question))
    return _ordered_ids(corpus, scores)


def dense_rank(question: str, corpus: Sequence[SourceChunk] = DOCUMENTS) -> list[str]:
    """教学版稠密替身：TF-IDF 余弦，确定性、可离线复现。"""
    q_terms = content_terms(question)
    if not q_terms:
        return [chunk.source for chunk in corpus]
    docs = [content_terms(chunk.content) for chunk in corpus]
    df = Counter(term for terms in docs for term in terms)
    size = len(corpus)
    idf = {term: math.log((size + 1) / (freq + 1)) + 1.0 for term, freq in df.items()}
    q_vec = Counter(q_terms)
    q_norm = math.sqrt(sum((tf * idf.get(term, 1.0)) ** 2 for term, tf in q_vec.items()))
    scores: list[float] = []
    for terms in docs:
        vec = Counter(terms)
        dot = sum(
            tf * idf.get(term, 1.0) * q_vec.get(term, 0) * idf.get(term, 1.0)
            for term, tf in vec.items()
        )
        norm = math.sqrt(sum((tf * idf.get(term, 1.0)) ** 2 for term, tf in vec.items()))
        scores.append(dot / (norm * q_norm) if norm and q_norm else 0.0)
    return _ordered_ids(corpus, scores)


def hybrid_rank(question: str, corpus: Sequence[SourceChunk] = DOCUMENTS) -> list[str]:
    """RRF 融合两路名次：score(d) = Σ 1/(60 + rank)。"""
    fused: dict[str, float] = {}
    for ranking in (bm25_rank(question, corpus), dense_rank(question, corpus)):
        for rank, chunk_id in enumerate(ranking, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (RRF_CONSTANT + rank)
    return sorted(fused, key=lambda chunk_id: (-fused[chunk_id], chunk_id))


def rerank(
    question: str,
    ranking: Sequence[str],
    corpus: Sequence[SourceChunk] = DOCUMENTS,
) -> list[str]:
    """在 Top10 内按实词覆盖率 + 原文精确出现重排，输出更短的候选列表。"""
    by_id = {chunk.source: chunk for chunk in corpus}
    q_terms = content_terms(question)

    def score(chunk_id: str) -> float:
        chunk = by_id[chunk_id]
        overlap = len(q_terms & content_terms(chunk.content)) / max(1, len(q_terms))
        exact = 0.05 if any(term in chunk.content for term in q_terms if len(term) >= 2) else 0.0
        return overlap + exact

    return sorted(ranking[:10], key=lambda chunk_id: (-score(chunk_id), chunk_id))


def retrieve(
    question: str,
    config: str,
    top_k: int = 5,
    corpus: Sequence[SourceChunk] = DOCUMENTS,
) -> list[str]:
    """四配置统一入口；未知配置直接报错，避免悄悄走默认分支掩盖配置错误。"""
    if config == "bm25_only":
        ranking = bm25_rank(question, corpus)
    elif config == "dense_only":
        ranking = dense_rank(question, corpus)
    elif config == "hybrid":
        ranking = hybrid_rank(question, corpus)
    elif config == "hybrid_rerank":
        ranking = rerank(question, hybrid_rank(question, corpus), corpus)
    else:
        raise ValueError(f"未知检索配置：{config}")
    return ranking[:top_k]


def get_chunks(
    ids: Sequence[str],
    corpus: Sequence[SourceChunk] = DOCUMENTS,
) -> tuple[SourceChunk, ...]:
    """按检索 ID 取回片段；找不到的 ID 跳过，不抛异常打断服务。"""
    by_id = {chunk.source: chunk for chunk in corpus}
    return tuple(by_id[chunk_id] for chunk_id in ids if chunk_id in by_id)
