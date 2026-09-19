# main.py — FastAPI 入口

"""study-liu Web 版后端。

结构：
    app/main.py      本文件：应用创建、CORS、路由挂载、静态托管
    app/routers/     各功能域路由（plan/chat/knowledge/progress/export/screenshot/settings）
    core/ agents/ tools/ i18n/   ← 桌面版业务层原样复用（未改动）

启动（开发）：
    cd backend
    pip install -r requirements.txt
    python run.py
启动（生产）：
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
"""

import os
import sys

# 让 app/ 能 import 同级的 core / agents / tools / i18n
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.routers import (  # noqa: E402
    chat,
    export,
    knowledge,
    plan,
    progress,
    screenshot,
    settings,
)

app = FastAPI(
    title="study-liu API",
    description="学习智能助手 Web 版 — 粤港澳大湾区 AI Coding 创新大赛",
    version="1.0.0",
)

# CORS：允许任何来源（比赛演示场景；正式部署可收紧为前端域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API 路由 ----------
app.include_router(plan.router, prefix="/api/plan", tags=["plan"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(screenshot.router, prefix="/api/screenshot", tags=["screenshot"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.get("/api/health", tags=["meta"])
def health():
    """健康检查：部署后先访问这个确认服务活着。"""
    from core.config import get_mode_label

    label, mode = get_mode_label()
    return {"ok": True, "mode": mode, "mode_label": label}


# ---------- 前端静态托管 ----------
# 前端构建产物（或本骨架的纯静态页）放在 ../frontend，
# 由 FastAPI 直接托管 —— 单容器即可上线，无需 nginx。
_FRONTEND_DIR = os.path.join(os.path.dirname(_BACKEND_ROOT), "frontend")
if os.path.isdir(_FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIR), name="assets")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))
