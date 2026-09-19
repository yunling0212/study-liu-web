# routers/progress.py — 学习进度：历史课程 / 勾选 / 统计

from fastapi import APIRouter, HTTPException, Query

from app.schemas import CourseNameIn, ToggleIn
from tools.progress_store import (
    delete_course,
    get_progress,
    get_stats,
    list_courses,
    load_result,
)

router = APIRouter()


@router.get("/courses")
def history_courses():
    """历史课程列表（按最近使用倒序）。"""
    return list_courses()


@router.get("/course")
def course_detail(course: str = Query(..., min_length=1)):
    """某课程：完整方案 + 进度勾选状态 + 统计。"""
    result = load_result(course)
    if result is None:
        raise HTTPException(status_code=404, detail=f"课程「{course}」还没有生成过方案")
    progress = get_progress(course)
    done, total, ratio = get_stats(course)
    return {
        "course": course,
        "result": result,
        "progress": progress,
        "stats": {"done": done, "total": total, "ratio": round(ratio, 4)},
    }


@router.post("/toggle")
def toggle(req: ToggleIn):
    """勾选 / 取消一项（kind=outline 或 plan）。"""
    ok = set_done_safe(req.course, req.kind, req.index, req.done)
    if not ok:
        raise HTTPException(status_code=400, detail="课程不存在或索引越界")
    done, total, ratio = get_stats(req.course)
    return {"ok": True, "stats": {"done": done, "total": total, "ratio": round(ratio, 4)}}


@router.post("/delete")
def remove_course(req: CourseNameIn):
    """删除一门课程及其进度。"""
    ok = delete_course(req.course)
    return {"ok": ok}


def set_done_safe(course, kind, index, done):
    """包一层避免直接把 progress_store.set_done 引入路由命名空间。"""
    from tools.progress_store import set_done

    return set_done(course, kind, index, done)
