// app.js — 页面逻辑：Tab 切换 / 方案生成 / 问答 / 知识库 / 进度 / 截图讲解

// ================= Tab 切换 =================
function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".panel").forEach((p) =>
    p.classList.toggle("active", p.id === `tab-${name}`));
  // 惰性加载
  if (name === "knowledge") loadNotes();
  if (name === "progress") loadProgress();
}

// ================= 主题 =================
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  document.getElementById("theme-toggle").textContent = theme === "dark" ? "☀️" : "🌙";
}
function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
}

// ================= 顶栏模式角标 =================
async function refreshModeBadge() {
  const el = document.getElementById("mode-badge");
  try {
    const s = await API.settingsStatus();
    el.textContent = s.mode === "mock" ? "📦 Mock 离线模式" : `⚡ ${s.mode_label}`;
    el.className = "badge " + s.mode;
  } catch (e) {
    el.textContent = "⚠ 后端未连接";
    el.className = "badge";
  }
}

// ================= Tab 1: 方案生成 =================
async function generatePlan() {
  const course = document.getElementById("course-input").value.trim();
  const status = document.getElementById("plan-status");
  const resultBox = document.getElementById("plan-result");
  const btn = document.getElementById("generate-btn");

  if (!course) { status.className = "status warn"; status.textContent = "请输入课程名"; return; }

  const profile = {
    level: document.getElementById("pf-level").value,
    daily_hours: document.getElementById("pf-hours").value,
    goal: document.getElementById("pf-goal").value,
    deadline: document.getElementById("pf-deadline").value || "",
  };

  btn.disabled = true;
  status.className = "status";
  status.textContent = "🤖 Planner → Searcher → Writer → Reviewer 流水线运行中，请稍候…";
  resultBox.classList.add("hidden");

  try {
    const result = await API.generatePlan(course, profile);
    renderPlanResult(course, result);
    status.className = "status ok";
    status.textContent = result._from_cache
      ? "⚡ 命中缓存（同课程同画像不重复消耗 API）"
      : `✅ 生成完成：${(result.outline || []).length} 章 · ${(result.plan || []).length} 天`;
    if (result._degraded) {
      status.className = "status warn";
      status.textContent = `⚠ LLM 不可用，本次为内置模板方案：${result._degraded.error}`;
    }
  } catch (e) {
    status.className = "status warn";
    status.textContent = `生成失败：${e.message}`;
  } finally {
    btn.disabled = false;
  }
}

function renderPlanResult(course, result) {
  const box = document.getElementById("plan-result");
  const outline = result.outline || [];
  const resources = result.resources || [];
  const plan = result.plan || [];

  const outlineHtml = outline.map((ch, i) => {
    const title = (ch && (ch.title || ch.name)) || `第 ${i + 1} 章`;
    const points = (ch && (ch.points || ch.items)) || [];
    return `<div class="outline-item"><b>${title}</b>${points.length ? "<br>" + points.map((p) => `· ${p}`).join("<br>") : ""}</div>`;
  }).join("");

  const resHtml = resources.map((r) => {
    const t = (r && r.title) || "(未命名)";
    const url = (r && r.url) || "";
    const type = (r && r.type) || "—";
    return `<div class="resource-item">${t} <small>[${type}]</small>${url ? ` — <a href="${url}" target="_blank" rel="noopener">${url}</a>` : ""}</div>`;
  }).join("");

  const planHtml = plan.map((day, i) => {
    let title = `Day ${i + 1}`, tasks = [], chapters = [];
    if (typeof day === "string") {
      const m = day.match(/^第?(\d+)?天?[：:]?(.*)$/);
      title = (m && m[2]) ? m[2] : day;
      tasks = [title];
    } else if (day && typeof day === "object") {
      title = day.title || `Day ${i + 1}`;
      tasks = day.tasks || [];
      chapters = day.chapters || [];
    }
    return `<div class="day-card">
      <div class="day-title">Day ${i + 1} · ${title}</div>
      ${chapters.length ? `<div class="day-chapters">关联章节：${chapters.join(" / ")}</div>` : ""}
      ${tasks.map((t) => `<div class="day-task">☐ ${t}</div>`).join("")}
    </div>`;
  }).join("");

  box.innerHTML = `
    <div class="plan-section"><h3>📑 课程大纲</h3>${outlineHtml || "（空）"}</div>
    <div class="plan-section"><h3>🔗 推荐资源</h3>${resHtml || "（空）"}</div>
    <div class="plan-section"><h3>📅 学习计划（${plan.length} 天）</h3>${planHtml || "（空）"}</div>
    <div class="form-row" style="margin-top:16px">
      <button class="ghost-btn" onclick="window.open('${API.exportMd(course)}')">📄 导出 Markdown</button>
      <button class="ghost-btn" onclick="window.open('${API.exportIcs(course)}')">📅 导出学习日历 (.ics)</button>
      <button class="ghost-btn" onclick="switchTab('progress')">✅ 去勾选进度</button>
    </div>`;
  box.classList.remove("hidden");
}

