"""Web sunucusu: Chrome'dan http://localhost:8765 ile yönetilir.

Tek akış: soru fotoğraflarını yükle → Beyin Çalışsın → aday soruları seç → PDF.
"""
import json
import shutil
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, pdfgen, qbank, runner

app = FastAPI(title="Beyin Çalışsın")
STATIC = Path(__file__).parent / "static"
USED_FILE = config.DATA / "used_qids.json"
ANSWER_OVERRIDES = config.DATA / "answer_overrides.json"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
IMG_MAGIC = (b"\xff\xd8", b"\x89PNG", b"RIFF", b"GIF8")
# her seçenek konu başına {öğretici, pekiştirme, zorlayıcı} hedefi; beyin seçim için daha fazla aday getirir
SIZES = {"az": (2, 2, 1), "normal": (3, 3, 2), "cok": (4, 5, 3)}


def _json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _photos_dir() -> Path:
    return Path(config.get()["photos_dir"])


def _rel(p: Path) -> str:
    """Proje içindeki yollar göreli saklanır (klasör başka yere taşınınca da çalışsın)."""
    try:
        return p.resolve().relative_to(config.ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def _resolve(p: str) -> Path:
    p = config.remap(p)
    return Path(p) if Path(p).is_absolute() else config.ROOT / p


# ------------------------------------------------------------------ genel
@app.get("/api/state")
def state():
    cfg = config.get()
    books = qbank.all_books()
    claude = config.find_claude()
    return {
        "config": {**cfg, **config._load()},  # ayarlar formu: göreli yollar göreli görünsün
        "version": (config.ROOT / "VERSION").read_text(encoding="utf-8").strip() if (config.ROOT / "VERSION").exists() else "",
        "claude": claude,
        "claude_login": config.claude_logged_in(claude) if claude else None,
        "bank": {"books": len(books), "questions": sum(b["questions"] for b in books)},
        "used": len(_json(USED_FILE, [])),
    }


@app.post("/api/config")
def set_config(patch: dict):
    cfg = config._load()  # ham hali: göreli yollar göreli kalsın
    for k in ("student_name", "claude_path", "claude_model"):
        if k in patch:
            cfg[k] = patch[k]
    config.save(cfg)
    return cfg


@app.post("/api/used/reset")
def used_reset():
    USED_FILE.write_text("[]", encoding="utf-8")
    return {"ok": True}


# ------------------------------------------------------------------ fotoğraflar
@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    """Fotoğrafları ogrenci/Sorular/<tarih>/ altına kaydeder, göreli yollarını döner."""
    day = _photos_dir() / datetime.now().strftime("%Y-%m-%d")
    day.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%H%M%S")
    got = []
    for f in files:  # önce hepsini denetle: biri bozuksa hiçbiri yazılmasın
        ext = Path(f.filename or "").suffix.lower() or ".png"
        if ext not in IMG_EXT:
            raise HTTPException(400, f"{f.filename}: desteklenmeyen dosya (JPG/PNG yükleyin; iPhone'da HEIC ise "
                                     f"Ayarlar › Kamera › Biçimler › En Uyumlu seçin)")
        data = await f.read()
        if not data.startswith(IMG_MAGIC):
            raise HTTPException(400, f"{f.filename}: resim dosyası değil")
        got.append((ext, data))
    out = []
    for i, (ext, data) in enumerate(got, 1):
        p = day / f"{stamp}_{i}{ext}"
        p.write_bytes(data)
        out.append(_rel(p))
    return {"paths": out}


@app.get("/api/file")
def get_file(path: str):
    p = _resolve(path).resolve()
    allowed = [_photos_dir().resolve(), (config.ROOT / "ogrenci").resolve()]
    if not any(r == p or r in p.parents for r in allowed) or not p.is_file():
        raise HTTPException(404)
    return FileResponse(p)


@app.get("/api/crop")
def crop(qid: str):
    p = qbank.crop_png(qid)
    if not p:
        raise HTTPException(404)
    return FileResponse(p, media_type="image/png", headers={"Cache-Control": "max-age=86400"})


# ------------------------------------------------------------------ beyin
class BrainReq(BaseModel):
    images: list[dict]            # [{"path", "status"}]
    note: str = ""
    size: str = "normal"          # az / normal / cok
    allow_repeat: bool = False
    model: str = ""               # "" = ayarlardaki; opus / sonnet / haiku
    deep: bool = False            # soru-analisti ajanıyla derin analiz


@app.post("/api/brain")
def brain(req: BrainReq):
    images = [{"path": im["path"], "status": im.get("status") or "Yapamadı"}
              for im in req.images if im.get("path") and _resolve(im["path"]).is_file()]
    if not images:
        raise HTTPException(400, "Önce yapamadığı sorunun fotoğrafını yükleyin.")
    h, p, z = SIZES.get(req.size, SIZES["normal"])
    task = {
        "student": config.get()["student_name"],
        "teacher_note": req.note,
        "images": images,
        "counts": {"hatirlatici": h, "pekistirme": p, "zorlayici": z},
        "max_topics": 4,
        "exclude_qids": [] if req.allow_repeat else _json(USED_FILE, []),
        "deep": req.deep,
    }
    title = f"{len(images)} soru fotoğrafı" + (" · derin analiz" if req.deep else "")
    prompt = ("brain/BRAIN.md dosyasındaki talimatları uygula. Görev dosyası: <RUN_DIR>/task.json. "
              "RUN_DIR = <RUN_DIR>. Sonucu <RUN_DIR>/candidates.json dosyasına yaz. Türkçe çalış.")
    rid = runner.start("brain", title, prompt, req.model_dump() | {"images": images},
                       files={"task.json": task}, on_finish=_save_candidate_ratings, model=req.model)
    return {"job": rid}


def _save_candidate_ratings(rid: str) -> None:
    """Beynin adaylara verdiği zorluk puanlarını kalıcı depoya yaz."""
    data = _json(runner.run_dir(rid) / "candidates.json", {})
    patch = {}
    for g in data.get("groups", []):
        for it in g.get("items", []):
            try:
                v = int(it.get("difficulty"))
            except (TypeError, ValueError):
                continue
            if 1 <= v <= 5 and qbank.get_question(it.get("qid", "")):
                patch[it["qid"]] = {"claude": v, "note": str(it.get("difficulty_note", ""))[:200]}
    if patch:
        qbank.update_store("ratings", patch)


@app.post("/api/feedback")
def feedback(body: dict):
    """{"qid", "value": "kullanma"|null} — "kullanma" denen soru bir daha önerilmez."""
    qid, v = body["qid"], body.get("value")
    if v not in (None, "", "kullanma"):
        raise HTTPException(400, "geçersiz değer")
    qbank.update_store("feedback", {qid: {"teacher": v} if v else None})
    return {"qid": qid}


def _run_summary(j: dict) -> dict:
    params = j.get("params", {})
    images = params.get("images") or _json(runner.run_dir(j["id"]) / "task.json", {}).get("images", [])
    return {"id": j["id"], "title": j.get("title", ""), "created": j.get("created", ""), "status": j.get("status"),
            "duration_s": j.get("duration_s"), "cost_usd": j.get("cost_usd"),
            "images": [im["path"] for im in images], "pdfs": []}


@app.get("/api/runs")
def runs():
    """Önceki beyin çalışmaları ve bunlardan üretilen PDF'ler (en yeni önce)."""
    out = [_run_summary(j) for j in runner.list_jobs("brain")]
    by_id = {r["id"]: r for r in out}
    for p in sorted(config.OUTPUT_DIR.glob("*.pdf"), reverse=True):
        meta = _json(p.with_suffix(".json"), {})
        r = by_id.get(meta.get("run_id", ""))
        if r is not None:
            r["pdfs"].append({"file": p.name, "title": meta.get("title", p.stem), "count": meta.get("count"),
                              "url": f"/api/outputs/{p.name}"})
    return out


@app.get("/api/jobs/{rid}")
def job(rid: str, since: int = 0):
    try:
        j = runner.read_job(rid)
    except FileNotFoundError:
        raise HTTPException(404)
    feed = runner.read_feed(rid, since)
    cand = runner.run_dir(rid) / "candidates.json"
    return {"job": _run_summary(j), "feed": feed, "next": since + len(feed), "has_candidates": cand.exists()}


@app.post("/api/jobs/{rid}/cancel")
def job_cancel(rid: str):
    return {"ok": runner.cancel(rid)}


@app.get("/api/jobs/{rid}/candidates")
def job_candidates(rid: str):
    data = _json(runner.run_dir(rid) / "candidates.json", None)
    if data is None:
        raise HTTPException(404, "aday dosyası yok veya bozuk")
    overrides = _json(ANSWER_OVERRIDES, {})
    stores = {k: qbank.load_store(k) for k in qbank.STORES}
    for g in data.get("groups", []):
        for it in g.get("items", []):
            q = qbank.get_question(it.get("qid", ""))
            it["found"] = bool(q)
            if q:
                it["source"] = pdfgen.source_label(q)
                it["bank_answer"] = overrides.get(it["qid"]) or q.get("answer", "")
                it["kind"] = q["book"]["kind_name"]
                it["diff"] = qbank.difficulty(q["book"], q, stores)
    return data


@app.post("/api/runs/delete")
def runs_delete(body: dict):
    """Çalışmaları ve onlardan üretilen PDF'leri siler; PDF'lerdeki sorular tekrar önerilebilir olur."""
    runs_dir = config.RUNS_DIR.resolve()
    ids = set(body.get("ids", []))
    n = 0
    for rid in ids:
        d = (config.RUNS_DIR / rid).resolve()
        if d.parent != runs_dir or not d.is_dir():
            continue
        if _json(d / "job.json", {}).get("status") == "running":
            continue
        shutil.rmtree(d, ignore_errors=True)
        n += 1
    freed, still = set(), set()
    for m in config.OUTPUT_DIR.glob("*.json"):
        meta = _json(m, {})
        qids = {it["qid"] for it in meta.get("items", [])}
        if meta.get("run_id") in ids:
            freed |= qids
            for f in (m, m.with_suffix(".pdf")):
                f.unlink(missing_ok=True)
        else:
            still |= qids
    used = [q for q in _json(USED_FILE, []) if q not in freed or q in still]
    USED_FILE.write_text(json.dumps(used, ensure_ascii=False), encoding="utf-8")
    return {"deleted": n}


# ------------------------------------------------------------------ PDF
class PdfReq(BaseModel):
    title: str = "Çalışma Kâğıdı"
    items: list[dict]                   # [{"qid", "role", "group", "answer"?}]
    wrong_images: list[str] = []        # öğrencinin yapamadığı soru fotoğrafları (başa eklenir)
    run_id: str = ""


@app.post("/api/pdf")
def make_pdf(req: PdfReq):
    if not req.items:
        raise HTTPException(400, "soru seçilmedi")
    overrides = _json(ANSWER_OVERRIDES, {})
    for it in req.items:  # Claude'un çözdüğü cevapları kaydet
        q = qbank.get_question(it["qid"])
        if it.get("answer") and q and not q.get("answer"):
            overrides[it["qid"]] = it["answer"]
    ANSWER_OVERRIDES.write_text(json.dumps(overrides, ensure_ascii=False, indent=1), encoding="utf-8")
    orig = qbank.get_question

    def with_override(qid):
        q = orig(qid)
        if q and not q.get("answer") and overrides.get(qid):
            q["answer"] = overrides[qid]
        return q

    qbank.get_question = with_override
    try:
        wrong = [{"path": str(_resolve(p)), "caption": f"Soru {i}"} for i, p in enumerate(req.wrong_images, 1)]
        out = pdfgen.build(req.items, req.title, config.get()["student_name"], req.title, wrong)
    finally:
        qbank.get_question = orig
    used = _json(USED_FILE, [])
    used += [it["qid"] for it in req.items if it["qid"] not in used]
    USED_FILE.write_text(json.dumps(used, ensure_ascii=False), encoding="utf-8")
    meta = {"file": out.name, "title": req.title, "run_id": req.run_id, "items": req.items,
            "count": len(req.items)}
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"file": out.name, "url": f"/api/outputs/{out.name}"}


@app.get("/api/outputs/{name}")
def output_file(name: str, download: bool = False):
    p = (config.OUTPUT_DIR / name).resolve()
    if p.parent != config.OUTPUT_DIR.resolve() or not p.exists():
        raise HTTPException(404)
    return FileResponse(p, media_type="application/pdf",
                        filename=name if download else None,
                        content_disposition_type="attachment" if download else "inline")


# ------------------------------------------------------------------ statik
class _Static(StaticFiles):
    """Arayüz dosyaları her açılışta tazelenip denetlensin: güncellemeden sonra tarayıcı eski app.js'i kullanmasın."""
    async def get_response(self, path, scope):
        r = await super().get_response(path, scope)
        r.headers["Cache-Control"] = "no-cache"
        return r


app.mount("/", _Static(directory=STATIC, html=True), name="static")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    runner.recover_stale()
    from . import bank
    bank.seed()
    port = int(config.get().get("port", 8765))
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    url = f"http://localhost:{port}"
    print(f"\n  Beyin Çalışsın hazır → {url}\n  (kapatmak için bu pencereyi kapatın)\n")
    if "--no-browser" not in sys.argv:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
