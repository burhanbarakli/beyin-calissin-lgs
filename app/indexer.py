"""LGS kaynak PDF'lerinden soru indeksi çıkarır (yapay zekâ kullanmadan, hızlı).

Kaynak klasöründeki `katalog.json` her PDF'in türünü, ünitesini ve kazanımını verir:
    {"01_Carpanlar_Ve_Katlar/8.02_EBOB_EKOK_Testi.pdf":
        {"kind": "kazanim_testi", "unit": "Çarpanlar ve Katlar", "code": "8.02", "title": "EBOB - EKOK"}}

Her soru için: sayfa, kırpma kutusu (bbox), soru no, konu, seviye (öğretici/temel/yeni nesil/LGS),
metin özeti ve (PDF'te varsa) cevap. Soru numarası metin olarak okunamıyorsa renkli numara kutularından bulunur.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

from . import config

SUBJECTS = {"mat": "Matematik", "fen": "Fen Bilimleri"}
# tür → (görünen ad, seviye etiketi, rank: 1 öğretici/temel · 2 orta/pekiştirme · 3 zor/LGS düzeyi)
KINDS = {
    "calisma_kagidi": ("Çalışma Kağıdı", "Öğretici", 1),
    "kazanim_testi": ("Kazanım Testi", "Temel", 1),
    "tarama": ("Konu Tarama", "Yeni Nesil", 2),
    "lgs_cikmis": ("LGS Çıkmış", "LGS", 3),
    "deneme": ("MEBİ Deneme", "LGS", 3),
    "meb_kitap": ("MEB Çalışma Kitabı", "LGS", 3),
}

TP_FLAGS = pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES
QNUM_RE = re.compile(r"^\s*(\d{1,3})\s*[.)](?!\d)\s*(.*)$")  # "15.00" saat/ondalık değil
KEY_PAIR_RE = re.compile(r"(?<![\d,])(\d{1,2})\s*\.\s*([A-D])\b")
# sınav kapağındaki "1. Bu testte 20 soru vardır." gibi yönerge satırları soru değildir
INSTRUCTION_RE = re.compile(r"Bu testte|Cevaplarınızı|cevap kâğıdı|SINAV BAŞLAMADAN", re.I)
SKIP_PAGE_RE = re.compile(r"SINAV BAŞLAMADAN|her hakkı saklıdır|Bu kitapçıkta \d+ soru", re.I)
SUBJECT_HEAD_RE = re.compile(r"FEN BİLİMLERİ|MATEMATİK")


def fix_text(s: str) -> str:
    """Bazı PDF'lerde (çıkmış sorular) font kodlaması 29 karakter kaydırılmış: '7XUIDQ' -> 'Turfan'."""
    if "\n" in s:
        return "\n".join(fix_text(x) for x in s.split("\n"))
    if any(ord(c) < 0x20 and c not in "\t\r" for c in s):
        return "".join(chr(ord(c) + 29) if 0x03 <= ord(c) <= 0x5D else c for c in s)
    return s


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", fix_text(s))
    s = s.replace("­", "")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- Soru tespiti
