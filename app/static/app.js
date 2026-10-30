// Beyin Çalışsın — tek akış: fotoğraf yükle → beyin → adayları seç → PDF
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const api = async (url, opt = {}) => {
  const r = await fetch(url, opt.body && !(opt.body instanceof FormData)
    ? { ...opt, headers: { "Content-Type": "application/json" }, body: JSON.stringify(opt.body) } : opt);
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).detail || m; } catch {} throw new Error(m); }
  return r.json();
};
const store = { get: (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} } };
const fileUrl = (p) => "/api/file?path=" + encodeURIComponent(p);
const cropUrl = (q) => "/api/crop?qid=" + encodeURIComponent(q);
const toast = (m, ms = 2600) => { const t = $("#toast"); t.textContent = m; t.classList.remove("hidden"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.add("hidden"), ms); };
const modal = (html) => { $("#modalContent").innerHTML = html; $("#modal").classList.remove("hidden"); };
$$(".modal").forEach((m) => m.addEventListener("click", (e) => { if (e.target === m || e.target.classList.contains("close")) m.classList.add("hidden"); }));

const ROLE = { hatirlatici: "Öğretici", pekistirme: "Pekiştirme", zorlayici: "Zorlayıcı" };
const ROLE_ORDER = { hatirlatici: 0, pekistirme: 1, zorlayici: 2 };
const STATUSES = ["Yapamadı", "Yanlış"];
const statusTr = (s) => ({ running: "düşünüyor…", done: "tamamlandı", error: "hata", cancelled: "durduruldu" }[s] || s);
const when = (iso) => (iso || "").replace("T", " ").slice(0, 16);

// photos: yüklenen fotoğraflar [{path, status}] — sayfa yenilense de kalsın
// basket: seçilen sorular (qid → öğe), her beyin çalışması için ayrı saklanır
const S = { state: null, photos: store.get("photos", []), job: null, running: false, since: 0, poll: null, cand: null, runId: "",
  runImages: [], basket: new Map(), hidden: new Set() };
const savePhotos = () => { store.set("photos", S.photos); renderPhotos(); };
function loadBasket() { S.basket = new Map(store.get("basket:" + S.runId, []).map((x) => [x.qid, x])); return S.basket.size > 0; }
const saveBasket = () => { store.set("basket:" + S.runId, [...S.basket.values()]); renderBar(); };

// ------------------------------------------------------------------ durum + ayarlar
async function loadState() {
  S.state = await api("/api/state");
  const c = S.state.config;
  $("#student").textContent = "· " + c.student_name + (S.state.version ? ` · v${S.state.version}` : "");
  const st = $("#claudeStatus");
  const login = S.state.claude && S.state.claude_login === false;
  st.className = "status" + (S.state.claude && !login ? " ok" : "");
  st.textContent = !S.state.claude ? "Claude Code bulunamadı" : login ? "Claude Code: giriş yapılmamış" : "Claude Code hazır";
  st.title = !S.state.claude ? "Ayarlar'dan yolu girin"
    : login ? "Terminalde `claude` çalıştırıp /login ile giriş yapın. Sonra buraya tıklayın." : S.state.claude;
  $("#setStudent").value = c.student_name; $("#setClaude").value = c.claude_path || ""; $("#setModel").value = c.claude_model || "";
  $("#bankInfo").textContent = `Soru bankası: ${S.state.bank.books} kaynak PDF, ${S.state.bank.questions} soru · daha önce verilen: ${S.state.used} soru`;
}
$("#claudeStatus").onclick = () => loadState();
$("#openSettings").onclick = () => $("#settings").classList.remove("hidden");
$("#saveSettings").onclick = async () => {
  await api("/api/config", { method: "POST", body: { student_name: $("#setStudent").value,
    claude_path: $("#setClaude").value.trim(), claude_model: $("#setModel").value } });
  await loadState(); toast("Kaydedildi"); $("#settings").classList.add("hidden");
};
$("#resetUsed").onclick = async () => {
  if (!confirm("Daha önce verilen sorular listesi sıfırlansın mı? (Beyin bu soruları tekrar önerebilir.)")) return;
  await api("/api/used/reset", { method: "POST" }); await loadState(); toast("Sıfırlandı");
};

