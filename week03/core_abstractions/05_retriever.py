"""
第 3 周 · 核心抽象 05：Retriever（检索器）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」第 5 项：Retriever

【周次学习要点】
  - Retriever 按查询召回相关文档：输入 str，输出 list[Document]。
  - 本周只认接口 invoke(query)，用内存版关键词检索演示，不碰向量库。
  - 它是第 7~10 周 RAG 全链路的入口抽象，现在认准接口即可，不要提前深挖。

【易忽略细节】
  1. 自定义 Retriever 要继承 BaseRetriever 并实现 _get_relevant_documents。
  2. BaseRetriever 是 Pydantic 模型，字段必须有类型注解（docs: list[Document]）。
  3. 文档切分 / Embedding / 向量库 / Rerank 属于第 7~10 周，本周明确不越界。

【示例用途】可运行：`python week03/core_abstractions/05_retriever.py`
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class KeywordRetriever(BaseRetriever):
    """内存版关键词检索器：只演示 Retriever 接口形态，不是生产实现。"""

    docs: list[Document]  # BaseRetriever 继承 Pydantic，字段必须带注解

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """最朴素的包含匹配；run_manager 是框架回调钩子，本例不使用。
        第 9 周会换成混合检索 + Rerank。
        """
        return [doc for doc in self.docs if query in doc.page_content]


def build_retriever() -> KeywordRetriever:
    """构造 3 条示例文档，覆盖网关、降级、成本三个主题。"""
    return KeywordRetriever(docs=[
        Document(page_content="网关负责统一模型接入与请求路由", metadata={"id": 1}),
        Document(page_content="降级链在主模型不可用时自动切换备用模型", metadata={"id": 2}),
        Document(page_content="成本由输入 token 与输出 token 分别计价得出", metadata={"id": 3}),
    ])


def demo() -> None:
    retriever = build_retriever()
    for query in ("网关", "降级", "成本"):
        docs = retriever.invoke(query)  # 本周只需会用这个统一入口
        print(f"查询 {query!r} → {[d.metadata['id'] for d in docs]}")


if __name__ == "__main__":
    demo()
