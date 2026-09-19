// i18n.js — 前端中英双语（复用桌面版 i18n 文案表思路）

const I18N = {
  zh: {
    plan_title: "想学什么？",
    plan_hint: "输入课程名，多智能体为你定制个性化学习方案",
    plan_placeholder: "例如：高等数学 / 大学物理 / Python 深度学习",
    plan_btn: "生成方案",
    plan_profile: "⚙ 个性化设置（水平 / 时长 / 目标 / 截止日）",
    plan_level: "水平", plan_hours: "每日时长", plan_goal: "目标", plan_deadline: "截止日",
    chat_empty: "向学习助手提问吧 —— 知识库里的笔记会优先作答",
    chat_placeholder: "例如：二重积分 / 反向传播 / 不确定度",
    chat_send: "发送",
    kb_search: "搜索", kb_add: "＋ 新增", kb_paste: "📥 粘贴导入",
    prog_title: "历史课程与进度",
    shot_title: "📷 截图讲解",
    shot_placeholder: "把截图里的文字粘贴到这里（公式用文字描述，如 x^2 + y^2）",
    shot_btn: "让 AI 讲解",
  },
  en: {
    plan_title: "What do you want to learn?",
    plan_hint: "Enter a course name — multi-agent pipeline crafts a personalized plan",
    plan_placeholder: "e.g. Calculus / College Physics / Deep Learning with Python",
    plan_btn: "Generate Plan",
    plan_profile: "⚙ Personalization (level / hours / goal / deadline)",
    plan_level: "Level", plan_hours: "Daily hours", plan_goal: "Goal", plan_deadline: "Deadline",
    chat_empty: "Ask away — your knowledge base notes answer first",
    chat_placeholder: "e.g. double integral / backpropagation / uncertainty",
    chat_send: "Send",
    kb_search: "Search", kb_add: "＋ New", kb_paste: "📥 Paste import",
    prog_title: "Courses & Progress",
    shot_title: "📷 Screenshot Explainer",
    shot_placeholder: "Paste text from your screenshot here (describe formulas, e.g. x^2 + y^2)",
    shot_btn: "Explain with AI",
  },
};

let currentLang = localStorage.getItem("lang") || "zh";

function applyI18n() {
  const dict = I18N[currentLang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const key = el.getAttribute("data-i18n-ph");
    if (dict[key]) el.placeholder = dict[key];
  });
  document.getElementById("lang-toggle").textContent =
    currentLang === "zh" ? "🌐 EN" : "🌐 中文";
}

function toggleLang() {
  currentLang = currentLang === "zh" ? "en" : "zh";
  localStorage.setItem("lang", currentLang);
  applyI18n();
}
