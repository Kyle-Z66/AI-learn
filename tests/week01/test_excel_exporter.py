"""
第 1 周单元测试 · 动手项目：Excel 批量导出器
"""
from __future__ import annotations

import io
import zipfile

import pytest
from openpyxl import load_workbook
from week01.excel_exporter.exporter import build_xlsx_bytes, build_zip, chunk_rows, export_excel
from week01.excel_exporter.models import ExportRow, ExportTask


def make_rows(count: int) -> list[ExportRow]:
    return [
        ExportRow(
            id=i, name=f"用户{i}", department="研发部", amount=float(i), exported_at="2026-11-23"
        )
        for i in range(1, count + 1)
    ]


def test_chunk_rows() -> None:
    chunks = chunk_rows(make_rows(250), 100)
    assert [len(c) for c in chunks] == [100, 100, 50]
    assert chunks[0][0].id == 1
    assert chunks[-1][-1].id == 250
    with pytest.raises(ValueError):
        chunk_rows(make_rows(3), 0)


def test_build_xlsx_bytes() -> None:
    data = build_xlsx_bytes("part1", make_rows(2))
    workbook = load_workbook(io.BytesIO(data))
    sheet = workbook["part1"]
    assert sheet.max_row == 3  # 表头 + 2 行
    assert sheet["A2"].value == 1
    assert sheet["B2"].value == "用户1"


def test_build_zip() -> None:
    data = build_zip([("a.xlsx", b"aaa"), ("b.xlsx", b"bbb")])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.namelist() == ["a.xlsx", "b.xlsx"]
        assert archive.read("a.xlsx") == b"aaa"


async def test_export_excel_end_to_end() -> None:
    task = ExportTask(task_id="TEST", rows=make_rows(250))
    zip_bytes = await export_excel(task, chunk_size=100)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        assert names == ["TEST_part1.xlsx", "TEST_part2.xlsx", "TEST_part3.xlsx"]
        workbook = load_workbook(io.BytesIO(archive.read(names[0])))
        assert workbook.active.max_row == 101  # 表头 + 100 行