// ------------------------------------------------------------------ 1 · fotoğraflar
async function uploadFiles(files) {
  files = [...files].filter((f) => f.type.startsWith("image/") || /\.(jpe?g|png|webp|heic)$/i.test(f.name));
  if (!files.length) return toast("Fotoğraf bulunamadı");
  const fd = new FormData(); files.forEach((f, i) => fd.append("files", f, f.name || `yapistirilan_${i + 1}.png`));
  toast(`${files.length} fotoğraf yükleniyor…`);
  try {
    const r = await api("/api/upload", { method: "POST", body: fd });
    r.paths.forEach((path) => S.photos.push({ path, status: "Yapamadı" }));
    savePhotos(); toast(`${r.paths.length} fotoğraf eklendi`);
  } catch (e) { toast(e.message, 6000); }
}
const drop = $("#drop");
drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("over"); };
drop.ondragleave = () => drop.classList.remove("over");
drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove("over"); uploadFiles(e.dataTransfer.files); };
$("#fileIn").onchange = (e) => { uploadFiles(e.target.files); e.target.value = ""; };
document.addEventListener("paste", (e) => {
  if (e.target.closest("input, textarea")) return;
  const files = [...(e.clipboardData?.files || [])];
  if (files.length) { e.preventDefault(); uploadFiles(files); }
});

function renderPhotos() {
  $("#photos").innerHTML = S.photos.map((p, i) => `<div class="photo" data-i="${i}">
      <img src="${fileUrl(p.path)}" data-zoom title="Büyüt">
      <button class="x" title="Listeden çıkar">×</button>
      <span class="seg mini">${STATUSES.map((s) => `<label><input type="radio" name="st${i}" value="${s}" ${p.status === s ? "checked" : ""}>${s}</label>`).join("")}</span>
    </div>`).join("");
  $$("#photos .photo").forEach((el) => {
    const i = +el.dataset.i;
    $(".x", el).onclick = () => { S.photos.splice(i, 1); savePhotos(); };
    $$("input", el).forEach((r) => (r.onchange = () => { S.photos[i].status = r.value; store.set("photos", S.photos); }));
    $("[data-zoom]", el).onclick = () => modal(`<img src="${fileUrl(S.photos[i].path)}">`);
  });
  renderRunButton();
}
// beyin çalışırken büyük düğme "Beyni Durdur" olur (ikinci bir iş de böylece başlatılamaz)
function renderRunButton() {
  const b = $("#runBrain");
  b.classList.toggle("stop", !!S.running);
  b.disabled = !S.running && !S.photos.length;
  b.textContent = S.running ? "⏹ Beyni Durdur"
    : S.photos.length ? `🧠 Beyin Çalışsın (${S.photos.length} soru)` : "🧠 Beyin Çalışsın — önce fotoğraf ekleyin";
}

// ------------------------------------------------------------------ 2 · beyin
try { $("#model").value = localStorage.getItem("model") || ""; } catch {}
$("#model").onchange = () => { try { localStorage.setItem("model", $("#model").value); } catch {} };

$("#runBrain").onclick = async () => {
  if (S.running) return stopBrain();
  await loadState();  // giriş sonradan yapılmış olabilir: sayfayı yenilemeden tekrar bak
  if (!S.state.claude) return toast("Claude Code bulunamadı — Ayarlar'a bakın.");
  if (S.state.claude_login === false)
    return toast("Claude Code'da giriş yapılmamış: terminalde `claude` çalıştırıp /login ile giriş yapın.", 7000);
  const body = { images: S.photos, note: $("#note").value, size: $("input[name=size]:checked").value,
    allow_repeat: $("#allowRepeat").checked, model: $("#model").value, deep: $("#deep").checked };
  try {
    const r = await api("/api/brain", { method: "POST", body });
    watchJob(r.job, true); loadRuns();
  } catch (e) { toast(e.message); }
};

