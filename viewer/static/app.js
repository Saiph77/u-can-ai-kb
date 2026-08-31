const MIN_PAGE_SIZE = 6;
const MAX_PAGE_SIZE = 14;
const EST_ITEM_HEIGHT = 108;

const state = {
  offset: 0,
  total: 0,
  items: [],
  selectedId: null,
  showRaw: false,
  pageSize: 10,
  collections: [],
};

const els = {
  statsBar: document.getElementById("statsBar"),
  collectionFilter: document.getElementById("collectionFilter"),
  categoryField: document.getElementById("categoryField"),
  categoryFilter: document.getElementById("categoryFilter"),
  collectionHint: document.getElementById("collectionHint"),
  searchInput: document.getElementById("searchInput"),
  applyFiltersBtn: document.getElementById("applyFiltersBtn"),
  itemList: document.getElementById("itemList"),
  listCount: document.getElementById("listCount"),
  pageInfo: document.getElementById("pageInfo"),
  prevPageBtn: document.getElementById("prevPageBtn"),
  nextPageBtn: document.getElementById("nextPageBtn"),
  reloadBtn: document.getElementById("reloadBtn"),
  emptyState: document.getElementById("emptyState"),
  detailView: document.getElementById("detailView"),
  detailBadges: document.getElementById("detailBadges"),
  detailTitle: document.getElementById("detailTitle"),
  detailMeta: document.getElementById("detailMeta"),
  contentHtml: document.getElementById("contentHtml"),
  contentRaw: document.getElementById("contentRaw"),
  toggleRawBtn: document.getElementById("toggleRawBtn"),
};

marked.setOptions({ gfm: true, breaks: true });

function badge(text, className = "") {
  const span = document.createElement("span");
  span.className = `badge ${className}`.trim();
  span.textContent = text;
  return span;
}

function computePageSize() {
  const list = document.querySelector(".item-list");
  if (!list) return 10;
  const available = list.clientHeight || window.innerHeight - 320;
  return Math.max(MIN_PAGE_SIZE, Math.min(MAX_PAGE_SIZE, Math.floor(available / EST_ITEM_HEIGHT)));
}

function currentFilters() {
  return {
    collection: els.collectionFilter.value,
    category: els.categoryFilter.value,
    q: els.searchInput.value.trim(),
  };
}

function renderStats(meta) {
  els.statsBar.innerHTML = "";
  const total = document.createElement("div");
  total.className = "stat";
  total.innerHTML = `<span class="label">总篇数</span><span class="value">${meta.total}</span>`;
  els.statsBar.appendChild(total);
  for (const col of meta.collections.filter((c) => c.count > 0).slice(0, 5)) {
    const el = document.createElement("div");
    el.className = "stat";
    el.innerHTML = `<span class="label">${col.label}</span><span class="value">${col.count}</span>`;
    els.statsBar.appendChild(el);
  }
}

function fillCollectionOptions(meta) {
  els.collectionFilter.innerHTML = "";
  for (const col of meta.collections) {
    if (col.count === 0 && col.id !== "guides") continue;
    const opt = document.createElement("option");
    opt.value = col.id;
    opt.textContent = `${col.label} (${col.count})`;
    els.collectionFilter.appendChild(opt);
  }
  state.collections = meta.collections;
  updateCategoryOptions();
}

function updateCategoryOptions() {
  const colId = els.collectionFilter.value;
  const col = state.collections.find((c) => c.id === colId);
  els.categoryFilter.innerHTML = '<option value="">全部</option>';
  const hasCats = col && col.categories && col.categories.length > 0;
  els.categoryField.classList.toggle("hidden", !hasCats);
  if (hasCats) {
    for (const cat of col.categories) {
      const opt = document.createElement("option");
      opt.value = cat.id;
      opt.textContent = cat.label;
      els.categoryFilter.appendChild(opt);
    }
  }
  els.collectionHint.textContent = col?.desc || "";
}

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderList() {
  els.itemList.innerHTML = "";
  if (!state.items.length) {
    const li = document.createElement("li");
    li.className = "muted";
    li.style.padding = "16px";
    li.textContent = "没有匹配的条目";
    els.itemList.appendChild(li);
    return;
  }
  for (const item of state.items) {
    const li = document.createElement("li");
    li.className = `item-card${item.id === state.selectedId ? " active" : ""}`;
    li.dataset.id = item.id;
    const h3 = document.createElement("h3");
    h3.textContent = item.title;
    const badges = document.createElement("div");
    badges.className = "badges";
    badges.appendChild(badge(item.collection_label, "library"));
    if (item.category_label) badges.appendChild(badge(item.category_label, "type"));
    const meta = document.createElement("div");
    meta.className = "meta-line";
    meta.textContent = item.path;
    li.append(h3, badges, meta);
    li.addEventListener("click", () => selectItem(item.id));
    els.itemList.appendChild(li);
  }
}

