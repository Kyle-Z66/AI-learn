"""
第 8 周 · 核心机制 03：Embedding 模型选型
================================================================
【对应知识点】文档第 8 周：bge-m3 / qwen3-embedding / text-embedding-v3

【周次学习要点】
  - bge-m3：多语言、稠密 + 稀疏双输出，适合后续第 9 周做混合检索。
  - qwen3-embedding：中文语境强，可作为纯稠密方案的本地或 API 选择。
  - text-embedding-v3：阿里云 API，运维成本最低但要考虑数据出域与费用。

【易忽略细节】
  1. 维度不是越大越好：1024 维的索引成本约为 256 维的 4 倍。
  2. 稀疏向量只有支持混合检索的库才能用，选错库等于白生成。
  3. 一旦换模型必须全量重嵌，旧向量与新向量不能混在同一个索引里。

【示例用途】可运行：`python -m week08.core_mechanisms.03_model_selection`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

# (名称, 向量类型, 语言侧重, 默认维度, 部署方式)
MODEL_CATALOG: tuple[tuple[str, str, str, int, str], ...] = (
    ("bge-m3", "稠密+稀疏", "多语言/中文强", 1024, "本地部署"),
    ("qwen3-embedding", "稠密", "中文强", 1024, "本地或 API"),
    ("text-embedding-v3", "稠密", "中文/多语言", 1024, "阿里云 API"),
)


def select_model(*, need_sparse: bool, avoid_external_api: bool) -> str:
    """按约束返回模型名；无解时抛 ValueError。"""
    for name, vector_type, _language, _dim, deploy in MODEL_CATALOG:
        if need_sparse and "稀疏" not in vector_type:
            continue
        if avoid_external_api and "API" in deploy and "本地" not in deploy:
            continue
        return name
    raise ValueError("没有满足约束的模型，请放宽条件")


def demo() -> None:
    print("模型               类型        语言侧重        维度  部署")
    for name, vector_type, language, dim, deploy in MODEL_CATALOG:
        print(f"{name:<18} {vector_type:<10} {language:<14} {dim:<5} {deploy}")
    print("需要稀疏向量且不出域：", select_model(need_sparse=True, avoid_external_api=True))
    print("允许 API 且要稀疏：", select_model(need_sparse=True, avoid_external_api=False))


if __name__ == "__main__":
    demo()
