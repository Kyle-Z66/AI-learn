"""
第 12 周 · P2 项目入口：把 app 交给 uvicorn
================================================================
【对应知识点】文档第 12 周：P2 项目可运行、有 API、有 Docker

【周次学习要点】
  - 入口只暴露 app 实例；业务仍在 service/generation/retrieval，不重复实现。
  - 容器与本地共用同一入口，避免"本地能跑、容器跑不起来"。
  - `python -m week12.p2_rag` 走 __main__.py 自检，不会启动长驻服务。

【易忽略细节】
  1. 生产容器里关掉 reload，避免多进程 + 热重载浪费内存（第 6 周已讲）。
  2. 真实 Key 走环境变量；本项目全本地确定性实现，不需要 Key。
  3. main.py 不写 if __name__ == "__main__" 起服务，测试导入时零副作用。

【示例用途】Docker CMD 指向 `week12.p2_rag.main:app`；CLI 自检见 __main__.py。
"""
from __future__ import annotations

from week12.p2_rag.app import create_app

app = create_app()