function updatePagination() {
  const page = Math.floor(state.offset / state.pageSize) + 1;
  const pages = Math.max(1, Math.ceil(state.total / state.pageSize));
  els.pageInfo.textContent = `第 ${page} / ${pages} 页`;
  els.listCount.textContent = `${state.total} 篇`;
  els.prevPageBtn.disabled = state.offset <= 0;
  els.nextPageBtn.disabled = state.offset + state.pageSize >= state.total;
}

async function loadItems(keepSelection = false) {
  const f = currentFilters();
  const params = new URLSearchParams({
    limit: String(state.pageSize),
    offset: String(state.offset),
    q: f.q,
  });
  if (f.collection) params.set("collection", f.collection);
  if (f.category) params.set("category", f.category);
  const data = await api(`/api/items?${params}`);
  state.total = data.total;
  state.items = data.items;
  if (!keepSelection || !state.items.some((i) => i.id === state.selectedId)) {
    state.selectedId = state.items[0]?.id || null;
  }
  els.itemList.scrollTop = 0;
  renderList();
  updatePagination();
  if (state.selectedId) await renderDetail(state.selectedId);
  else showEmpty();
}

function showEmpty() {
  els.emptyState.classList.remove("hidden");
  els.detailView.classList.add("hidden");
}

async function renderDetail(id) {
  const data = await api(`/api/content?id=${encodeURIComponent(id)}`);
  state.selectedId = id;
  renderList();
  els.emptyState.classList.add("hidden");
  els.detailView.classList.remove("hidden");
  els.detailTitle.textContent = data.title;
  els.detailBadges.innerHTML = "";
  els.detailBadges.appendChild(badge(data.collection_label, "library"));
  if (data.category_label) els.detailBadges.appendChild(badge(data.category_label, "type"));
  els.detailMeta.innerHTML = `<div><strong>路径</strong> ${data.path}</div>`;
  els.contentRaw.textContent = data.raw;
  const html = DOMPurify.sanitize(marked.parse(data.body || data.raw));
  els.contentHtml.innerHTML = html;
  els.contentHtml.classList.toggle("hidden", state.showRaw);
  els.contentRaw.classList.toggle("hidden", !state.showRaw);
  els.toggleRawBtn.textContent = state.showRaw ? "渲染预览" : "Markdown 原文";
}

async function selectItem(id) {
  state.showRaw = false;
  await renderDetail(id);
}

function applyFilters() {
  state.offset = 0;
  loadItems();
}

async function bootstrap() {
  state.pageSize = computePageSize();
  const meta = await api("/api/meta");
  renderStats(meta);
  fillCollectionOptions(meta);
  if (!els.collectionFilter.value && meta.collections.length) {
    els.collectionFilter.value = meta.collections.find((c) => c.id === "by-audience")?.id || meta.collections[0].id;
    updateCategoryOptions();
  }
  await loadItems();
}

els.applyFiltersBtn.addEventListener("click", applyFilters);
els.searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") applyFilters();
});
els.collectionFilter.addEventListener("change", () => {
  els.categoryFilter.value = "";
  updateCategoryOptions();
  applyFilters();
});
els.categoryFilter.addEventListener("change", applyFilters);
els.prevPageBtn.addEventListener("click", () => {
  state.offset = Math.max(0, state.offset - state.pageSize);
  loadItems(true);
});
els.nextPageBtn.addEventListener("click", () => {
  if (state.offset + state.pageSize < state.total) {
    state.offset += state.pageSize;
    loadItems(true);
  }
});
els.reloadBtn.addEventListener("click", async () => {
  await api("/api/reload");
  const meta = await api("/api/meta");
  renderStats(meta);
  fillCollectionOptions(meta);
  applyFilters();
});
els.toggleRawBtn.addEventListener("click", () => {
  state.showRaw = !state.showRaw;
  els.contentHtml.classList.toggle("hidden", state.showRaw);
  els.contentRaw.classList.toggle("hidden", !state.showRaw);
  els.toggleRawBtn.textContent = state.showRaw ? "渲染预览" : "Markdown 原文";
});
window.addEventListener("resize", () => {
  const next = computePageSize();
  if (next !== state.pageSize) {
    state.pageSize = next;
    state.offset = 0;
    loadItems(true);
  }
});

bootstrap().catch((err) => {
  console.error(err);
  els.itemList.innerHTML = `<li class="muted" style="padding:16px">加载失败：${err.message}</li>`;
});
