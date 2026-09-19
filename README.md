# study-liu · 学习智能助手（Web 版）

> 粤港澳大湾区 AI Coding 创新大赛 · 方向一「AI + 教学管理助手 — 多模态教学智能体」
> 深大计软 & 腾讯云 | 团队：黄思扬（光电信息科学与工程·大二·队长）/ 软件工程·大三 / 计算机科学与技术·大三

## 一句话介绍

输入课程名和个人画像，**Planner → Searcher → Writer → Reviewer 多智能体流水线**自动生成个性化学习方案；配套知识库问答、学习进度管理、Markdown/日历导出、截图讲解。支持多 LLM 平台（DeepSeek 等），内置 Mock 离线模式，LLM 不可用时**明确警告并自动降级**（绝不静默糊弄）。

## 功能总览

| 模块 | 能力 |
|---|---|
| 🎯 方案生成 | 课程名 + 画像（水平/时长/目标/截止日）→ 大纲 + 资源 + 每日计划；截止日驱动天数；结果缓存（同课程同画像 24h 不重复调用 API） |
| 💬 课程问答 | 知识库笔记优先作答，未命中走 LLM 多轮对话（最近 8 条上下文） |
| 📚 知识库 | 增删查 + 粘贴导入（自动抽取关键句）+ PDF/MD/TXT 文件导入 |
| ✅ 进度管理 | 大纲/每日计划逐项勾选，进度条统计，历史课程回看 |
| 📤 导出 | Markdown 学习方案 + .ics 学习日历（Google/苹果/Outlook 可导入） |
| 📷 截图讲解 | 截图文字 → LLM 助教讲解（服务器无 OCR 时走粘贴兜底） |
| 🔐 工程化 | API Key AES-GCM 加密落盘、滑动窗口限流、降级感知警告、中英双语、暗色模式 |

## 技术架构

```
frontend/            纯静态前端（HTML/CSS/JS，无构建依赖，FastAPI 直接托管）
backend/
  app/               FastAPI 应用层（路由 / Pydantic 模型 / 静态托管）
    main.py          入口：CORS + 路由挂载 + 前端托管
    routers/         plan / chat / knowledge / progress / export / screenshot / settings
    schemas.py       请求/响应模型
  core/              配置 / LLM 客户端 / Agent 编排 / 意图识别 / 路径解析  ← 桌面版原样复用
  agents/            Planner / Searcher / Writer / Reviewer 四智能体      ← 桌面版原样复用
  tools/             知识库 / 进度 / 缓存 / 限流 / 导出 / 加密 / 导入      ← 桌面版原样复用
  i18n/              中英文案表                                       ← 桌面版原样复用
  data/              运行时数据（knowledge.json 为演示种子）
```

**核心设计**：桌面版（tkinter）与 Web 版共享同一套业务层（core/agents/tools），Web 化零重写——这是分层架构的直接收益。

## 快速开始

### 本地开发

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env       # 填入 DeepSeek API Key（不填则 Mock 模式，可完整演示）
python run.py              # http://localhost:8000
```

### Docker 一键部署（推荐，比赛用）

```bash
# 服务器上（已装 docker + docker compose 插件）：
cp backend/.env.example backend/.env   # 填入 API Key
docker compose up -d --build
# 访问 http://<服务器IP>:8000
```

> ⚠️ 部署提醒：国内云服务器**直接用 IP:8000 访问，不要绑域名**（ICP 备案 1~3 周，赶不上比赛截止）。若绑域名需购买境外区域服务器。

### 冒烟检查

```bash
curl http://localhost:8000/api/health
# {"ok":true,"mode":"mock","mode_label":"Mock 模式"}  ← 服务正常
```

更完整的接口冒烟测试（17 项，覆盖生成/问答/知识库/进度/导出/截图讲解全链路）：

```bash
python smoke_test.py   # 依赖 fastapi + httpx，任意目录可直接跑
```

## API 速览（完整文档：/docs，FastAPI 自动生成）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/plan/generate | 生成学习方案（多 Agent 流水线） |
| POST | /api/chat/ask | 课程问答（知识库优先） |
| GET/POST | /api/knowledge/* | 笔记增删查 + 粘贴/文件导入 |
| GET | /api/progress/courses | 历史课程 |
| POST | /api/progress/toggle | 勾选进度项 |
| GET | /api/export/markdown?course=… | 导出 .md |
| GET | /api/export/ics?course=… | 导出 .ics 日历 |
| POST | /api/screenshot/explain | 截图文字 AI 讲解 |
| GET | /api/settings/status | 当前 LLM 模式（Key 掩码显示） |

## 第三方依赖声明

| 库 | 用途 | 协议 |
|---|---|---|
| FastAPI / Uvicorn / Starlette | Web 框架与服务器 | MIT |
| Pydantic | 数据校验 | MIT |
| requests | LLM API 调用 | Apache-2.0 |
| python-dotenv | 环境变量 | BSD-3 |
| cryptography | API Key AES-GCM 加密 | Apache-2.0 / BSD-3 |
| Pillow / pypdf / pdfplumber | 文档导入解析 | HPND / BSD-3 / MIT |

本项目采用 **MIT 协议**开源。

## 团队分工

| 成员 | 专业 | 职责 |
|---|---|---|
| 黄思扬 | 光电信息科学与工程（大二） | 队长 · 后端集成 · AI 结对开发（LearnBuddy/WorkBuddy）· 演示视频 |
| 队友 | 软件工程（大三） | 前端工程 · Docker 部署 · 仓库管理 |
| 队友 | 计算机科学与技术（大三） | 前端功能模块 · 测试 · PPT 与材料 |

## 开发时间线（比赛倒排）

- 9/19–9/20：骨架落地，核心链路跑通
- 9/21–9/22：功能补全 + 云部署上线
- 9/23：联调回归，链接稳定可演示
- 9/24：材料日（视频 / PPT / README）
- 9/25：**第一版提交**（LearnBuddy 赛事专区）
- 9/26：终检 + 最终提交（23:59 截止）
