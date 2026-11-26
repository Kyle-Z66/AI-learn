"""
第 12 周 · P2 项目 CLI：只做导入与自检，不启动长驻服务
================================================================
【对应知识点】文档第 12 周：P2 项目可运行（本地自检形态）

【周次学习要点】
  - `python -m week12.p2_rag` 验证"导入成功 + 相关问答有引用 + 无关问题拒答"。
  - 自检结果用退出码表达：0 = 通过，1 = 失败，可直接放进 CI 冒烟步骤。
  - 真实服务用 `uvicorn week12.p2_rag.main:app` 启动，与本入口互不影响。

【易忽略细节】
  1. 不要在 __main__ 里 import uvicorn 并 run()：那会让"仅验证导入"的命令卡住。
  2. 自检用的两条问题与 golden set 无关，避免自检依赖评测数据文件。
  3. Java 常用 main(String[] args) 做启动器；这里把自检与启动分离，
     Python 的 `python -m package` 约定让包本身可执行。

【示例用途】可运行：`python -m week12.p2_rag`（仅自检，几毫秒内退出）。
"""
from __future__ import annotations

from week12.p2_rag.service import RAGService


def self_check() -> bool:
    """返回 True 表示 P2 项目导入与基本链路正常。"""
    return RAGService().self_check()


def main() -> None:
    ok = self_check()
    print("P2 RAG 自检：", "通过（相关问答带引用，无关问题拒答）" if ok else "失败")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
