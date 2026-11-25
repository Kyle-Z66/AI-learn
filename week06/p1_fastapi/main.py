"""
第 6 周 · 动手项目入口：P1 FastAPI 服务
================================================================
【对应知识点】文档第 6 周：FastAPI 暴露 REST 接口 + Docker 化

【周次学习要点】
  - 入口文件只做一件事：把第 6 周工程层的 app 实例交给 uvicorn。
  - 业务逻辑仍在 week03 网关 / week05 稳定性层，这里没有重复实现。
  - 容器与本地用同一入口，避免"本地能跑、容器跑不起来"。

【易忽略细节】
  1. reload 在容器里要关掉，否则多进程 + 热重载会占用额外内存。
  2. host=0.0.0.0 才能让容器外部访问；本地开发用 127.0.0.0.1 更安全。
  3. 真实 Key 通过环境变量注入，代码里只保留变量名。

【示例用途】容器 CMD 指向本文件；CLI：`uv run python -m week06.p1_fastapi`
"""
from __future__ import annotations

from week06.engineering.app import create_app

app = create_app()
