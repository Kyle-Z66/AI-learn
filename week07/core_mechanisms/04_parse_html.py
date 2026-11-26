"""
第 7 周 · 核心机制 04：HTML 解析与噪声清理
================================================================
【对应知识点】文档第 7 周：HTML 解析（BeautifulSoup）

【周次学习要点】
  - 先 decompose 掉 script/style/noscript，再 get_text，避免噪声进入切分。
  - h1~h3 作为 sections，保留文档的层级线索。
  - 相比 Java 的 Jsoup select，BS4 的 find_all 更简洁，但同样要显式声明关注标签。

【易忽略细节】
  1. get_text("\\n", strip=True) 会把相邻行也拆开，后续切分要能处理多行段落。
  2. 不清理 script 时，跟踪代码会变成"正文"，embedding 后污染检索结果。
  3. title 标签与 h1 可能不同：Document.title 用 title，sections 用 h1~h3。

【示例用途】可运行：`python -m week07.core_mechanisms.04_parse_html`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.engineering.fixtures import write_html
from week07.engineering.parsers import parse_html


def parse_generated_html() -> tuple[str, bool, int]:
    """生成临时 HTML 并解析，返回 (标题, 是否含脚本噪声, 标题数)。"""
    with tempfile.TemporaryDirectory() as directory:
        path = write_html(Path(directory) / "incident.html")
        document = parse_html(path)
        return document.title, "NOISE_SCRIPT" in document.text, len(document.sections)


def demo() -> None:
    title, has_noise, section_count = parse_generated_html()
    print(f"解析结果：title={title} 脚本噪声残留={has_noise} 标题数={section_count}")
    print("提示：脚本必须先删，否则它会被当成正文切分并进入向量库。")


if __name__ == "__main__":
    demo()
