"""Öğretmen kitaplığı: yayınevlerinin öğretmene verdiği PDF soru bankaları için sayfa-konu indeksi.

PDF'ler taranmış görüntüdür; Tesseract OCR ile her sayfa okunur, sayfanın konusu (sistemin kazanım adlarıyla) ve
dersi (matematik dışı sayfalar elenir) bulunur. Beyin uygun sayfaları bulup görselini açar, soruyu kendisi seçer.

PDF'ler, OCR metni ve indeks yalnızca bu bilgisayarda durur (data/kitaplik/, .gitignore); GitHub'a gitmez.

    python -m app.kitaplik tara [--workers 6] [--limit N]   -> OCR (kaldığı yerden devam eder)
    python -m app.kitaplik siniflandir                    -> sayfa-konu indeksi (data/kitaplik/sayfalar.json)
    python -m app.kitaplik ozet                           -> kitap başına sayfa/konu dağılımı
    python -m app.kitaplik ara --topic "ebob,ekok" [--text "eşit,en az"] [--book nartest] [--limit 20]
    python -m app.kitaplik sayfa <kitap_id> <sayfa>       -> sayfanın PNG yolu (Read ile bakılır)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pymupdf

from . import config
from .fenomen import TOPICS
from .qbank import fold

DATA = config.DATA / "kitaplik"
OCR_DIR = DATA / "ocr"
PNG_DIR = config.CACHE_DIR / "kitaplik"
INDEX = DATA / "sayfalar.json"
TESS = os.environ.get("TESSERACT", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA = config.ROOT.parent / "tessdata"


def kitap_dir() -> Path:
    p = config.get().get("kitaplik_dir") or str(config.ROOT.parent / "soru bankaları")
    return Path(p)


# ------------------------------------------------------------------ kitaplar
def book_id(path: Path) -> str:
    s = fold(path.stem)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:60]


def short_name(path: Path) -> str:
    """Adreslerde görünen kısa ad: 'Nartest Mod Serisi Soru Bankası 2023'."""
    s = path.stem
    s = re.sub(r"^\d+\s+", "", s)
    s = re.sub(r"\b8\s*\.?\s*(SINIF|sınıf|Sınıf)\b", "", s)
    s = re.sub(r"\bMATEMAT[İI]K\b|\bMatematik\b|\bmatematik\b", "", s)
    s = re.sub(r"[()]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" -")
    fix = {"bankasi": "Bankası", "sinif": "Sınıf", "kitabi": "Kitabı", "donem": "Dönem", "denemelerı": "Denemeleri",
           "seri": "Seri", "ilk": "İlk", "izleme": "İzleme", "sinavi": "Sınavı", "unitesi": "Ünitesi"}
    keep = {"LGS", "SB", "MPS", "VIP", "PSF", "IQ", "BTDS", "KOZ", "KÖK", "YT", "AV", "MEB", "MAT8", "TYT"}
    out = []
    for w in s.split():
        if w.upper() in keep:
            out.append(w.upper())
        elif fold(w) in fix:
            out.append(fix[fold(w)])
        else:
            out.append(w[:1].upper() + w[1:].lower().replace("i̇", "i"))
    return " ".join(out)


def books() -> list[Path]:
    d = kitap_dir()
    return sorted(d.rglob("*.pdf")) if d.is_dir() else []


# ------------------------------------------------------------------ OCR
def _ocr_png(png: Path) -> str:
    env = dict(os.environ, TESSDATA_PREFIX=str(TESSDATA))
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    r = subprocess.run([TESS, str(png), "stdout", "-l", "tur", "--psm", "3"], capture_output=True, env=env,
                       creationflags=flags, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def _ocr_job(args) -> tuple[str, int, str]:
    path, pno = args
    try:
        d = pymupdf.open(path)
        pix = d[pno].get_pixmap(dpi=120, colorspace=pymupdf.csGRAY)
        d.close()
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "p.png"
            pix.save(f)
            return path, pno, _ocr_png(f)
    except Exception as e:  # noqa: BLE001
        return path, pno, f"__HATA__ {e}"


def tara(workers: int = 6, limit: int = 0, log=print) -> None:
    """Her kitabın her sayfasını OCR'lar; data/kitaplik/ocr/<id>.json. Biten kitapları atlar."""
    from multiprocessing import Pool
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    todo = []
    for p in books():
        out = OCR_DIR / f"{book_id(p)}.json"
        if out.exists():
            continue
        todo.append(p)
    if limit:
        todo = todo[:limit]
    log(f"{len(todo)} kitap OCR'lanacak")
    with Pool(workers) as pool:
        for i, p in enumerate(todo, 1):
            t0 = time.time()
            n = pymupdf.open(p).page_count
            pages = [""] * n
            for _, pno, txt in pool.imap_unordered(_ocr_job, [(str(p), k) for k in range(n)], chunksize=2):
                pages[pno] = txt
            (OCR_DIR / f"{book_id(p)}.json").write_text(
                json.dumps({"dosya": p.name, "ad": short_name(p), "sayfalar": pages}, ensure_ascii=False),
                encoding="utf-8")
            log(f"[{i}/{len(todo)}] {p.name} — {n} sayfa, {time.time() - t0:.0f} sn")


