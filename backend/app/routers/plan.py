# routers/plan.py — 学习方案生成（多 Agent 流水线）

"""方案生成接口：Planner → Searcher → Writer → Reviewer。

注意：run_plan_pipeline 是阻塞调用（内部多次调 LLM），
FastAPI 的 def 端点自动跑在线程池里，不阻塞事件循环。
"""

from fastapi import APIRouter, HTTPException

from app.schemas import PlanRequest
from core.agent_loop import run_plan_pipeline
from tools.progress_store import save_result

router = APIRouter()


@router.post("/generate")
def generate_plan(req: PlanRequest):
    """生成学习方案。返回 outline / resources / plan，自动存入历史。"""
    profile = None
    if req.profile is not None:
        profile = req.profile.model_dump()

    try:
        result = run_plan_pipeline(req.course, profile=profile, use_cache=req.use_cache)
    except Exception as e:  # 业务层已有兜底，这里防意外
        raise HTTPException(status_code=500, detail=f"生成失败：{e}") from e

    # 存历史 + 进度（与桌面版行为一致）
    try:
        save_result(req.course, result)
    except Exception:
        pass  # 持久化失败不影响返回

    return result