function watchJob(id, fresh = false) {
  S.job = id; S.since = 0; S.live = fresh; clearInterval(S.poll);
  $("#feed").innerHTML = ""; $("#lastThought").textContent = "";
  $("#live").classList.remove("hidden");
  $("#candidates").classList.add("hidden"); S.cand = null; S.runId = ""; S.basket = new Map(); S.hidden = new Set(); renderBar();
  if (fresh) $("#live").scrollIntoView({ behavior: "smooth" });
  S.poll = setInterval(pollJob, 1500); pollJob();
}
async function pollJob() {
  if (!S.job) return;
  let r; try { r = await api(`/api/jobs/${S.job}?since=${S.since}`); } catch { return; }
  S.since = r.next;
  const f = $("#feed");
  r.feed.forEach((x) => {
    const d = document.createElement("div"); d.className = x.type; d.textContent = x.text; f.appendChild(d);
    if (x.type === "text" || x.type === "error" || x.type === "done") {
      const lt = $("#lastThought");  // art arda gelen hatalar birlikte görünsün (ilki genelde asıl sebeptir)
      lt.textContent = x.type === "error" && lt.classList.contains("error") ? lt.textContent + "\n" + x.text : x.text;
      lt.className = "last-thought " + x.type;
    }
  });
  f.scrollTop = f.scrollHeight;
  const j = r.job; const running = j.status === "running";
  S.runImages = j.images;
  $("#jobHead").innerHTML = `${running ? '<span class="spinner"></span>' : ""}Beyin ${statusTr(j.status)} <span class="muted small">· ${esc(when(j.created))}${j.duration_s ? ` · ${(j.duration_s / 60).toFixed(1)} dk` : ""}</span>`;
  $("#cancelJob").classList.toggle("hidden", !running);
  S.running = running; renderRunButton();
  if (!running) {
    clearInterval(S.poll);
    if (r.has_candidates) loadCandidates(j.id, S.live);
    if (S.live) loadRuns();
  }
}
async function stopBrain() {
  if (!S.job || !confirm("Beyin durdurulsun mu? Bu çalışmanın adayları oluşmaz.")) return;
  await api(`/api/jobs/${S.job}/cancel`, { method: "POST" });
  toast("Beyin durduruldu"); pollJob();
}
$("#cancelJob").onclick = stopBrain;

// ------------------------------------------------------------------ 3 · adaylar
async function loadCandidates(id, scroll = false) {
  let c; try { c = await api(`/api/jobs/${id}/candidates`); } catch (e) { toast("Adaylar okunamadı: " + e.message); return; }
  S.cand = c; S.runId = id;
  $("#candidates").classList.remove("hidden");
  $("#summary").innerHTML = `<p>${esc(c.summary || "")}</p>`;
  $("#diagnosis").innerHTML = (c.diagnosis || []).map((d) => `<div class="d"><b>${esc(d.topic)}</b>
    <div>${esc(d.skill || "")}</div><div class="muted small">${esc((d.evidence || []).join(", "))}${d.level_note ? " · " + esc(d.level_note) : ""}</div></div>`).join("");
  // bu çalışmanın kayıtlı seçimi varsa onu yükle; yoksa beynin önerdikleriyle başla
  const fresh = !loadBasket();
  loadHidden();
  $("#groups").innerHTML = "";
  (c.groups || []).forEach((g, gi) => {
    const items = (g.items || []).filter((it) => it.found).sort((a, b) => (ROLE_ORDER[a.role] ?? 9) - (ROLE_ORDER[b.role] ?? 9));
    if (fresh) items.filter((it) => it.recommended).forEach((it) => S.basket.set(it.qid, basketItem(it, g, gi)));
    const el = document.createElement("div"); el.className = "group";
    el.innerHTML = `<div class="group-head"><div><h3>${esc(g.title)}</h3><div class="muted">${esc(g.why || "")}</div>
      <div class="row gap" style="margin-top:6px"><button class="chip" data-a="rec">Önerilenler</button><button class="chip" data-a="all">Tümü</button><button class="chip" data-a="none">Hiçbiri</button></div></div>
      <div class="src-imgs">${(g.source_images || []).map((p) => `<img src="${fileUrl(p)}" title="Öğrencinin yapamadığı soru">`).join("")}</div></div>
      <div class="cards">${items.map(cardHtml).join("")}</div>`;
    $("#groups").appendChild(el);
    el._items = items; el._g = g; el._gi = gi;
    $$("[data-a]", el).forEach((b) => (b.onclick = () => {
      items.forEach((it) => {
        const on = !S.hidden.has(it.qid) && (b.dataset.a === "all" || (b.dataset.a === "rec" && it.recommended));
        on ? S.basket.set(it.qid, basketItem(it, g, gi)) : S.basket.delete(it.qid);
      });
      syncCards(); saveBasket();
    }));
    $$(".src-imgs img", el).forEach((i) => (i.onclick = () => modal(`<img src="${i.src}">`)));
    $$(".card", el).forEach((card) => card.addEventListener("click", (e) => onCard(e, card, el)));
  });
  syncCards(); saveBasket();
  if (scroll) $("#candidates").scrollIntoView({ behavior: "smooth" });
}
const basketItem = (it, g, gi) => ({ qid: it.qid, role: it.role, group: g?.title || "", gi, answer: it.answer || "",
  source_images: g?.source_images || [] });

