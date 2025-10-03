import {
  checkHealth,
  uploadFile,
  fetchObjects,
  requestHeaders,
  requestSpecs,
  exportSpecs,
} from "./api.js";
import {
  state,
  setUpload,
  setObjects,
  setHeaders,
  setSpecs,
  setSectionText,
  updateSettings,
  addLog,
  resetLogs,
  markHeaderProcessed,
} from "./state.js";
import {
  renderHeadersTree,
  renderSidebarHeadersList,
  updateSectionPreview,
  renderSpecsTable,
  setActiveTab,
  updateHealthStatus,
  updateProgress,
  appendLog,
  toggleSettings,
} from "./ui.js";

const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const uploadButton = document.getElementById("upload-button");
const headersTreeEl = document.getElementById("headers-tree");
const sectionPreviewEl = document.getElementById("section-preview");
const sidebarHeadersEl = document.getElementById("sidebar-headers");
const headersCountEl = document.getElementById("headers-count");
const specsTableBody = document.querySelector("#specs-table tbody");
const specsSearch = document.getElementById("specs-search");
const sortSelect = document.getElementById("sort-select");
const tabs = Array.from(document.querySelectorAll(".tab"));
const tabContents = Array.from(document.querySelectorAll(".tab-content"));
const healthIndicator = document.getElementById("health-indicator");
const healthLabel = document.getElementById("health-label");
const progressFill = document.getElementById("progress-fill");
const logConsole = document.getElementById("log-console");
const findHeadersBtn = document.getElementById("find-headers");
const findSpecsBtn = document.getElementById("find-specs");
const exportCsvBtn = document.getElementById("export-csv");
const toggleSettingsBtn = document.getElementById("toggle-settings");
const settingsPanel = document.getElementById("settings-panel");
const settingsForm = document.getElementById("settings-form");

let selectedFile = null;
let activeTab = "headers";
let activeSection = null;

function log(message) {
  addLog(message);
  appendLog(logConsole, message);
}

function clearLog() {
  resetLogs();
  logConsole.textContent = "";
}

function getDocumentLines() {
  const lines = [];
  (state.objects || []).forEach((obj) => {
    if (obj.type === "text") {
      const text = (obj.content || "").trim();
      if (text) lines.push(text);
    } else if (obj.type === "table") {
      const text = (obj.content || "").split(/\r?\n/).map((line) => line.trim());
      text.filter(Boolean).forEach((line) => lines.push(line));
    }
  });
  return lines;
}

function normalize(value) {
  return value.toLowerCase().replace(/\s+/g, " ").trim();
}

function findLineIndex(lines, header) {
  const combo = normalize(`${header.section_number} ${header.section_name}`);
  const number = normalize(header.section_number);
  const name = normalize(header.section_name);
  for (let i = 0; i < lines.length; i += 1) {
    const current = normalize(lines[i]);
    if (current.startsWith(combo)) return i;
  }
  for (let i = 0; i < lines.length; i += 1) {
    const current = normalize(lines[i]);
    if (number && current.startsWith(number) && current.includes(name)) return i;
  }
  for (let i = 0; i < lines.length; i += 1) {
    const current = normalize(lines[i]);
    if (name && current.includes(name)) return i;
  }
  return 0;
}

function computeSectionText(header) {
  const lines = getDocumentLines();
  if (!lines.length) return "";
  const headers = state.headers || [];
  const start = findLineIndex(lines, header);
  let end = lines.length;
  headers.forEach((candidate) => {
    if (candidate.section_number === header.section_number) return;
    const candidateIndex = findLineIndex(lines, candidate);
    if (candidateIndex > start && candidateIndex < end) {
      end = candidateIndex;
    }
  });
  return lines.slice(start, end).join("\n").trim();
}

function getProcessedSections() {
  const processed = new Set();
  state.headerProgress?.forEach((isComplete, section) => {
    if (isComplete) processed.add(section);
  });
  return processed;
}

