# routers/knowledge.py — 知识库：增 / 删 / 查 / 粘贴导入 / 文件导入

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import NoteIdIn, NoteIn, PasteImportIn, SearchIn
from tools.document_importer import import_file, list_supported_extensions, paste_import
from tools.knowledge_store import KnowledgeStore

router = APIRouter()


@router.get("/list")
def list_notes():
    """全部笔记（新 → 旧）。"""
    return KnowledgeStore().list_all()


@router.post("/search")
def search_notes(req: SearchIn):
    """按关键词搜笔记（标题/内容/标签，不区分大小写）。"""
    return KnowledgeStore().search(req.keyword)


@router.post("/add")
def add_note(req: NoteIn):
    """新增一条笔记，返回 id。"""
    note_id = KnowledgeStore().add(req.title, req.content, tags=req.tags)
    return {"id": note_id, "ok": True}


@router.post("/delete")
def delete_note(req: NoteIdIn):
    """按 id 删除笔记。"""
    ok = KnowledgeStore().delete(req.id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"笔记 {req.id} 不存在")
    return {"ok": True}


@router.post("/import/paste")
def import_paste(req: PasteImportIn):
    """粘贴文本导入，返回新笔记 id（业务层空文本抛 ValueError）。"""
    try:
        note_id = paste_import(req.text, title=req.title, tags=req.tags or None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True, "id": note_id}


@router.post("/import/file")
async def import_uploaded_file(file: UploadFile = File(...), title: str = ""):
    """上传 PDF / Markdown / TXT 导入（自动抽取关键句）。"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in list_supported_extensions():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式 {ext}，支持：{', '.join(list_supported_extensions())}",
        )

    # 落到临时文件再走统一导入逻辑（业务层按路径解析）
    suffix = ext if ext else ".txt"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix="studyliu_import_"
        ) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        note_id = import_file(tmp_path, title=title or None)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败：{e}") from e
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    return {"ok": True, "id": note_id, "filename": file.filename}