// ================= Tab 2: 课程问答 =================
let chatHistory = [];

async function sendChat() {
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question) return;

  appendMsg("user", question);
  input.value = "";

  const log = document.getElementById("chat-log");
  log.appendChild(botThinking());

  try {
    const result = await API.chat(question, chatHistory, null);
    log.querySelector(".thinking")?.remove();
    appendMsg("bot", result.answer, result.source);
    chatHistory.push({ role: "user", content: question });
    chatHistory.push({ role: "assistant", content: result.answer });
    if (chatHistory.length > 16) chatHistory = chatHistory.slice(-16); // 后端只取最近 8 条
  } catch (e) {
    log.querySelector(".thinking")?.remove();
    appendMsg("bot", `出错了：${e.message}`);
  }
}

function appendMsg(role, text, source) {
  const log = document.getElementById("chat-log");
  const empty = log.querySelector(".chat-empty");
  if (empty) empty.remove();
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  if (source === "knowledge") {
    const chip = document.createElement("span");
    chip.className = "src-chip";
    chip.textContent = "📚 命中知识库";
    div.appendChild(document.createElement("br"));
    div.appendChild(chip);
  } else if (source === "llm") {
    const chip = document.createElement("span");
    chip.className = "src-chip";
    chip.textContent = "🤖 AI 生成";
    div.appendChild(document.createElement("br"));
    div.appendChild(chip);
  }
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function botThinking() {
  const div = document.createElement("div");
  div.className = "msg bot thinking";
  div.textContent = "思考中…";
  return div;
}

// ================= Tab 3: 知识库 =================
async function loadNotes(keyword) {
  const list = document.getElementById("kb-list");
  list.innerHTML = "<p class='hint'>加载中…</p>";
  try {
    const notes = keyword
      ? await API.searchNotes(keyword)
      : await API.listNotes();
    if (!notes.length) { list.innerHTML = "<p class='hint'>暂无笔记，点右上角新增或导入</p>"; return; }
    list.innerHTML = notes.map((n) => `
      <div class="note-item">
        <div class="note-head">
          <span class="note-title">${esc(n.title)}</span>
          <button class="del-btn" onclick="removeNote(${n.id})">删除</button>
        </div>
        <div class="note-content">${esc(n.content).slice(0, 300)}${n.content.length > 300 ? "…" : ""}</div>
        <div>${(n.tags || []).map((t) => `<span class="tag-chip">${esc(t)}</span>`).join("")}</div>
      </div>`).join("");
  } catch (e) {
    list.innerHTML = `<p class="status warn">加载失败：${esc(e.message)}</p>`;
  }
}

function searchNotes() {
  const kw = document.getElementById("kb-search").value.trim();
  loadNotes(kw || null);
}

async function removeNote(id) {
  if (!confirm("确认删除这条笔记？")) return;
  try { await API.deleteNote(id); loadNotes(); } catch (e) { alert(e.message); }
}

function showAddNote() {
  const title = prompt("笔记标题：");
  if (!title) return;
  const content = prompt("笔记内容：");
  if (!content) return;
  API.addNote(title, content, []).then(() => loadNotes()).catch((e) => alert(e.message));
}

function showPasteImport() {
  const text = prompt("粘贴要导入的文本：");
  if (!text) return;
  API.pasteImport(text, null, []).then((r) => {
    alert(`导入成功（笔记 #${r.id}）`);
    loadNotes();
  }).catch((e) => alert(e.message));
}

function importFile(input) {
  const file = input.files[0];
  if (!file) return;
  API.importFile(file).then((r) => {
    alert(`导入成功：${r.filename || file.name}`);
    loadNotes();
  }).catch((e) => alert(e.message)).finally(() => { input.value = ""; });
}

// ================= Tab 4: 进度 =================
async function loadProgress() {
  const list = document.getElementById("progress-list");
  list.innerHTML = "<p class='hint'>加载中…</p>";
  try {
    const courses = await API.listCourses();
    if (!courses.length) { list.innerHTML = "<p class='hint'>还没有生成过方案，去「生成方案」试试</p>"; return; }
    const rows = await Promise.all(courses.map(async (c) => {
      try {
        const d = await API.courseDetail(c.course);
        const pct = Math.round((d.stats.ratio || 0) * 100);
        return `<div class="course-row" onclick="openProgress('${esc(c.course)}')">
          <b>${esc(c.course)}</b>
          <div class="progress-bar"><div class="fill" style="width:${pct}%"></div></div>
          <small>${d.stats.done}/${d.stats.total} (${pct}%)</small>
        </div>`;
      } catch (_) {
        return `<div class="course-row" onclick="openProgress('${esc(c.course)}')"><b>${esc(c.course)}</b><small>—</small></div>`;
      }
    }));
    list.innerHTML = rows.join("");
  } catch (e) {
    list.innerHTML = `<p class="status warn">加载失败：${esc(e.message)}</p>`;
  }
}

async function openProgress(course) {
  const box = document.getElementById("progress-detail");
  box.classList.add("hidden");
  try {
    const d = await API.courseDetail(course);
    const renderList = (kind, items) => items.map((it, i) => `
      <label class="check-item ${it.done ? "done" : ""}">
        <input type="checkbox" ${it.done ? "checked" : ""}
               onchange="toggleItem('${esc(course)}','${kind}',${i},this.checked)">
        <span class="text">${esc(it.title)}</span>
      </label>`).join("");
    box.innerHTML = `
      <h2>${esc(course)}</h2>
      <p class="hint">已完成 ${d.stats.done}/${d.stats.total} 项</p>
      <div class="plan-section"><h3>📑 大纲掌握</h3>${renderList("outline", d.progress.outline)}</div>
      <div class="plan-section"><h3>📅 每日计划</h3>${renderList("plan", d.progress.plan)}</div>
      <div class="form-row" style="margin-top:14px">
        <button class="ghost-btn" onclick="window.open('${API.exportMd(course)}')">📄 导出 Markdown</button>
        <button class="ghost-btn" onclick="window.open('${API.exportIcs(course)}')">📅 导出日历</button>
      </div>`;
    box.classList.remove("hidden");
  } catch (e) { alert(e.message); }
}

async function toggleItem(course, kind, index, done) {
  try {
    await API.toggle(course, kind, index, done);
    openProgress(course);   // 重新渲染进度条
    loadProgress();
  } catch (e) { alert(e.message); }
}

// ================= Tab 5: 截图讲解 =================
async function explainScreenshot() {
  const text = document.getElementById("shot-text").value.trim();
  const hint = document.getElementById("shot-hint-input").value.trim();
  const resultBox = document.getElementById("shot-result");
  if (!text) { alert("请先粘贴截图中的文字"); return; }

  resultBox.classList.remove("hidden");
  resultBox.textContent = "🤖 AI 助教思考中…";
  try {
    const r = await API.explainShot(text, hint);
    resultBox.textContent = r.answer;
  } catch (e) {
    resultBox.textContent = `讲解失败：${e.message}`;
  }
}

// ================= 工具 =================
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// ================= 初始化 =================
window.addEventListener("DOMContentLoaded", () => {
  applyTheme(localStorage.getItem("theme") || "light");
  applyI18n();
  refreshModeBadge();
});