function selectHeader(header, { refresh = true } = {}) {
  if (!header) return;
  activeSection = header.section_number;
  const preview = state.sectionTexts.get(header.section_number) || computeSectionText(header);
  setSectionText(header.section_number, preview);
  updateSectionPreview(sectionPreviewEl, preview);
  if (refresh) {
    refreshHeaders();
  }
}

function refreshHeaders() {
  const processedSections = getProcessedSections();
  if (!state.headers?.length) {
    activeSection = null;
  }

  renderHeadersTree(headersTreeEl, state.headers, {
    activeSection,
    processedSections,
    onSelect: (header) => selectHeader(header),
  });

  renderSidebarHeadersList(sidebarHeadersEl, state.headers, {
    activeSection,
    processedSections,
    onSelect: (header) => selectHeader(header),
  });

  if (!activeSection) {
    updateSectionPreview(sectionPreviewEl, "Select a header to preview text.");
  }

  headersCountEl.textContent = String(state.headers?.length || 0);
}

function refreshSpecs() {
  renderSpecsTable(specsTableBody, state.specs, {
    searchTerm: specsSearch.value,
    sortKey: sortSelect.value,
  });
}

async function loadObjects(uploadId) {
  const { items } = await fetchObjects(uploadId, 1, 1000);
  setObjects(items);
}

async function handleUpload() {
  if (!selectedFile) {
    log("Please select a file before uploading.");
    return;
  }
  clearLog();
  log(`Uploading ${selectedFile.name}…`);
  updateProgress(progressFill, 10);
  try {
    const response = await uploadFile(selectedFile);
    log(`Parsed ${response.object_count} objects (upload ${response.upload_id}).`);
    await loadObjects(response.upload_id);
    setUpload({ uploadId: response.upload_id, objects: state.objects });
    refreshHeaders();
    updateProgress(progressFill, 40);
    log("Document ready. Proceed with header extraction.");
    updateProgress(progressFill, 50);
  } catch (error) {
    log(`Upload failed: ${error.message}`);
    updateProgress(progressFill, 0);
    throw error;
  }
}

async function handleHeaders() {
  if (!state.uploadId) {
    log("Upload a document before extracting headers.");
    return;
  }
  if (!state.model) {
    log("Please configure a model name in settings.");
    return;
  }
  log("Requesting headers from LLM…");
  updateProgress(progressFill, 60);
  const config = {
    uploadId: state.uploadId,
    provider: state.provider,
    model: state.model,
    params: state.params,
    apiKey: state.apiKey,
    baseUrl: state.baseUrl,
  };
  const startTime = performance.now();
  try {
    const headers = await requestHeaders(config);
    setHeaders(headers);
    headers.forEach((header) => {
      const text = computeSectionText(header);
      if (text) setSectionText(header.section_number, text);
    });
    if (headers.length > 0) {
      selectHeader(headers[0], { refresh: false });
    }
    refreshHeaders();
    updateProgress(progressFill, 75);
    const duration = ((performance.now() - startTime) / 1000).toFixed(1);
    log(`Headers extracted (${headers.length}) in ${duration}s.`);
  } catch (error) {
    log(`Header extraction failed: ${error.message}`);
    updateProgress(progressFill, 50);
  }
}

async function handleSpecs() {
  if (!state.uploadId) {
    log("Upload a document before extracting specifications.");
    return;
  }
  if (!state.headers.length) {
    log("Please run header extraction first.");
    return;
  }
  if (!state.model) {
    log("Please configure a model name in settings.");
    return;
  }
  log("Requesting specifications from LLM…");
  updateProgress(progressFill, 80);
  const config = {
    uploadId: state.uploadId,
    provider: state.provider,
    model: state.model,
    params: state.params,
    apiKey: state.apiKey,
    baseUrl: state.baseUrl,
  };
  const startTime = performance.now();
  try {
    const specs = await requestSpecs(config);
    setSpecs(specs);
    refreshSpecs();
    const processed = new Set();
    specs.forEach((spec) => {
      const sectionNumber = spec.section_number || spec.section;
      const key = sectionNumber ? String(sectionNumber) : null;
      if (key && !processed.has(key)) {
        processed.add(key);
        markHeaderProcessed(key);
      }
    });
    refreshHeaders();
    updateProgress(progressFill, 100);
    const duration = ((performance.now() - startTime) / 1000).toFixed(1);
    log(`Specifications extracted (${specs.length}) in ${duration}s.`);
  } catch (error) {
    log(`Specification extraction failed: ${error.message}`);
    updateProgress(progressFill, 80);
  }
}

