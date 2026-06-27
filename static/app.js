const form = document.getElementById("query-form");
const wordInput = document.getElementById("word-input");
const modelInput = document.getElementById("model-input");
const forceRefreshInput = document.getElementById("force-refresh");
const submitButton = document.getElementById("submit-button");
const resultTitle = document.getElementById("result-title");
const resultContent = document.getElementById("result-content");
const errorBox = document.getElementById("error-box");
const statusChip = document.getElementById("status-chip");
const recentArchives = document.getElementById("recent-archives");

const metaModel = document.getElementById("meta-model");
const metaCreatedAt = document.getElementById("meta-created-at");
const metaCache = document.getElementById("meta-cache");
const metaArchive = document.getElementById("meta-archive");

const refreshArchivesButton = document.getElementById("refresh-archives");

function setStatus(type, label) {
  statusChip.className = `status-chip ${type}`;
  statusChip.textContent = label;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
  setStatus("error", "Error");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", { hour12: false });
}

function renderResult(data) {
  resultTitle.textContent = data.display_word;
  resultContent.classList.remove("empty");
  resultContent.innerHTML = data.html_output;
  metaModel.textContent = data.model || "—";
  metaCreatedAt.textContent = formatDate(data.created_at);
  metaCache.textContent = data.from_cache ? "命中缓存" : `新生成（${data.duration_ms} ms）`;
  metaArchive.textContent = data.archive_path || "—";
  setStatus("success", data.from_cache ? "Cached" : "Generated");
}

async function loadArchives() {
  const response = await fetch("/api/archives");
  const items = await response.json();
  recentArchives.innerHTML = "";

  if (!items.length) {
    recentArchives.innerHTML = `<div class="recent-item"><div class="recent-meta">还没有归档记录。</div></div>`;
    return;
  }

  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "recent-item";
    button.innerHTML = `
      <div class="recent-word">${item.display_word}</div>
      <div class="recent-meta">${item.model}</div>
      <div class="recent-meta">${formatDate(item.created_at)}</div>
    `;
    button.addEventListener("click", async () => {
      wordInput.value = item.word;
      forceRefreshInput.checked = false;
      await submitQuery();
    });
    recentArchives.appendChild(button);
  }
}

async function loadConfig() {
  const response = await fetch("/api/config");
  const config = await response.json();
  modelInput.value = config.default_model || "";
  await loadArchives();
}

async function submitQuery(event) {
  if (event) event.preventDefault();
  clearError();

  const word = wordInput.value.trim();
  if (!word) {
    showError("请输入要解析的英文单词。");
    return;
  }

  submitButton.disabled = true;
  setStatus("loading", "Working");
  resultTitle.textContent = `解析中：${word}`;

  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        word,
        model: modelInput.value.trim(),
        force_refresh: forceRefreshInput.checked,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "请求失败。");
    }

    renderResult(data);
    await loadArchives();
  } catch (error) {
    showError(error.message || "发生未知错误。");
  } finally {
    submitButton.disabled = false;
  }
}

form.addEventListener("submit", submitQuery);
refreshArchivesButton.addEventListener("click", loadArchives);

loadConfig().catch((error) => {
  showError(error.message || "初始化失败。");
});
