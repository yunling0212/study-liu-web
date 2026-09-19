# routers/export.py — 导出：Markdown（.md）与学习日历（.ics）

import os
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from core.paths import data_dir
from tools.calendar_export import export_plan_to_ics, suggest_ics_filename
from tools.markdown_export import export_plan_to_file, suggest_filename
from tools.progress_store import load_result

router = APIRouter()


def _download_headers(filename: str) -> dict:
    """中文文件名必须 URL 编码（HTTP 头只允许 latin-1）。"""
    return {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}


def _load_or_404(course: str) -> dict:
    result = load_result(course)
    if result is None:
        raise HTTPException(status_code=404, detail=f"课程「{course}」还没有生成过方案")
    return result


@router.get("/markdown", response_class=PlainTextResponse)
def export_markdown(course: str = Query(..., min_length=1)):
    """把已生成的方案渲染成 Markdown 并下载。"""
    result = _load_or_404(course)
    filename = suggest_filename(course)
    out_dir = os.path.join(data_dir(), "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    export_plan_to_file(result, out_path, course=course)
    return PlainTextResponse(
        content=open(out_path, "r", encoding="utf-8").read(),
        media_type="text/markdown",
        headers=_download_headers(filename),
    )


@router.get("/ics", response_class=PlainTextResponse)
def export_ics(course: str = Query(..., min_length=1)):
    """把学习计划导出为 .ics 日历文件（Google/苹果/Outlook 可直接导入）。"""
    result = _load_or_404(course)
    filename = suggest_ics_filename(course)
    out_dir = os.path.join(data_dir(), "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    export_plan_to_ics(result, out_path)
    return PlainTextResponse(
        content=open(out_path, "r", encoding="utf-8").read(),
        media_type="text/calendar",
        headers=_download_headers(filename),
    )