// zorluk rozeti: d1 kolay (≤2,4) · d2 orta (≤3,6) · d3 zor
const diffLevel = (it) => !it.diff ? "" : it.diff.value <= 2.4 ? "d1" : it.diff.value <= 3.6 ? "d2" : "d3";

// toplu kaldır düğmeleri: tüm konu gruplarındaki aday sorulardan uyanları listeden kaldırır (seçimden de çıkar);
// kaldırılanlar her çalışma için ayrı saklanır, "geri getir" ile döner
const BULK = { pekistirme: (it) => it.role === "pekistirme", orta: (it) => diffLevel(it) === "d2",
  zor: (it) => it.role === "zorlayici" || diffLevel(it) === "d3" };
const loadHidden = () => { S.hidden = new Set(store.get("hidden:" + S.runId, [])); };
const saveHidden = () => store.set("hidden:" + S.runId, [...S.hidden]);
const bulkMatches = (k) => $$("#groups .group").flatMap((el) => el._items || []).filter((it) => !S.hidden.has(it.qid) && BULK[k](it));
$$("[data-bulk]").forEach((b) => (b.onclick = () => {
  const hit = bulkMatches(b.dataset.bulk);
  hit.forEach((it) => { S.hidden.add(it.qid); S.basket.delete(it.qid); });
  saveHidden(); syncCards(); saveBasket(); toast(`${hit.length} soru kaldırıldı`);
}));
$("#bulkUndo").onclick = () => { const n = S.hidden.size; S.hidden.clear(); saveHidden(); syncCards(); toast(`${n} soru geri getirildi`); };
function syncBulk() {
  $$("[data-bulk]").forEach((b) => { const n = bulkMatches(b.dataset.bulk).length; $("b", b).textContent = n; b.disabled = !n; });
  $("#bulkUndo").classList.toggle("hidden", !S.hidden.size);
  $("b", $("#bulkUndo")).textContent = S.hidden.size;
}

function cardHtml(it) {
  const ans = it.bank_answer || it.answer || "";
  const claude = !it.bank_answer && it.answer;
  const d = it.diff;
  const lvl = diffLevel(it);
  return `<div class="card" data-q="${esc(it.qid)}">
    <div class="img"><img loading="lazy" src="${cropUrl(it.qid)}"></div>
    <div class="body"><div class="top-line"><span class="role ${it.role}">${ROLE[it.role] || it.role}</span>
      <span class="kind">${esc(it.kind || "")}</span>
      ${d ? `<span class="diff ${lvl}" title="${esc(it.difficulty_note || "")}">Zorluk ${d.value}/5</span>` : ""}
      ${it.verified ? '<span class="badge ver" title="Soru analisti bu soruyu çözdü ve uygun buldu">✓ denetlendi</span>' : ""}
      <span class="sel">☐</span></div>
      ${it.why ? `<div class="why">${esc(it.why)}</div>` : ""}
      <div class="foot"><span class="ans ${claude ? "claude" : ""}" title="${claude ? "Cevabı Claude çözdü — kontrol edin" : "Kaynağın cevap anahtarı"}">${ans ? `Cevap: ${esc(ans)}${claude ? "*" : ""}` : ""}</span>
        <span class="src" title="${esc(it.source || "")}">${esc(it.source || it.qid)}</span>
        <button class="chip zoom" title="Büyüt">⤢</button><button class="chip never" title="Bu soru bir daha önerilmesin">✕</button></div>
    </div></div>`;
}
async function onCard(e, card, groupEl) {
  const qid = card.dataset.q;
  if (e.target.closest(".zoom")) return modal(`<img src="${cropUrl(qid)}" style="width:680px">`);
  if (e.target.closest(".never")) {
    if (!confirm("Bu soru bu ve sonraki çalışmalarda bir daha önerilmesin mi?")) return;
    await api("/api/feedback", { method: "POST", body: { qid, value: "kullanma" } });
    S.basket.delete(qid); card.remove(); saveBasket(); return toast("Bu soru bir daha önerilmeyecek");
  }
  if (S.basket.has(qid)) S.basket.delete(qid);
  else S.basket.set(qid, basketItem(groupEl._items.find((x) => x.qid === qid), groupEl._g, groupEl._gi));
  syncCards(); saveBasket();
}
function syncCards() {
  $$(".card").forEach((c) => { const on = S.basket.has(c.dataset.q); c.classList.toggle("on", on); $(".sel", c).textContent = on ? "☑" : "☐";
    c.classList.toggle("hidden", S.hidden.has(c.dataset.q)); });
  syncBulk();
}

