# smoke_test.py — Web 骨架冒烟测试（临时脚本，验证后删除）
"""验证 FastAPI 应用可启动、核心接口全链路可用（mock 模式）。"""

import os
import sys

BACKEND = r"c:\Users\ASUS\WorkBuddy\20260918150307\study-liu-web\backend"
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)  # 让 data_dir 落在 backend/data

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}" + (f"  → {detail}" if detail and not cond else ""))


# 1. 健康检查
r = client.get("/api/health")
check("health", r.status_code == 200 and r.json().get("ok"), r.text)

# 2. 方案生成（mock 模式，走完整 4-agent 流水线）
r = client.post("/api/plan/generate", json={
    "course": "高等数学",
    "profile": {"level": "入门", "daily_hours": "2h", "goal": "考试", "deadline": ""},
    "use_cache": False,
})
body = r.json()
check("plan.generate", r.status_code == 200 and body.get("plan"), r.text[:300])
check("plan.has_outline", bool(body.get("outline")))
check("plan.has_resources", bool(body.get("resources")))

# 3. 知识库（种子数据）
r = client.get("/api/knowledge/list")
notes = r.json()
check("knowledge.list", r.status_code == 200 and len(notes) >= 5, f"n={len(notes)}")

# 4. 问答命中知识库
r = client.post("/api/chat/ask", json={"question": "二重积分"})
check("chat.knowledge_hit", r.status_code == 200 and r.json().get("source") == "knowledge", r.text[:200])

# 5. 问答走 LLM（mock 兜底，未命中知识库）
r = client.post("/api/chat/ask", json={
    "question": "什么是量子隧穿效应",
    "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "你好"}],
})
check("chat.llm_fallback", r.status_code == 200 and r.json().get("answer"), r.text[:200])

# 6. 进度
r = client.get("/api/progress/courses")
check("progress.courses", r.status_code == 200 and any(c["course"] == "高等数学" for c in r.json()), r.text[:200])
r = client.get("/api/progress/course", params={"course": "高等数学"})
d = r.json()
check("progress.detail", r.status_code == 200 and d.get("stats", {}).get("total", 0) > 0, r.text[:200])
r = client.post("/api/progress/toggle", json={"course": "高等数学", "kind": "plan", "index": 0, "done": True})
check("progress.toggle", r.status_code == 200 and r.json().get("ok"), r.text[:200])

# 7. 导出
r = client.get("/api/export/markdown", params={"course": "高等数学"})
check("export.markdown", r.status_code == 200 and "# 📘 高等数学 学习方案" in r.text, r.text[:200])
r = client.get("/api/export/ics", params={"course": "高等数学"})
check("export.ics", r.status_code == 200 and "BEGIN:VEVENT" in r.text, r.text[:200])

# 8. 知识库新增 + 删除
r = client.post("/api/knowledge/add", json={"title": "测试笔记", "content": "测试内容", "tags": ["test"]})
check("knowledge.add", r.status_code == 200 and r.json().get("id"), r.text[:200])
if r.status_code == 200:
    client.post("/api/knowledge/delete", json={"id": r.json()["id"]})

# 9. 粘贴导入
r = client.post("/api/knowledge/import/paste", json={
    "text": "机器学习是通过数据训练模型的方法。深度学习是机器学习的分支。神经网络由多层构成。",
    "title": None, "tags": [],
})
check("knowledge.paste_import", r.status_code == 200 and r.json().get("ok"), r.text[:300])

# 10. 截图讲解（mock 模式下 chat 会返回 mock 内容或失败提示）
r = client.post("/api/screenshot/explain", json={"text": "x^2 + y^2 = r^2 圆的方程", "user_hint": ""})
check("screenshot.explain", r.status_code == 200 and r.json().get("answer"), r.text[:200])

# 11. 设置状态
r = client.get("/api/settings/status")
check("settings.status", r.status_code == 200 and r.json().get("mode"), r.text[:200])

# 12. 首页静态文件
r = client.get("/")
check("index.html", r.status_code == 200 and "study-liu" in r.text)

print(f"\n===== {len(PASS)} passed / {len(FAIL)} failed =====")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