# ------------------------------------------------------------------ konu bulma
# kod -> anahtar ifadeler (fold'lu). Başlıkta (sayfanın ilk satırları) geçerse daha çok puan alır.
KEYS = {
    "CK1": ["asal carpan", "pozitif tam sayilarin carpan", "carpan agaci", "carpanlar ve katlar", "bolen sayisi",
            "pozitif carpan", "carpan sayisi"],
    "CK2": ["ebob", "ekok", "en buyuk ortak bolen", "en kucuk ortak kat"],
    "CK3": ["ebob - ekok problem", "ebob ve ekok problem", "ortak bolen", "ortak kat", "ayni anda",
            "tekrar birlikte", "tekrar ayni"],
    "CK4": ["aralarinda asal"],
    "U1": ["tam sayilarin tam sayi kuvvet", "uslu ifadeler", "negatif kuvvet", "kuvveti"],
    "U2": ["uslu ifadelerle ilgili temel kural", "uslu ifadelerde carpma", "uslu ifadelerde bolme", "cozumleme",
           "cozumlenmis"],
    "U3": ["rasyonel sayilarin kuvvet"],
    "U4": ["bilimsel gosterim", "10'un kuvvet", "10 un kuvvet", "ondalik gosterim"],
    "K1": ["tam kare", "tamkare", "karekok", "kokunun", "karekoklu sayilarda tahmin"],
    "K2": ["a√b", "a kok b", "katsayiyi karekok", "farkli bicimlerde gosterim"],
    "K3": ["karekoklu ifadelerde toplama", "karekoklu ifadelerle toplama", "toplama ve cikarma"],
    "K4": ["karekoklu ifadelerde carpma", "karekoklu ifadelerle carpma", "karekoklu ifadelerle bolme",
           "karekoklu ifadelerde bolme"],
    "K5": ["ondalik ifadelerin karekok", "ondalik gosterimlerin karekok"],
    "K6": ["gercek sayilar", "irrasyonel"],    # 'gerçek sayı' bilimsel gösterim tanımında da geçer
    "V": ["veri analizi", "sutun grafig", "daire grafig", "cizgi grafig", "grafik"],
    "O": ["olasilik", "olasilig", "olasi durum", "olma olasiligi"],
    "C1": ["cebirsel ifade"],
    "C2": ["ozdeslik"],
    "C3": ["carpanlara ayirma", "carpanlarina ayir"],
    "D1": ["birinci dereceden bir bilinmeyenli", "denklem"],
    "D2": ["koordinat sistemi", "koordinat", "orijin", "apsis", "ordinat"],
    "D3": ["dogrusal denklem", "dogrusal iliski", "dogrusal degis", "dogrusal olarak", "degisimini gosteren grafik", "dogrunun denklem",
           "dogru denklem",
           "dogrunun grafig", "dogrularin grafig", "dogru grafik",
           "denkleminin grafig"],
    "D4": ["egim"],
    "E": ["esitsizlik"],
    "T1": ["kenarortay", "aciortay", "yardimci eleman"],
    "T2": ["ucgenin kenar", "kenar bagint", "ucgen esitsizlig"],
    "T3": ["aci kenar bagint", "aci-kenar"],
    "T4": ["ucgen cizim", "ucgen insa", "ucgen ciz", "pergel"],
    "T5": ["pisagor", "dik ucgen", "hipotenus"],
    "EB": ["eslik", "benzerlik", "benzer"],
    "DG": ["oteleme", "yansima", "donusum geometri", "otelen", "yansit"],
    "G1": ["prizma"],
    "G2": ["silindir"],
    "G3": ["piramit"],
    "G4": ["koni"],
}
# matematik dışı sayfalar (tüm dersler kitapları)
OTHER = {
    "fen": ["periyodik", "kalitim", "dna", "mevsim", "basinc", "elektrik yuk", "asit", "baz ", "madde dongu",
            "enerji donusum", "besin zinciri", "fotosentez", "gen ", "mitoz", "mayoz", "element", "kimyasal"],
    "turkce": ["paragraf", "fiilimsi", "cumle", "yazim", "noktalama", "sozcuk", "anlatim bozuk", "metin"],
    "inkilap": ["ataturk", "inkilap", "milli mucadele", "osmanli", "kurtulus savas", "cumhuriyet"],
    "din": ["din kulturu", "peygamber", "kuran", "ibadet", "ahlak"],
    "ingilizce": [" the ", " you ", " which ", " friend", " what "],
}
UNIT_OF = {c: TOPICS[c].split(":")[0] for c in TOPICS}
# tüm dersler kitaplarında sayfa üstündeki ders adı ('8. Sınıf Fen Bilimleri | Deneme Sınavı')
DERS_RE = re.compile(r"fen bilimleri|turkce|t\.?c\.? inkilap|inkilap tarihi|din kulturu|ingilizce|english")
# sayfanın herhangi bir yerinde ('TÜRKÇE TESTİ BİTTİ')
DERS_ALT_RE = re.compile(r"(turkce|fen bilimleri|inkilap tarihi|ingilizce) testi|testi bitti|fen bilimleri")


