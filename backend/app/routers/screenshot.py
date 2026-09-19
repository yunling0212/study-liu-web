# routers/screenshot.py — 截图讲解：上传图片 → OCR → LLM 讲解

"""两条路：
1. POST /ocr   上传图片 → OCR 提取文字 → 返回文字（前端可编辑）
2. POST /explain  把（可能已编辑的）文字发给 LLM 讲解

设计说明：服务器（2C2G）不装 EasyOCR/torch，is_ocr_available() 为 False 时，
前端引导用户"看图打字"——这是文档化的兜底路径，与桌面版行为一致。
OCR 与讲解拆成两步，用户可在讲解前修正 OCR 识别错误的公式/符号。
"""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import ScreenshotTextIn
from tools.screenshot_ocr import (
    extract_text_from_image,
    format_ocr_for_llm,
    get_supported_formats,
    is_ocr_available,
)

router = APIRouter()


@router.get("/status")
def ocr_status():
    """OCR 是否可用（前端据此决定展示上传框还是粘贴框）。"""
    return {
        "ocr_available": is_ocr_available(),
        "supported_formats": get_supported_formats(),
    }


@router.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """上传截图 → OCR 提取文字。OCR 不可用时返回 503 + 提示走粘贴。"""
    if not is_ocr_available():
        raise HTTPException(
            status_code=503,
            detail="服务器未安装 OCR 引擎，请直接粘贴截图中的文字（/explain 接口）",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in get_supported_formats():
        raise HTTPException(status_code=400, detail=f"不支持的图片格式：{ext}")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=ext, prefix="studyliu_shot_"
        ) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        ocr_result = extract_text_from_image(tmp_path)
        if ocr_result.get("error"):
            raise HTTPException(status_code=500, detail=ocr_result["error"])
        return ocr_result
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


@router.post("/explain")
def explain(req: ScreenshotTextIn):
    """把截图文字（OCR 或手动粘贴）交给 LLM 讲解。"""
    from core.llm import chat

    ocr_result = {"text": req.text, "backend": "paste-or-frontend-ocr"}
    prompt = format_ocr_for_llm(ocr_result, user_hint=req.user_hint)

    answer = chat([
        {"role": "system", "content": "你是耐心的学习助教，负责讲解学生截图里的知识点。用中文，条理清晰，先概括再展开，必要时给出例题。"},
        {"role": "user", "content": prompt},
    ])
    return {"answer": answer}