// ------------------------------------------------------------------ 4 · PDF
function renderBar() {
  $("#pdfBar").classList.toggle("hidden", !S.basket.size);
  $("#bCount").textContent = S.basket.size;
  document.body.classList.toggle("has-bar", S.basket.size > 0);
}
$("#bClear").onclick = () => { S.basket.clear(); syncCards(); saveBasket(); };
$("#makePdf").onclick = async () => {
  // konu grubu → öğretici → pekiştirme → zorlayıcı sırası
  const items = [...S.basket.values()].filter((x) => !S.hidden.has(x.qid)).map((x, i) => ({ ...x, _i: i }))
    .sort((a, b) => (a.gi ?? 99) - (b.gi ?? 99) || (ROLE_ORDER[a.role] ?? 9) - (ROLE_ORDER[b.role] ?? 9) || a._i - b._i);
  let wrong = [];
  if ($("#optWrong").checked) {
    wrong = [...new Set(items.flatMap((it) => it.source_images || []))];
    if (!wrong.length) wrong = S.runImages || [];
  }
  $("#makePdf").disabled = true; $("#makePdf").textContent = "Hazırlanıyor…";
  try {
    const r = await api("/api/pdf", { method: "POST", body: { title: $("#pdfTitle").value || "Çalışma Kâğıdı",
      items: items.map(({ qid, role, group, answer }) => ({ qid, role, group, answer })), wrong_images: wrong, run_id: S.runId } });
    window.open(r.url, "_blank");
    toast("PDF hazır: " + r.file); loadRuns(); loadState();
  } catch (e) { toast("PDF hatası: " + e.message, 5000); }
  $("#makePdf").disabled = false; $("#makePdf").textContent = "📄 PDF Oluştur";
};

// ------------------------------------------------------------------ önceki çalışmalar
async function loadRuns() {
  const runs = await api("/api/runs");
  $("#runList").innerHTML = runs.map((r) => `<div class="run ${r.id === S.job ? "cur" : ""}" data-id="${esc(r.id)}">
      <div class="thumbs">${r.images.slice(0, 4).map((p) => `<img loading="lazy" src="${fileUrl(p)}">`).join("")}</div>
      <div class="t"><b>${esc(when(r.created))}</b> · ${esc(r.title)} <span class="muted small">· ${statusTr(r.status)}${r.cost_usd ? ` · ~$${r.cost_usd.toFixed(2)}` : ""}</span>
        <div class="small">${r.pdfs.map((p) => `<a href="${p.url}" target="_blank">📄 ${esc(p.title)} (${p.count} soru)</a>`).join(" · ") || '<span class="muted">PDF yok</span>'}</div></div>
      <button class="ghost small" data-open>Aç</button>
      <button class="ghost small danger" data-del title="Çalışmayı ve PDF'lerini sil">🗑</button></div>`).join("")
    || `<p class="muted small">Henüz çalışma yok.</p>`;
  $$("#runList .run").forEach((el) => {
    const r = runs.find((x) => x.id === el.dataset.id);
    $("[data-open]", el).onclick = () => {
      S.photos = r.images.map((path) => ({ path, status: "Yapamadı" }));
      savePhotos(); watchJob(r.id); loadRuns(); $("#live").scrollIntoView({ behavior: "smooth" });
    };
    $("[data-del]", el).onclick = async () => {
      if (!confirm("Bu çalışma ve ondan üretilen PDF'ler silinsin mi?\n(İçindeki sorular tekrar önerilebilir olur.)")) return;
      await api("/api/runs/delete", { method: "POST", body: { ids: [r.id] } });
      try { localStorage.removeItem("basket:" + r.id); } catch {}
      if (r.id === S.job) { clearInterval(S.poll); S.job = null; S.runId = ""; S.basket = new Map(); renderBar();
        $("#live").classList.add("hidden"); $("#candidates").classList.add("hidden"); }
      loadRuns(); loadState();
    };
  });
}

// ------------------------------------------------------------------ başlat
(async function init() {
  renderPhotos();
  await loadState();
  await loadRuns();
  // adres satırından: ?run=<id> belirli bir çalışmayı açar; yoksa en son çalışma gösterilir
  const qp = new URLSearchParams(location.search);
  const last = qp.get("run") || (await api("/api/runs"))[0]?.id;
  if (last) watchJob(last);
})();
