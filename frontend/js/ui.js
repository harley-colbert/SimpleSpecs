const ROW_HEIGHT = 72;

export function initializeVirtualList(container) {
  container.innerHTML = "";
  const inner = document.createElement("div");
  inner.className = "virtual-list-inner";
  container.appendChild(inner);

  let items = [];

  function render() {
    const totalHeight = items.length * ROW_HEIGHT;
    inner.style.height = `${totalHeight}px`;
    const scrollTop = container.scrollTop;
    const viewportHeight = container.clientHeight;
    const startIndex = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - 5);
    const endIndex = Math.min(items.length, Math.ceil((scrollTop + viewportHeight) / ROW_HEIGHT) + 5);

    inner.innerHTML = "";
    for (let index = startIndex; index < endIndex; index += 1) {
      const item = items[index];
      const row = document.createElement("div");
      row.className = "virtual-row";
      row.style.top = `${index * ROW_HEIGHT}px`;
      const badge = document.createElement("span");
      badge.className = "type-badge";
      badge.textContent = item.type;
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.appendChild(badge);
      const page = document.createElement("span");
      page.textContent = item.page ? `Page ${item.page}` : "Page N/A";
      meta.appendChild(page);

      const content = document.createElement("div");
      content.className = "content";
      content.textContent = item.content;

      row.appendChild(meta);
      row.appendChild(content);
      inner.appendChild(row);
    }
  }

  container.addEventListener("scroll", render);

  return {
    setItems(newItems) {
      items = Array.isArray(newItems) ? newItems : [];
      container.scrollTop = 0;
      render();
    },
  };
}

export function updateObjectCount(element, count) {
  element.textContent = String(count);
}

function buildTree(headers) {
  const root = {};
  headers.forEach((header) => {
    const parts = header.section_number.split(".");
    let node = root;
    parts.forEach((part, index) => {
      node.children = node.children || new Map();
      if (!node.children.has(part)) {
        node.children.set(part, { children: new Map() });
      }
      node = node.children.get(part);
      if (index === parts.length - 1) {
        node.header = header;
      }
    });
  });
  return root;
}

function renderTreeNode(node, activeSection, onSelect) {
  if (!node.children) return document.createDocumentFragment();
  const ul = document.createElement("ul");
  const entries = Array.from(node.children.entries()).sort((a, b) => a[0].localeCompare(b[0], undefined, { numeric: true }));
  entries.forEach(([, child]) => {
    const li = document.createElement("li");
    if (child.header) {
      li.textContent = `${child.header.section_number} ${child.header.section_name}`;
      li.dataset.section = child.header.section_number;
      if (activeSection === child.header.section_number) {
        li.classList.add("active");
      }
      li.addEventListener("click", () => onSelect?.(child.header));
    }
    if (child.children && child.children.size > 0) {
      li.appendChild(renderTreeNode(child, activeSection, onSelect));
    }
    ul.appendChild(li);
  });
  return ul;
}

export function renderHeadersTree(container, headers, { onSelect, activeSection } = {}) {
  container.innerHTML = "";
  if (!headers?.length) {
    container.textContent = "No headers extracted yet.";
    return;
  }
  const tree = buildTree(headers);
  const fragment = renderTreeNode(tree, activeSection, onSelect);
  container.appendChild(fragment);
}

export function updateSectionPreview(element, text) {
  element.textContent = text || "No preview available.";
}

function normalize(value) {
  return value.toLowerCase();
}

export function renderSpecsTable(tableBody, specs, { searchTerm = "", sortKey = "section_number" } = {}) {
  tableBody.innerHTML = "";
  let rows = Array.isArray(specs) ? [...specs] : [];
  if (searchTerm) {
    const term = searchTerm.toLowerCase();
    rows = rows.filter((row) =>
      [row.section_number, row.section_name, row.specification, row.domain]
        .join(" ")
        .toLowerCase()
        .includes(term),
    );
  }
  rows.sort((a, b) => {
    const left = normalize(String(a[sortKey] || ""));
    const right = normalize(String(b[sortKey] || ""));
    return left.localeCompare(right, undefined, { numeric: true });
  });

  const fragment = document.createDocumentFragment();
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [row.section_number, row.section_name, row.specification, row.domain].forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    });
    fragment.appendChild(tr);
  });
  tableBody.appendChild(fragment);
}

export function setActiveTab(tabs, contents, active) {
  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === active);
  });
  contents.forEach((section) => {
    section.classList.toggle("hidden", section.id !== `tab-${active}`);
  });
}

export function updateHealthStatus(indicator, label, status) {
  indicator.classList.remove("status-online", "status-offline", "status-warning");
  if (status === "ok") {
    indicator.classList.add("status-online");
    label.textContent = "Healthy";
  } else if (status === "degraded") {
    indicator.classList.add("status-warning");
    label.textContent = "Degraded";
  } else {
    indicator.classList.add("status-offline");
    label.textContent = "Offline";
  }
}

export function updateProgress(fill, percent) {
  fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
}

export function appendLog(consoleEl, message) {
  const timestamp = new Date().toLocaleTimeString();
  consoleEl.textContent += `[${timestamp}] ${message}\n`;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

export function toggleSettings(panel) {
  panel.classList.toggle("hidden");
}
