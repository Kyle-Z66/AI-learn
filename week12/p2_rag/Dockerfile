# 第 12 周 · P2 企业 RAG 知识库镜像
# 对应文档：第 12 周「P2 项目可运行，有 API，有 Docker」
# 要点：只装运行依赖（--no-dev）；非 root；镜像内不写任何 API Key。
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

# 构建上下文是仓库根：P2 复用第 11 周守卫、第 6 周交付思路，故复制 week01~12。
COPY pyproject.toml uv.lock README.md ./
COPY week01 week02 week03 week04 week05 week06 ./
COPY week07 week08 week09 week10 week11 week12 ./

RUN uv sync --frozen --no-dev

EXPOSE 8000

USER 10001

CMD ["uv", "run", "--no-dev", "uvicorn", "week12.p2_rag.main:app", "--host", "0.0.0.0", "--port", "8000"]