# genel geçen (zayıf) ifadeler 1 puan, diğerleri 2 puan
WEAK = {"kuvveti", "denklem", "grafik", "prizma", "benzer", "koordinat", "ortak kat", "ortak bolen", "karekok",
        "toplama ve cikarma", "tam kare", "dogrusu", "olasi durum"}
# kelime başında aranır: 'karekok' içinde 'ekok' geçer
SHORT = {"ebob", "ekok", "egim", "koni", "orijin"}
# OCR'da √ çoğunlukla 'V' olarak okunur; bilimsel gösterim '6,7 -10*' gibi
ROOT_RE = re.compile(r"(?:√|\bV)\s?\d")
TEN_RE = re.compile(r"\d\s*[-·.x]\s*10\s*[-?'*°\d]")
POW_RE = re.compile(r"\b\d{1,2}\^?\s?\(?-\d\)?")


def _score(text: str) -> Counter:
    t = fold(text)
    sc = Counter()
    for code, keys in KEYS.items():
        for k in keys:
            n = len(re.findall(r"(?<![a-z])" + k, t)) if k in SHORT else t.count(k)
            if n:
                sc[code] += min(n, 3) * (1 if k in WEAK else 2)
    if "cozumle" in t:
        sc["U2"] += 3
    roots = len(ROOT_RE.findall(text))
    if roots:
        sc["K1"] += min(roots, 3)
    tens = len(TEN_RE.findall(text))
    if tens >= 2:
        sc["U4"] += 2
    return sc


def _other(text: str) -> Counter:
    t = " " + fold(text) + " "
    return Counter({d: sum(min(t.count(k), 4) for k in keys) for d, keys in OTHER.items()})


# satır başındaki soru numarası: '7.', '7)', OCR'ın önüne eklediği '* 7.' gibi işaretlerle; '1.Kaset' gibi bitişik değil
QNO = re.compile(r"^[^\w\n]{0,4}(\d{1,2})\s*[.)](?:\s|$)")


