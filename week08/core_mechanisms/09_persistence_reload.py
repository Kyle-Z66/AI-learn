"""
第 8 周 · 核心机制 09：持久化与重载一致性
================================================================
【对应知识点】文档第 8 周：向量库部署 / 数据落盘

【周次学习要点】
  - 向量库重启后必须能从磁盘恢复，否则服务不可用。
  - 用 JSON 存快照：人类可读、git 可 diff、不执行反序列化代码。
  - 重载后同一查询的 Top-K 顺序必须与保存前完全一致。

【易忽略细节】
  1. pickle 反序列化会执行代码，绝不能用于不可信来源的索引文件。
  2. 浮点文本化再读回会有极小误差，比较时用近似而非严格相等。
  3. 生产库还要持久化索引参数（ef_search / lists），这里只存数据。

【示例用途】可运行：`python -m week08.core_mechanisms.09_persistence_reload`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.vector_store import load_store, save_store

# 数字前缀模块只能通过 importlib 导入，和 week06 测试的写法一致。
STORE_MODULE = importlib.import_module("week08.core_mechanisms.08_vector_store")
QUERY = "SGCC-4012 上游超时"


def persistence_roundtrip() -> tuple[list[str], list[str]]:
    """保存并重载，返回 (保存前 Top-3, 重载后 Top-3)。"""
    embedder = HashEmbedding(16)
    store = STORE_MODULE.build_store()
    query = tuple(embedder.embed_query(QUERY))
    before = [hit.record.id for hit in store.search(query, top_k=3)]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "store.json"
        save_store(store, path)
        restored = load_store(path)
    after = [hit.record.id for hit in restored.search(query, top_k=3)]
    return before, after


def demo() -> None:
    before, after = persistence_roundtrip()
    print(f"保存前 Top-3：{before}")
    print(f"重载后 Top-3：{after}")
    print("两者一致：", before == after)


if __name__ == "__main__":
    demo()
