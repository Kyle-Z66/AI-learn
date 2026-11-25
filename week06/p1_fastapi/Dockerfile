# 第 6 周 · P1 服务容器镜像
# 对应文档：第 6 周「Docker 化」任务
# 要点：只装运行依赖（--no-dev）；非 root 运行；镜像内不写任何 API Key。
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# uv 负责依赖安装（第 1 周工程规范），锁文件保证可复现
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY week01 week02 week03 week04 week05 week06 ./

# dev 组（ruff/mypy/pytest）不进生产镜像
RUN uv sync --frozen --no-dev

EXPOSE 8000

# 非 root 用户运行，降低容器逃逸风险
USER 10001

CMD ["uv", "run", "--no-dev", "uvicorn", "week06.p1_fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
