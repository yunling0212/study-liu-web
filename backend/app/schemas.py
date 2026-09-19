# schemas.py — 请求 / 响应模型（Pydantic）

"""API 数据模型。字段与桌面版 core 层约定保持一致，方便对照。"""

from typing import Optional

from pydantic import BaseModel, Field


# ---------- 方案生成 ----------
class ProfileIn(BaseModel):
    """用户画像（与 tools/user_profile.py 字段一致）。"""

    level: str = "入门"          # 入门 | 进阶 | 冲刺
    daily_hours: str = "2h"      # 1h | 2h | 4h
    goal: str = "兴趣"           # 考试 | 项目 | 兴趣
    deadline: str = ""           # YYYY-MM-DD 或空


class PlanRequest(BaseModel):
    course: str = Field(..., min_length=1, max_length=100, description="课程名")
    profile: Optional[ProfileIn] = None
    use_cache: bool = True


# ---------- 课程问答 ----------
class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    history: Optional[list[ChatMessage]] = None
    course_context: Optional[str] = None


# ---------- 知识库 ----------
class NoteIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=20000)
    tags: list[str] = []


class NoteIdIn(BaseModel):
    id: int


class SearchIn(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)


class PasteImportIn(BaseModel):
    """粘贴文本导入（自动抽取关键句）。"""

    text: str = Field(..., min_length=1, max_length=100000)
    title: Optional[str] = None
    tags: list[str] = []


# ---------- 进度 ----------
class ToggleIn(BaseModel):
    course: str
    kind: str = Field(..., pattern="^(outline|plan)$")
    index: int = Field(..., ge=0)
    done: bool


class CourseNameIn(BaseModel):
    course: str


# ---------- 截图讲解 ----------
class ScreenshotTextIn(BaseModel):
    """OCR 不可用时的手动粘贴兜底：直接把截图里的文字贴过来。"""

    text: str = Field(..., min_length=1, max_length=10000)
    user_hint: str = ""


# ---------- 设置 ----------
class SettingsIn(BaseModel):
    provider: str = "mock"       # deepseek / openai / mock
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