def detect_questions(page, tp=None, ignore=(), bottom=0.925) -> list[dict]:
    """ignore: kırpıma girmemesi gereken süs alanları (katalogdaki "ignore_rects": sayfa numarası vb.)
    bottom: altbilginin başladığı yer (sayfa yüksekliğinin oranı; katalogdaki "bottom")"""
    W, H = page.rect.width, page.rect.height
    mid = W / 2
    top_limit, bottom_limit = H * 0.04, H * bottom  # başlıksız kitaplarda ilk soru y≈41
    tp = tp or page.get_textpage(flags=TP_FLAGS)
    d = page.get_text("dict", textpage=tp)
    lines = []
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            lines.append((ln["bbox"], spans))

    cands = []
    for bbox, spans in lines:
        first = spans[0]
        txt = fix_text(first["text"])
        if len(spans) > 1 and re.fullmatch(r"\s*\d{1,3}\s*", txt):
            txt += fix_text(spans[1]["text"])
        m = QNUM_RE.match(txt)
        if not m:
            continue
        n = int(m.group(1))
        if n == 0 or n > 160:  # MEB çalışma kitabında ünite boyunca 154'e kadar
            continue
        x0, y0 = first["bbox"][0], first["bbox"][1]
        if y0 < top_limit or y0 > bottom_limit:
            continue
        bold = bool(first["flags"] & 16) or "bold" in first["font"].lower() or "black" in first["font"].lower()
        # "1. ADIM", "2020 TYT" vb. yanlış pozitifleri ele
        rest = norm(" ".join(s["text"] for s in spans))
        if re.search(r"ADIM|TEST|BÖLÜM|ÜNİTE|DENEME", rest, re.I) and len(rest) < 20:
            continue
        if INSTRUCTION_RE.search(rest):
            continue
        # numaranın ("12.") kapladığı alan: PDF'te orijinal numarayı kapatıp yenisini yazmak için
        if len(spans) > 1 and re.fullmatch(r"\s*\d{1,3}\s*", fix_text(first["text"])):
            nx1 = spans[1]["bbox"][2]
        else:
            # span "14.   " gibi sondaki boşluklarla gelebilir: karakter genişliği oranıyla böl
            # (rakam ~0,556 em, nokta/boşluk ~0,278 em); sayıyla oranlamak noktayı dışarıda bırakıyordu
            fx0, fx1 = first["bbox"][0], first["bbox"][2]
            ftxt = fix_text(first["text"])
            cw = lambda ch: 0.556 if ch.isdigit() else 0.278 if ch in ".) " else 0.5  # noqa: E731
            numlen = len(re.match(r"\s*\d{1,3}\s*[.)]", ftxt).group(0))
            nx1 = fx0 + (fx1 - fx0) * sum(map(cw, ftxt[:numlen])) / max(0.1, sum(map(cw, ftxt)))
        num = [round(x0, 1), round(y0, 1), round(nx1 + 1, 1), round(first["bbox"][3], 1)]
        cands.append({"n": n, "x0": x0, "y0": y0, "bold": bold, "col": 0 if x0 < mid - 10 else 1, "num": num})

    if not cands:
        return []
    # her sütunda soru numaraları sol kenara hizalıdır: en soldaki x0'a yakın olanları al
    # sağ sütun, ancak numaraları sol sütundakilerin devamıysa gerçektir (yoksa şekil içi madde: "15.")
    left_x = min([c["x0"] for c in cands if c["col"] == 0], default=0)
    left_ns = [c["n"] for c in cands if c["col"] == 0 and c["x0"] - left_x < 14]
    if left_ns and not any(min(left_ns) < c["n"] <= max(left_ns) + 4 for c in cands if c["col"] == 1):
        cands = [c for c in cands if c["col"] == 0]
    result = []
    two_col = any(c["col"] == 1 for c in cands)
    for col in (0, 1):
        cc = [c for c in cands if c["col"] == col]
        if not cc:
            continue
        # sol hizayı kalın numaralardan bul; kalın olmayanları sadece tam hizalıysa kabul et
        bolds = [c for c in cc if c["bold"]]
        if bolds and len(bolds) >= max(1, len(cc) // 3):
            left = min(c["x0"] for c in bolds)
            cc = [c for c in cc if (c["bold"] and c["x0"] - left < 14) or abs(c["x0"] - left) < 3]
        else:
            left = min(c["x0"] for c in cc)
            cc = [c for c in cc if c["x0"] - left < 14]
        cc.sort(key=lambda c: c["y0"])
        # artan numara dizisi
        seq, last = [], -1
        for c in cc:
            if c["n"] > last:
                seq.append(c)
                last = c["n"]
        for c in seq:
            c["left"] = left
        result += seq

    # sütun sınırları
    items = page_items(page)
    # iki sütunlu sayfada sol sütundan başlayıp sütun ortasını geçen yazı satırı olan soru tam genişliktedir
    # (ör. deneme kitapçığında üstte iki soru yan yana, altta tek soru boydan boya)
    for c in result:
        c["full"] = False
        if two_col and c["col"] == 0:
            below = [o["y0"] for o in result if o["col"] == 0 and o["y0"] > c["y0"] + 2]
            y1 = min(below, default=bottom_limit)
            c["full"] = any(x0 < mid - 20 and x1 > mid + 20 and c["y0"] - 4 <= y0 < y1 - 8  # alttakinin ilk satırı değil
                            for (x0, y0, x1, _), _ in lines)
    out = []
    for c in result:
        if c["full"]:
            cx0, cx1 = c["left"] - 6, W - 8
        elif two_col:
            cx0 = c["left"] - 6
            cx1 = mid - 4 if c["col"] == 0 else W - 8
            if c["col"] == 1:
                cx0 = max(mid - 4, c["left"] - 6)
        else:
            cx0, cx1 = c["left"] - 6, W - 8
        # alttaki sınır: aynı sütundaki sonraki soru ya da (sağ sütunda) alttaki tam genişlikli soru
        same = [o for o in result if (o["col"] == c["col"] or o["full"]) and o["y0"] > c["y0"] + 2]
        y_end = min([o["y0"] for o in same], default=bottom_limit) - 7  # numara simgesi yazıdan yukarıda başlar
        clip = pymupdf.Rect(cx0, c["y0"] - 4, cx1, y_end)
        # içeriğe sıkıştır
        tight = content_rect(items, clip, next_below=bool(same), ignore=ignore)
        if tight is None:  # taranmış sayfa (tam sayfa görsel + görünmez metin): sütun parçasını olduğu gibi al
            tight = clip
        if tight.height < 12:
            continue
        # yatayda da içeriğe sıkıştır: sütun arasındaki şerit ve kenar süsleri kırpıma girmesin
        rect = pymupdf.Rect(max(clip.x0, tight.x0 - 4), tight.y0 - 3, min(clip.x1, tight.x1 + 4), tight.y1 + 4)
        text = lines_text(lines, rect)
        above = lines_text(lines, pymupdf.Rect(cx0, c["y0"] - 26, cx1, c["y0"] - 1))
        out.append({"n": c["n"], "col": c["col"], "bbox": [round(v, 1) for v in rect], "num": c["num"],
                    "text": text, "above": above})
    out.sort(key=lambda q: (q["col"], q["bbox"][1]))
    return out


def lines_text(lines, rect) -> str:
    """Merkezi rect içinde kalan satırların metni (textpage ile clip çalışmadığı için elle)."""
    out = []
    for (x0, y0, x1, y1), spans in lines:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if rect.x0 <= cx <= rect.x1 and rect.y0 <= cy <= rect.y1:
            out.append((round(y0), x0, " ".join(s["text"] for s in spans)))
    out.sort()
    return norm(" ".join(t for _, _, t in out))


def page_items(page) -> list:
    """Sayfadaki çizilen öğelerin kutuları: şekiller/görseller + yatay metin satırları.

    Metin, bboxlog yerine satır satır alınır: bazı PDF'lerde tüm metin tek bir sayfa boyu kutuya
    düşer, ayrıca kenardaki döndürülmüş (dikey) yazılar böylece kırpıma girmez.
    """
    items = []
    try:
        for kind, rect in page.get_bboxlog():
            if kind.startswith("ignore") or kind.endswith("text"):
                continue
            items.append(pymupdf.Rect(rect))
    except Exception:
        pass
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            if abs(ln["dir"][1]) < 0.1 and any(sp["text"].strip() for sp in ln["spans"]):
                items.append(pymupdf.Rect(ln["bbox"]))
    return items


def content_rect(items, clip, next_below=False, ignore=()):
    r = None
    for it in items:
        br = it & clip
        if br.is_empty or (br.width < 1.5 and br.height < 1.5):
            continue
        # arka plan / sayfa genişliğindeki çerçeveleri sayma
        if it.width > clip.width * 1.2 or it.height > clip.height * 1.5:
            continue
        # soru alanını boydan boya saran kutu (sayfa çerçevesi) içerik değildir
        if it.x0 <= clip.x0 + 6 and it.x1 >= clip.x1 - 20 and it.y0 <= clip.y0 + 6 and it.y1 >= clip.y1 - 6:
            continue
        if any(z.contains(it) for z in ignore):
            continue
        # sütun kenarındaki dikey şerit ve onun (çizgi olarak çizilmiş) dikey yazısı
        if it.height > 30 and it.height > it.width * 6 and (br.x1 > clip.x1 - 25 or br.x0 < clip.x0 + 25):
            continue
        if it.width < 14 and (br.x0 > clip.x1 - 14 or br.x1 < clip.x0 + 14):
            continue
        # altta soru varsa sınırı aşan şekil onundur (şekli numarasından yukarıda başlayabilir)
        if next_below and it.y1 > clip.y1 + 4 and it.y0 > clip.y0 + 20:
            continue
        r = br if r is None else r | br
    return r


# ---------------------------------------------------------------- Numara kutuları
def detect_badges(page) -> list[dict]:
    """Metni okunamayan (font kodlaması bozuk) sayfalarda soruları renkli numara kutularından bulur.

    Kutu: sütunun sol kenarında 14-24 pt'lik renkli dolu kare, içinde soru numarası yazar.
    Sağ sütunda kutusu olmayan sol sütun sorusu sayfa genişliğindedir.
    """
    W, H = page.rect.width, page.rect.height
    mid = W / 2
    boxes, seen = [], set()
    for dr in page.get_drawings():
        r, fill = dr["rect"], dr.get("fill")
        if not fill or not (14 <= r.width <= 24 and 14 <= r.height <= 24):
            continue
        if max(fill) - min(fill) < 0.3:  # beyaz / gri: süs ya da sayfa numarası
            continue
        if r.y0 < H * 0.06 or r.y1 > H * 0.93:
            continue
        col = 0 if r.x0 < W * 0.15 else (1 if mid - 20 < r.x0 < W * 0.62 else None)
        label = page.get_textbox(r).strip()
        if col is None or not label.isdigit() or not 0 < int(label) <= 60 or int(label) in seen:
            continue
        seen.add(int(label))
        boxes.append({"n": int(label), "col": col, "r": r})
    items = page_items(page)
    out = []
    for b in boxes:
        r = b["r"]
        # tam genişlik: sorunun dikey aralığında (bir sonraki sol kutuya kadar) sağ sütunda kutu yok
        next_left = min([o["r"].y0 for o in boxes if o["col"] == 0 and o["r"].y0 > r.y0 + 2], default=H)
        full = b["col"] == 0 and not any(o["col"] == 1 and r.y0 - 30 < o["r"].y0 < next_left - 30 for o in boxes)
        cx0 = r.x0 - 4
        cx1 = W - 20 if b["col"] == 1 or full else mid - 4
        # bitiş: aynı sütunda alttaki kutu ya da alttaki daha büyük numaralı (tam genişlik) soru
        below = [o["r"].y0 for o in boxes if o["r"].y0 > r.y0 + 2
                 and (o["col"] == b["col"] or full or o["n"] > b["n"])]
        y_end = min(below, default=H * 0.93) - 3
        clip = pymupdf.Rect(cx0, r.y0 - 4, cx1, y_end)
        tight = content_rect(items, clip) or clip
        out.append({"n": b["n"], "col": b["col"],
                    "bbox": [round(v, 1) for v in (clip.x0, clip.y0, clip.x1, tight.y1 + 4)],
                    "num": [round(v, 1) for v in r]})
    return sorted(out, key=lambda q: q["n"])


def readable(text: str) -> bool:
    """Bozuk font kodlamalı metni ayırt eder (çoğu harf Türkçe alfabede değilse okunamaz)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return True
    ok = sum(1 for c in letters if c.lower() in "abcçdefgğhıijklmnoöprsştuüvyzqwx")
    return ok / len(letters) > 0.85


# ---------------------------------------------------------------- Kitap indeksi
def load_catalog(path: Path) -> dict:
    """PDF'in üst klasörlerindeki katalog.json'dan bu dosyanın kaydı."""
    for d in path.parents:
        cat = d / "katalog.json"
        if cat.exists():
            data = json.loads(cat.read_text(encoding="utf-8"))
            return data.get(path.relative_to(d).as_posix(), {})
    return {}


def slug(s: str) -> str:
    s = fold(s)
    return re.sub(r"[^a-z0-9.]+", "_", s).strip("_")


def fold(s: str) -> str:
    s = (s or "").replace("İ", "i").replace("I", "ı").lower()
    s = unicodedata.normalize("NFKD", s.translate(str.maketrans("çğıöşüâîû", "cgiosuaiu")))
    return "".join(c for c in s if not unicodedata.combining(c))


def book_meta(path: Path) -> dict:
    cat = load_catalog(path)
    kind = cat.get("kind") or ("lgs_cikmis" if "lgs_" in path.stem.lower() else
                               "tarama" if "tarama" in path.stem.lower() else
                               "calisma_kagidi" if "calisma" in path.stem.lower() else "kazanim_testi")
    subject = cat.get("subject", "mat")
    code, title, unit = cat.get("code", ""), cat.get("title", path.stem), cat.get("unit", "")
    if cat.get("id"):
        bid = cat["id"]
    elif kind == "lgs_cikmis":
        year = re.search(r"20\d\d", path.stem)
        bid = f"lgs_{subject}_cikmis_{year.group(0) if year else slug(path.stem)}"
    elif code:
        bid = f"lgs_{subject}_{code}_{'calisma' if kind == 'calisma_kagidi' else 'test'}"
    else:
        bid = f"lgs_{subject}_{slug(path.stem)}"
    name, level, rank = KINDS[kind]
    return {
        "id": bid,
        "path": config.rel(path),
        "exam": "LGS",
        "subject": subject,
        "subject_name": SUBJECTS.get(subject, subject),
        "kind": kind,
        "kind_name": name,
        "unit": unit,
        "code": code,
        "title": title,
        "level": level,
        "rank": rank,
    }


def book_topic(meta: dict) -> str:
    """Kazanım varsa "Ünite: Kazanım", yoksa ünite adı. Çıkmış sorularda boş (beyin etiketler)."""
    if meta["kind"] == "lgs_cikmis":
        return ""
    if meta["code"]:
        return f"{meta['unit']}: {meta['title']}"
    return meta["unit"]


def parse_key(text: str, subject: str) -> dict:
    """Cevap anahtarı metninden {no: şık}. Birden çok test varsa (Sayısal Bölüm: mat + fen) doğru blok seçilir."""
    blocks, cur, last = [], {}, 0
    for m in KEY_PAIR_RE.finditer(text):
        n = int(m.group(1))
        if n <= last and cur:
            blocks.append(cur)
            cur = {}
        cur[n] = m.group(2)
        last = n
    if cur:
        blocks.append(cur)
    if not blocks:
        return {}
    # "SAYISAL BÖLÜM" anahtarında sıra: Matematik, Fen Bilimleri
    if len(blocks) > 1 and subject == "fen":
        return blocks[1]
    return blocks[0]


def is_key_page(text: str) -> bool:
    pairs = len(KEY_PAIR_RE.findall(text))
    return pairs >= 8 and len(text) < 900 or pairs >= 4 and "CEVAP ANAHTAR" in text.upper()


def page_subject(text: str) -> str:
    m = SUBJECT_HEAD_RE.search(text[:300])
    if not m:
        return ""
    return "fen" if m.group(0).startswith("FEN") else "mat"


def index_book(path: Path, progress=None) -> dict:
    meta = book_meta(path)
    doc = pymupdf.open(path)
    topic = book_topic(meta)
    year = re.search(r"20\d\d", path.stem) if meta["kind"] == "lgs_cikmis" else None
    questions, key, key_pages = [], {}, []
    cat = load_catalog(path)
    ignore = [pymupdf.Rect(r) for r in cat.get("ignore_rects", [])]
    for i in range(doc.page_count):
        page = doc[i]
        tp = page.get_textpage(flags=TP_FLAGS)
        text = fix_text(page.get_text(textpage=tp))
        if progress:
            progress(i, doc.page_count)
        if is_key_page(text):
            key.update(parse_key(text, meta["subject"]))
            key_pages.append(i + 1)
            continue
        if SKIP_PAGE_RE.search(text):
            continue
        ps = page_subject(text)
        if ps and ps != meta["subject"]:  # Sayısal Bölüm kitapçığında diğer dersin sayfaları
            continue
        found = [] if meta["kind"] == "tarama" else detect_questions(page, tp, ignore, cat.get("bottom", 0.925))
        if not found or not readable(" ".join(q["text"] for q in found)):
            found = [{**b, "text": ""} for b in detect_badges(page)]
        # sayfa içinde numara sırasıyla: bazı kitapçıklarda sıra sol, sağ, sonra yine sol sütundur
        for q in sorted(found, key=lambda q: q["n"]):
            # numaralar kitap boyunca artar: geriye dönen ya da çok ileri atlayan numara
            # soru içindeki madde işaretidir (ör. "15." bir tablo satırı)
            last = questions[-1]["n"] if questions else 0
            if not last < q["n"] <= last + 3:
                continue
            text_q = q["text"] if readable(q["text"]) else ""
            questions.append({
                "qid": f"{meta['id']}|p{i + 1}|q{q['n']}",
                "page": i + 1,
                "n": q["n"],
                "bbox": q["bbox"],
                "num": q["num"],
                "topic": topic,
                "level": meta["level"],
                "rank": meta["rank"],
                "osym": f"{year.group(0)} LGS" if year else "",
                "text": text_q[:600],
                "answer": "",
                "solved": False,
            })
    # kazanım testlerinde sondaki sorular genelde daha zor: ikinci yarı "Orta"
    if meta["kind"] == "kazanim_testi" and questions:
        half = max(q["n"] for q in questions) / 2
        for q in questions:
            if q["n"] > half:
                q["level"], q["rank"] = "Orta", 2
    # kitabın anahtarı ayrı sayfada/kitapta ise katalogda verilir: {"key": {"1": "C", ...}}
    key = key or {int(n): a for n, a in load_catalog(path).get("key", {}).items()}
    for q in questions:
        q["answer"] = key.get(q["n"], "")
    return {"book": meta, "pages": doc.page_count, "key_pages": key_pages, "questions": questions,
            "answers_filled": bool(key)}


def index_path(book_id: str) -> Path:
    return config.INDEX_DIR / f"{book_id}.json"


def list_source_pdfs() -> list[Path]:
    out = []
    for src in config.get()["sources"]:
        p = Path(src)
        if p.is_dir():
            out += sorted(p.rglob("*.pdf"))
    return out


# indeks yenilenince korunacak, sonradan eklenen alanlar: cevap (Claude) ve etiket (`qbank label`)
KEEP_ANSWER = ("answer", "answer_source")
KEEP_LABEL = ("topic", "skill", "role", "broken", "labeled", "topics2")


def run(paths=None, force=False, log=print):
    paths = paths or list_source_pdfs()
    for p in paths:
        meta = book_meta(p)
        out = index_path(meta["id"])
        if out.exists() and not force:
            log(f"atlandı (var): {meta['id']}")
            continue
        log(f"indeksleniyor: {meta['id']}")
        data = index_book(p)
        if out.exists():
            old = {q["qid"]: q for q in json.loads(out.read_text(encoding="utf-8")).get("questions", [])}
            for q in data["questions"]:
                o = old.get(q["qid"], {})
                for f in KEEP_ANSWER:
                    if o.get(f) and not q.get(f):
                        q[f] = o[f]
                if o.get("labeled"):
                    q.update({f: o[f] for f in KEEP_LABEL if f in o})
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        answered = sum(1 for q in data["questions"] if q["answer"])
        log(f"  {len(data['questions'])} soru, {answered} cevaplı")


def relink(log=print):
    """Yeniden indekslemeden, indekslerdeki PDF yollarını bu bilgisayardaki kaynak dosyalara göreli bağlar
    (başka bilgisayarda, ör. Mac'te üretilmiş indeksler için). Kırpma kutuları, cevaplar, etiketler aynen kalır."""
    from .qbank import resolve_pdf
    missing = 0
    for out in sorted(config.INDEX_DIR.glob("*.json")):
        data = json.loads(out.read_text(encoding="utf-8"))
        old = data["book"].get("path", "")
        found = resolve_pdf(old)
        if not Path(found).is_file():
            missing += 1
            log(f"bulunamadı: {data['book']['id']} ({Path(old).name})")
            continue
        new = config.rel(found)
        if new != old:
            data["book"]["path"] = new
            out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            log(f"bağlandı: {data['book']['id']} -> {new}")
    log(f"bitti, bulunamayan: {missing}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--relink" in sys.argv:
        relink()
    else:
        run([Path(a) for a in args] or None, force="--force" in sys.argv)