def _segments(txt: str) -> tuple[str, list[tuple[int, str]]]:
    """Sayfa metnini başlık + soru parçalarına böler. Numaralar sayfa içinde artan sırada olmalı."""
    head, segs = [], []
    for ln in txt.splitlines():
        if not ln.strip():
            continue
        m = QNO.match(ln)
        if (m and 0 < int(m.group(1)) <= 40 and (not segs or int(m.group(1)) > segs[-1][0])
                and not fold(ln[m.end():m.end() + 6]).startswith("sinif")):   # '8. Sınıf Matematik' başlığı
            segs.append([int(m.group(1)), ln])
        elif segs:
            segs[-1][1] += "\n" + ln
        else:
            head.append(ln)
    return "\n".join(head), [(n, s) for n, s in segs]


def _best(sc: Counter, en_az: int) -> tuple[str | None, int]:
    """En yüksek puanlı konu; en az `en_az` puan ve ikinciden açıkça yüksek olmalı (ya da 4+ puan)."""
    top = sc.most_common(2)
    if not top:
        return None, 0
    code, v = top[0]
    second = top[1][1] if len(top) > 1 else 0
    if v >= 4 or (v >= en_az and v > second):
        return code, v
    return None, 0


def _deneme(name: str) -> bool:
    return bool(re.search(r"deneme|dnm|kamp|karma|son \d+ soru|tekrar|izleme|kazanim\b.*sinav", fold(name)))


