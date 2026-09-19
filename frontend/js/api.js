// api.js — 后端 API 封装（全部走 /api 前缀）

const API = {
  async request(path, options = {}) {
    const resp = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!resp.ok) {
      let detail = `HTTP ${resp.status}`;
      try {
        const body = await resp.json();
        detail = body.detail || JSON.stringify(body);
      } catch (_) { /* 非 JSON 错误体 */ }
      throw new Error(detail);
    }
    return resp.json();
  },

  // ---- 方案生成 ----
  generatePlan(course, profile) {
    return this.request("/api/plan/generate", {
      method: "POST",
      body: JSON.stringify({ course, profile, use_cache: true }),
    });
  },

  // ---- 课程问答 ----
  chat(question, history, courseContext) {
    return this.request("/api/chat/ask", {
      method: "POST",
      body: JSON.stringify({
        question,
        history: history || [],
        course_context: courseContext || null,
      }),
    });
  },

  // ---- 知识库 ----
  listNotes: () => API.request("/api/knowledge/list"),
  searchNotes: (kw) => API.request("/api/knowledge/search", {
    method: "POST", body: JSON.stringify({ keyword: kw }),
  }),
  addNote: (title, content, tags) => API.request("/api/knowledge/add", {
    method: "POST", body: JSON.stringify({ title, content, tags }),
  }),
  deleteNote: (id) => API.request("/api/knowledge/delete", {
    method: "POST", body: JSON.stringify({ id }),
  }),
  pasteImport: (text, title, tags) => API.request("/api/knowledge/import/paste", {
    method: "POST", body: JSON.stringify({ text, title, tags }),
  }),
  importFile(file) {
    const form = new FormData();
    form.append("file", file);
    return fetch("/api/knowledge/import/file", { method: "POST", body: form })
      .then(async (r) => {
        if (!r.ok) {
          const body = await r.json().catch(() => ({}));
          throw new Error(body.detail || `HTTP ${r.status}`);
        }
        return r.json();
      });
  },

  // ---- 进度 ----
  listCourses: () => API.request("/api/progress/courses"),
  courseDetail: (course) => API.request(`/api/progress/course?course=${encodeURIComponent(course)}`),
  toggle: (course, kind, index, done) => API.request("/api/progress/toggle", {
    method: "POST", body: JSON.stringify({ course, kind, index, done }),
  }),

  // ---- 导出（返回下载 URL，直接 window.open） ----
  exportMd: (course) => `/api/export/markdown?course=${encodeURIComponent(course)}`,
  exportIcs: (course) => `/api/export/ics?course=${encodeURIComponent(course)}`,

  // ---- 截图讲解 ----
  ocrStatus: () => API.request("/api/screenshot/status"),
  explainShot: (text, hint) => API.request("/api/screenshot/explain", {
    method: "POST", body: JSON.stringify({ text, user_hint: hint }),
  }),

  // ---- 设置 / 状态 ----
  health: () => API.request("/api/health"),
  settingsStatus: () => API.request("/api/settings/status"),
};
