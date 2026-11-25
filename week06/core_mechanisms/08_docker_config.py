"""
第 6 周 · 核心机制 08：Dockerfile / compose 静态自检
================================================================
【对应知识点】文档第 6 周：Docker 化，能 docker-compose up 跑起来

【周次学习要点】
  - 镜像只装运行依赖；pytest/mypy/ruff 属于 dev 组，不进生产镜像。
  - 非 root 用户运行，减少容器逃逸风险。
  - API Key 通过环境变量注入，镜像与 compose 文件里都不写明文。

【易忽略细节】
  1. 本机没有 Docker 也能做静态检查：检查 USER / ENV / healthcheck 等关键行。
  2. compose 的 build 上下文指向仓库根，否则复制不到 week01~05 的复用代码。
  3. `${VAR:-}` 提供空默认值，缺 Key 时 Mock 模式仍可启动。

【示例用途】可运行：`python -m week06.core_mechanisms.08_docker_config`
             测试见 tests/week06/test_p1_fastapi.py
"""
from __future__ import annotations

from pathlib import Path


def project_dir() -> Path:
    """week06/p1_fastapi 的绝对路径，与当前工作目录无关。"""
    return Path(__file__).resolve().parents[1] / "p1_fastapi"


def check_config() -> dict[str, bool]:
    dockerfile = (project_dir() / "Dockerfile").read_text(encoding="utf-8")
    compose = (project_dir() / "docker-compose.yml").read_text(encoding="utf-8")
    lowered = (dockerfile + compose).lower()
    return {
        "非 root 运行": "user 10001" in lowered,
        "无硬编码 Key": "api_key=sk" not in lowered and "secret_key=" not in lowered,
        "环境变量注入": "environment" in lowered and "${" in compose,
        "健康检查": "healthcheck" in lowered,
        "构建上下文为仓库根": "context: ../.." in compose,
    }


def demo() -> None:
    for name, passed in check_config().items():
        print(f"{'✓' if passed else '✗'} {name}")
    print("说明：静态检查不等于 docker build 成功，本机有 Docker 时仍需实跑一次")


if __name__ == "__main__":
    demo()
