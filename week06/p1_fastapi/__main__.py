"""
第 6 周 · 动手项目 CLI：`python -m week06.p1_fastapi`
================================================================
【对应知识点】文档第 6 周：P1 服务本地启动

【周次学习要点】
  - `__main__.py` 让包可以直接用 -m 启动，和前几周 __main__ 约定一致。
  - 真正的应用对象在 main.py，测试与容器都 import 同一实例。

【易忽略细节】
  1. reload=False：默认关闭热重载，容器行为与本地一致。
  2. 启动后访问 /docs 看自动生成的 OpenAPI 文档。

【示例用途】可运行：`uv run python -m week06.p1_fastapi`
"""
from __future__ import annotations

import uvicorn

from week06.p1_fastapi.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
