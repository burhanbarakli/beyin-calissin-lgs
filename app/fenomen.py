"""Öğrencinin elindeki basılı soru bankaları için sayfa/soru indeksi: Fenomen 8A/8B ve Ankara Güçlendiren.

Kitaplar şifreli uygulamada olduğu için soruların kendisi bankada yok; öğrencinin elindeki basılı
kitaptan bulunsun diye yalnızca kitap, sayfa, soru numarası, konu ve kısa beceri etiketi tutulur.
Kaynaklar (Claude'un kitapları sayfa sayfa inceleyerek yazdığı etiketler):
  kaynaklar/Fenomen/fenomen_8_mat_2026.tsv, kaynaklar/Ankara/ankara_8_mat_gsb_2025.tsv

8A ve Ankara sayfaları basılı sayfa numarasıdır. 8B ünite başına sayfalanır: "2-9" = 2. ünite, 9. sayfa.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from .qbank import fold

_KAYNAK = Path(__file__).resolve().parent.parent / "kaynaklar"
TSVS = [_KAYNAK / "Fenomen" / "fenomen_8_mat_2026.tsv", _KAYNAK / "Ankara" / "ankara_8_mat_gsb_2025.tsv"]

BOOKS = {"8A": "2026 Fenomen 8. Sınıf Matematik A Soru Bankası",
         "8B": "2026 Fenomen 8. Sınıf Matematik B Soru Bankası",
         "Ankara": "2025 Ankara Yayıncılık 8. Sınıf Matematik Güçlendiren Soru Bankası"}
# Fenomen türleri kısa kodla; Ankara'da tür sütunu test adıdır (Konu Testi / Geçiş Testi / Beceri Temelli Test)
TYPES = {"K": "Kazanım", "I": "Kalıplaşmış İkiz", "Y": "Yeni Nesil"}

# indeksteki kısa konu kodları → sistemin "Ünite: Kazanım" konu adları
TOPICS = {
    "CK1": "Çarpanlar ve Katlar: Çarpanlar ve Asal Çarpanlar",
    "CK2": "Çarpanlar ve Katlar: EBOB - EKOK",
    "CK3": "Çarpanlar ve Katlar: EBOB - EKOK Problemleri",
    "CK4": "Çarpanlar ve Katlar: Aralarında Asal Sayılar",
    "U1": "Üslü İfadeler: Tam Sayıların Tam Sayı Kuvvetleri",
    "U2": "Üslü İfadeler: Üslü İfadelerle İlgili Temel Kurallar ve Çözümleme",
    "U3": "Üslü İfadeler: Rasyonel Sayıların Kuvvetleri",
    "U4": "Üslü İfadeler: 10'un Kuvvetleriyle İfade Etme ve Bilimsel Gösterim",
    "K1": "Kareköklü İfadeler: Tam Kare Sayılar ve Kareköklü Sayılarda Tahmin",
    "K2": "Kareköklü İfadeler: a kök b Şeklinde Yazma ve Katsayıyı Karekök İçine Alma",
    "K3": "Kareköklü İfadeler: Kareköklü İfadelerle Toplama ve Çıkarma İşlemi",
    "K4": "Kareköklü İfadeler: Kareköklü İfadelerle Çarpma ve Bölme İşlemi",
    "K5": "Kareköklü İfadeler: Ondalık İfadelerin Karekökleri",
    "K6": "Kareköklü İfadeler: Gerçek Sayılar",
    "V": "Veri Analizi: Veri Analizi",
    "O": "Basit Olayların Olma Olasılığı: Olasılık",
    "C1": "Cebirsel İfadeler ve Özdeşlikler: Cebirsel İfadeler",
    "C2": "Cebirsel İfadeler ve Özdeşlikler: Özdeşlikler",
    "C3": "Cebirsel İfadeler ve Özdeşlikler: Çarpanlara Ayırma",
    "D1": "Doğrusal Denklemler: Birinci Dereceden Bir Bilinmeyenli Denklemler",
    "D2": "Doğrusal Denklemler: Koordinat Sistemi",
    "D3": "Doğrusal Denklemler: Doğrusal Denklemler",
    "D4": "Doğrusal Denklemler: Eğim",
    "E": "Eşitsizlikler: Eşitsizlikler",
    "T1": "Üçgenler: Üçgende Kenarortay, Açıortay ve Yükseklik",
    "T2": "Üçgenler: Üçgenin Kenarları Arasındaki İlişki",
    "T3": "Üçgenler: Üçgende Açı Kenar Bağıntıları",
    "T4": "Üçgenler: Üçgen Çizimleri",
    "T5": "Üçgenler: Pisagor Bağıntısı",
    "EB": "Eşlik ve Benzerlik: Eşlik ve Benzerlik",
    "DG": "Dönüşüm Geometrisi: Dönüşüm Geometrisi",
    "G1": "Geometrik Cisimler: Prizmalar",
    "G2": "Geometrik Cisimler: Silindir",
    "G3": "Geometrik Cisimler: Piramit",
    "G4": "Geometrik Cisimler: Koni",
}


def page_label(book: str, page: str) -> str:
    if "-" in page:
        unit, p = page.split("-", 1)
        return f"Ünite {unit} s.{p}"
    return f"s.{page}"


def ref(q: dict) -> str:
    """Kitapta bulmak için kısa adres: '8B Ünite 2 s.9 S1'."""
    return f"{q['kitap']} {page_label(q['kitap'], q['sayfa'])} S{q['soru']}"


@lru_cache(maxsize=1)
def load() -> list[dict]:
    out = []
    for tsv in TSVS:
        if not tsv.exists():
            continue
        with tsv.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out.append({
                    "kitap": r["kitap"], "sayfa": r["sayfa"], "soru": int(r["soru"]),
                    "tur": TYPES.get(r["tur"], r["tur"]),
                    "konu": TOPICS.get(r["konu"], r["konu"]),
                    "ek_konu": r["ek_konu"], "beceri": r["beceri"], "zorluk": int(r["zorluk"] or 0),
                })
    for q in out:
        q["ref"] = ref(q)
        if q["ek_konu"]:
            q["ek_konu"] = _full_topic(q["ek_konu"], q["konu"])
    return out


def _full_topic(name: str, main: str) -> str:
    """Ek konudaki kısa adı ('Temel Kurallar', 'a kök b') tam konu adına çevirir; önce ana konunun ünitesine bakar."""
    k = fold(name).replace("birinci dereceden denklemler", "birinci dereceden bir bilinmeyenli")
    hits =[t for t in TOPICS.values() if k and k in fold(t)]
    if not hits:
        return name
    unit = main.split(":")[0]
    same = [t for t in hits if t.startswith(unit)]
    return (same or hits)[0]


def _terms(s: str | None) -> list[str]:
    return [fold(t) for t in (s or "").split(",") if t.strip()]


def search(topic: str | None = None, text: str | None = None, topic_all: str | None = None,
           book: str | None = None, kind: str | None = None, min_zorluk: int = 0, max_zorluk: int = 5,
           limit: int = 30) -> list[dict]:
    """topic: virgüllü terimlerden biri konu/ek konu/becerede geçmeli (VEYA).
    topic_all: hepsi geçmeli (VE). text: virgüllü terimlerden biri beceride geçmeli; çok eşleşen öne gelir."""
    any_t, all_t, txt = _terms(topic), _terms(topic_all), _terms(text)
    res = []
    for q in load():
        if book and q["kitap"].lower() != book.lower() and not (book.lower() == "fenomen" and q["kitap"] in ("8A", "8B")):
            continue
        if kind and fold(kind) not in fold(q["tur"]):
            continue
        if not (min_zorluk <= q["zorluk"] <= max_zorluk):
            continue
        hay = fold(f"{q['konu']} | {q['ek_konu']} | {q['beceri']}")
        if any_t and not any(t in hay for t in any_t):
            continue
        if all_t and not all(t in hay for t in all_t):
            continue
        score = sum(t in fold(q["beceri"]) for t in txt)
        if txt and not score:
            continue
        res.append((score, q))
    res.sort(key=lambda x: (-x[0], x[1]["zorluk"], x[1]["kitap"]))
    return [q for _, q in res[:limit]]


def topics() -> list[tuple[str, int]]:
    cnt: dict[str, int] = {}
    for q in load():
        cnt[q["konu"]] = cnt.get(q["konu"], 0) + 1
    return sorted(cnt.items())
