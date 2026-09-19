# routers/chat.py — 课程问答（知识库优先，未命中走 LLM 多轮）

from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest
from core.agent_loop import run_chat_pipeline

router = APIRouter()


@router.post("/ask")
def ask(req: ChatRequest):
    """提问。先搜知识库，命中直接答；未命中调 LLM（带最近 8 条历史）。"""
    history = None
    if req.history:
        history = [m.model_dump() for m in req.history]

    try:
        result = run_chat_pipeline(
            req.question,
            history=history,
            course_context=req.course_context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败：{e}") from e

    return result