async function handleExport() {
  if (!state.uploadId) {
    log("Upload a document before exporting.");
    return;
  }
  try {
    const blob = await exportSpecs(state.uploadId);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "specs.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    log("Specifications CSV downloaded.");
  } catch (error) {
    log(`Export failed: ${error.message}`);
  }
}

function handleFileSelection(file) {
  if (!file) return;
  const allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
  if (!allowed.some((type) => file.type === type || file.name.endsWith(".pdf") || file.name.endsWith(".docx") || file.name.endsWith(".txt"))) {
    log("Unsupported file type. Please upload PDF, DOCX, or TXT.");
    return;
  }
  selectedFile = file;
  log(`Selected file: ${file.name}`);
}

function setupDragAndDrop() {
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("dragging");
    });
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.remove("dragging");
    });
  });
  dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      handleFileSelection(file);
    }
  });
}

function setupTabs() {
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      activeTab = tab.dataset.tab;
      setActiveTab(tabs, tabContents, activeTab);
      if (activeTab === "specs") {
        refreshSpecs();
      }
    });
  });
}

function setupSettingsForm() {
  function syncProviderFields(provider) {
    document
      .querySelectorAll(".provider-group")
      .forEach((group) => group.classList.toggle("hidden", group.dataset.provider !== provider));
  }

  settingsForm.addEventListener("input", () => {
    const formData = new FormData(settingsForm);
    const provider = formData.get("provider") || "openrouter";
    const model = (formData.get("model") || "").toString();
    const temperature = Number(formData.get("temperature")) || 0;
    const maxTokens = Number(formData.get("max_tokens")) || 512;
    const apiKey = (formData.get("api_key") || "").toString();
    const baseUrl = (formData.get("base_url") || "").toString();
    updateSettings({ provider, model, temperature, maxTokens, apiKey, baseUrl });
    syncProviderFields(provider);
  });
  const defaultProvider = settingsForm.querySelector("input[name=provider]:checked")?.value || "openrouter";
  syncProviderFields(defaultProvider);
  const initialData = new FormData(settingsForm);
  updateSettings({
    provider: initialData.get("provider") || "openrouter",
    model: (initialData.get("model") || "").toString(),
    temperature: Number(initialData.get("temperature")) || 0.2,
    maxTokens: Number(initialData.get("max_tokens")) || 512,
    apiKey: (initialData.get("api_key") || "").toString(),
    baseUrl: (initialData.get("base_url") || "").toString(),
  });
}

function setupSearchControls() {
  specsSearch.addEventListener("input", refreshSpecs);
  sortSelect.addEventListener("change", refreshSpecs);
}

async function pollHealth() {
  try {
    const data = await checkHealth();
    updateHealthStatus(healthIndicator, healthLabel, data.status);
  } catch (error) {
    updateHealthStatus(healthIndicator, healthLabel, "error");
    log(`Health check failed: ${error.message}`);
  }
}

function initialize() {
  setupDragAndDrop();
  setupTabs();
  setupSettingsForm();
  setupSearchControls();
  toggleSettingsBtn.addEventListener("click", () => toggleSettings(settingsPanel));

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) handleFileSelection(file);
  });

  uploadButton.addEventListener("click", () => {
    handleUpload().catch(() => undefined);
  });

  findHeadersBtn.addEventListener("click", () => {
    handleHeaders().catch(() => undefined);
  });

  findSpecsBtn.addEventListener("click", () => {
    handleSpecs().catch(() => undefined);
  });

  exportCsvBtn.addEventListener("click", () => {
    handleExport().catch(() => undefined);
  });

  refreshHeaders();
  pollHealth();
  setInterval(pollHealth, 10000);
}

initialize();