def siniflandir(log=print) -> list[dict]:
    """OCR metinlerinden her sorunun konusunu çıkarır. Soru metninde konu belli değilse sayfa başlığının konusu,
    o da yoksa (konu kitaplarında) önceki sayfaların başlık konusu kullanılır. Deneme kitaplarında soru tek tek."""
    rows = []
    for f in sorted(OCR_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        bid, karma = f.stem, _deneme(d["dosya"])
        prev, prev_age = None, 99
        for i, txt in enumerate(d["sayfalar"], 1):
            if len(txt.strip()) < 40:
                continue
            oth = _other(txt)
            mat_sc = _score(txt)
            if max(oth.values()) >= 4 and max(oth.values()) > sum(mat_sc.values()):
                continue                       # matematik dışı sayfa (tüm dersler kitapları)
            ust = fold(txt[:250])
            if "icindekiler" in fold(txt[:400]):
                continue                       # içindekiler sayfası
            if (DERS_RE.search(ust) and "matematik" not in ust) or (
                    DERS_ALT_RE.search(fold(txt)) and "matematik" not in fold(txt)):
                continue                       # başlıkta başka ders adı
            head, segs = _segments(txt)
            head_code, head_v = _best(_score(head), 1)
            page_code = head_code
            if not page_code and not karma and prev and prev_age <= 3:
                page_code = prev
            if head_code:
                prev, prev_age = head_code, 0
            else:
                prev_age += 1
            base = {"kitap": bid, "ad": d["ad"], "dosya": d["dosya"], "sayfa": i}
            if not segs:
                code, v = _best(mat_sc, 3)
                code = code or page_code
                if code:
                    rows.append({**base, "soru": 0, "kod": code, "konu": TOPICS[code], "ek_konu": [], "guven": v})
                continue
            for no, s in segs:
                sc = _score(s)
                code, v = _best(sc, 1)
                if page_code and (not code or v < 2):
                    code, v = page_code, 1     # zayıf tek kelime, sayfa başlığındaki konuyu geçemez
                if not code:
                    continue
                if code == "CK2" and len(s) > 220:
                    code = "CK3"               # uzun sözel EBOB-EKOK sorusu = problem
                ek = [c for c, x in sc.most_common(3) if c != code and x >= 2 and UNIT_OF[c] != UNIT_OF[code]]
                rows.append({**base, "soru": no, "kod": code, "konu": TOPICS[code],
                             "ek_konu": [TOPICS[c] for c in ek[:1]], "guven": v})
    DATA.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    load.cache_clear()
    log(f"{len(rows)} soru/sayfa kaydı, {len({r['kitap'] for r in rows})} kitap")
    return rows


@lru_cache(maxsize=1)
def load() -> list[dict]:
    return json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else []


@lru_cache(maxsize=64)
def _ocr_text(bid: str) -> list[str]:
    f = OCR_DIR / f"{bid}.json"
    return json.loads(f.read_text(encoding="utf-8"))["sayfalar"] if f.exists() else []


def _terms(s):
    return [fold(t) for t in (s or "").split(",") if t.strip()]


def _soru_text(r: dict) -> str:
    txt = _ocr_text(r["kitap"])[r["sayfa"] - 1]
    return dict(_segments(txt)[1]).get(r["soru"], txt) if r["soru"] else txt


def ara(topic=None, text=None, book=None, limit=20, topic_all=None) -> list[dict]:
    """topic: konu adında (VEYA); topic_all: hepsi; text: sayfanın OCR metninde geçen kelimeler (çok eşleşen öne)."""
    any_t, all_t, txt = _terms(topic), _terms(topic_all), _terms(text)
    res = []
    for r in load():
        if book and fold(book) not in r["kitap"] and fold(book) not in fold(r["ad"]):
            continue
        hay = fold(r["konu"] + " | " + " ".join(r["ek_konu"]))
        if any_t and not any(t in hay for t in any_t):
            continue
        if all_t:
            # en az biri konu etiketinde, diğerleri etikette ya da sorunun kendi metninde
            if not any(t in hay for t in all_t):
                continue
            if not all(t in hay for t in all_t) and not all(t in hay or t in fold(_soru_text(r)) for t in all_t):
                continue
        score = 0
        if txt:
            body = fold(_ocr_text(r["kitap"])[r["sayfa"] - 1])
            score = sum(t in body for t in txt)
            if not score:
                continue
        res.append((score, r["guven"], r))
    res.sort(key=lambda x: (-x[0], -x[1]))
    # aynı kitaptan çok sayfa gelmesin: kitap başına en fazla 3 sayfa
    out, per = [], Counter()
    for _, _, r in res:
        if per[r["kitap"]] >= 3:
            continue
        per[r["kitap"]] += 1
        out.append(r)
        if len(out) >= limit:
            break
    return out


def sayfa_png(bid: str, pno: int, dpi: int = 110) -> Path:
    r = next((x for x in load() if x["kitap"] == bid), None)
    if not r:
        raise SystemExit(f"kitap yok: {bid}")
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    out = PNG_DIR / f"{bid}_s{pno}_{dpi}.png"
    if not out.exists():
        d = pymupdf.open(kitap_dir() / r["dosya"])
        d[pno - 1].get_pixmap(dpi=dpi).save(out)
        d.close()
    return out


def ref(r: dict) -> str:
    """Kitapta bulmak için adres: 'Nartest Mod Serisi Soru Bankası 2023 s.45 S3' (s = PDF sayfası)."""
    return f"{r['ad']} s.{r['sayfa']}" + (f" S{r['soru']}" if r.get("soru") else "")


def ozet() -> None:
    by = {}
    for r in load():
        by.setdefault(r["kitap"], []).append(r)
    for bid, rs in sorted(by.items()):
        kon = Counter(r["kod"] for r in rs)
        print(f"{rs[0]['ad'][:48]:48} | {len({r['sayfa'] for r in rs}):4} sayfa | {len(rs):5} kayıt | "
              f"{', '.join(f'{k}:{v}' for k, v in kon.most_common(6))}")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m app.kitaplik")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tara"); t.add_argument("--workers", type=int, default=6); t.add_argument("--limit", type=int, default=0)
    sub.add_parser("siniflandir")
    sub.add_parser("ozet")
    a_ = sub.add_parser("ara")
    for x in ("--topic", "--text", "--book"):
        a_.add_argument(x)
    a_.add_argument("--topic-all", dest="topic_all")
    a_.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("sayfa"); s.add_argument("kitap"); s.add_argument("sayfa", type=int)
    a = ap.parse_args(argv)
    if a.cmd == "tara":
        tara(a.workers, a.limit)
    elif a.cmd == "siniflandir":
        siniflandir()
    elif a.cmd == "ozet":
        ozet()
    elif a.cmd == "ara":
        rows = ara(a.topic, a.text, a.book, a.limit, a.topic_all)
        if not rows:
            print("Eşleşen sayfa yok; terimleri genişletin.")
        for r in rows:
            print(f"{ref(r):55} | {r['konu'][:55]}{' | ek konu: ' + r['ek_konu'][0] if r['ek_konu'] else ''}"
                  f"\n    görsel: python -m app.kitaplik sayfa {r['kitap']} {r['sayfa']}")
    elif a.cmd == "sayfa":
        print(sayfa_png(a.kitap, a.sayfa))


if __name__ == "__main__":
    main()
