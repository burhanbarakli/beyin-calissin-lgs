# 🧠 Beyin Çalışsın

LGS (8. sınıf) öğrencisinin **yapamadığı soruların fotoğrafına** bakıp eksik beceriyi teşhis eden ve
soru bankasındaki **gerçek sorulardan** öğretici → pekiştirme → zorlayıcı sıralı bir çalışma kâğıdı (PDF)
hazırlayan yerel web uygulaması. Şu an LGS matematik; fen sonra eklenecek.

"Beyin", uygulamanın çalıştığı bilgisayardaki **Claude Code**'dur (`claude -p`).

> 📖 **Kılavuz:** [docs/KILAVUZ.md](docs/KILAVUZ.md) · 🆕 **Yenilikler:** [GUNCELLEME.md](GUNCELLEME.md) ·
> 🔒 **Kaynaklar ve veri:** [docs/KAYNAKLAR_VE_VERI.md](docs/KAYNAKLAR_VE_VERI.md) ·
> **Güncellemek için** Claude Code'a bu klasörde *"sistemi GitHub'dan güncelle"* demeniz yeterli;
> verileriniz korunur (ayrıntı: `CLAUDE.md`).

![Aday sorular](docs/img/2-adaylar.jpg)

```
1 · Yapamadığı soruların fotoğrafları (sürükle / yapıştır / seç)
        │
        ▼
2 · 🧠 Claude Code: fotoğrafı çözer, eksik beceriyi bulur ──► soru bankasında benzerini arar
        │
        ▼
3 · Aday sorular: Öğretici → Pekiştirme → Zorlayıcı (öğretmen seçer)
        │
        ▼
4 · 📄 A4 PDF: yapamadığı sorular + seçilen sorular + cevap anahtarı
```

## Soru bankası

`kaynaklar/LGS_Matematik/` — 102 PDF, 1679 soru:

| Tür | Kaynak | Soru | Rol |
|---|---|---|---|
| Çalışma kâğıtları (kazanım başına) | kerimhoca.com | 223 | Öğretici — açık uçlu alıştırma |
| Kazanım testleri | kerimhoca.com | 360 | İlk yarı temel, ikinci yarı orta (cevabı beyin çözer) |
| Konu tarama testleri | kerimhoca.com | 172 | Pekiştirme — yeni nesil, cevaplı |
| LGS çıkmış sorular 2018-2026 | kerimhoca.com | 180 | Zorlayıcı — cevaplı |
| MEB LGS Çalışma Kitabı (6 ünite) | odsgm.meb.gov.tr | 504 | Pekiştirme / zorlayıcı — LGS tarzı, cevaplı |
| MEBİ LGS denemeleri 1-12 (matematik) | kerimhoca.com (MEB) | 240 | Pekiştirme / zorlayıcı — cevaplı |

Kazanım testi ve çalışma kâğıdı dışındaki soruların hepsi Claude tarafından kazanım, ölçtüğü beceri ve 1-5 zorlukla
etiketlenmiştir. `katalog.json` her PDF'in türünü, ünitesini ve kazanımını verir.

### Basılı kitap indeksleri

Öğrencinin elindeki basılı soru bankalarının soruları sistemde **yok**. Sistemde yalnızca her sorunun adresi
(kitap, sayfa, soru no) ve Claude'un kısa sınıflandırması var. Beyin bunlardan da benzer soru önerir, öğrenci
soruyu kitaptan bulup çözer.

| Kitap | Kod | Soru | Dosya |
|---|---|---|---|
| 2026 Fenomen 8. Sınıf Matematik A / B Soru Bankası | `8A` / `8B` | 1357 + 557 | `kaynaklar/Fenomen/` |
| 2025 Ankara Yayıncılık 8. Sınıf Matematik Güçlendiren Soru Bankası | `Ankara` | 1009 | `kaynaklar/Ankara/` |

### Öğretmen kitaplığı (yalnızca bu bilgisayarda)

Yayınevlerinin öğretmene verdiği yaklaşık 160 PDF soru bankası ve deneme `tuna beyin/soru bankaları/` klasöründe durur.
Sayfaları Tesseract OCR ile okunup her soruya otomatik konu verilir (`python -m app.kitaplik`). Beyin uygun sayfaları
açıp kontrol ederek soru önerir. PDF'ler, OCR metni ve indeks GitHub'a gönderilmez (`data/kitaplik/`, `.gitignore`).

Ayrıntı: [docs/KAYNAKLAR_VE_VERI.md](docs/KAYNAKLAR_VE_VERI.md).

## Kurulum

- Python 3.10+ ve **Claude Code** (bir kez `claude` → `/login`).
- Windows: `baslat.bat`'a çift tıklayın. Mac/Linux: `python3 -m pip install -r requirements.txt`, sonra
  `python3 -m app.server`. Tarayıcıda `http://localhost:8765` açılır.

## Mimari

| Dosya | Görev |
|---|---|
| `app/server.py` | FastAPI sunucusu: yükleme, beyin, adaylar, PDF |
| `app/static/` | Tek ekranlık arayüz (bağımlılıksız) |
| `app/fenomen.py` | Basılı kitap indeksleri (Fenomen 8A/8B, Ankara): `python -m app.qbank fenomen` |
| `app/kitaplik.py` | Öğretmen kitaplığı PDF'leri: OCR, soru-konu indeksi, arama, sayfa görseli |
| `app/indexer.py` | Kaynak PDF → soru indeksi (sayfa, kırpma kutusu, konu, seviye, cevap anahtarı) |
| `app/qbank.py` | Soru bankası arama/görsel/etiket CLI'ı: `python -m app.qbank --help` |
| `app/runner.py` | Claude Code'u headless başlatır, akışı `data/runs/<id>/` altına kaydeder |
| `app/pdfgen.py` | Vektör kırpımlarla A4 PDF |
| `brain/BRAIN.md` | Beynin görev talimatı |
| `.claude/agents/soru-analisti.md` | Derin analiz ajanı |

Claude'un izinleri `app/runner.py` içindeki `ALLOWED_TOOLS` listesiyle sınırlıdır: dosya okuma/yazma
ve `python` komutları.

İndeksi yeniden üretmek: `python -m app.indexer --force` (cevaplar ve etiketler korunur).

## Kaynaklar ve veri kullanımı

Ayrıntılı açıklama [docs/KAYNAKLAR_VE_VERI.md](docs/KAYNAKLAR_VE_VERI.md) belgesindedir. Kısaca:

- **Claude'a gönderilen:** Beyin çalışırken öğrencinin soru fotoğrafları Claude'a (Anthropic) gönderilir.
- **Bu bilgisayarda kalan:** Fotoğraflar `ogrenci/Sorular/` altında, çalışmalar, PDF'ler ve puanlar `data/` altında durur.
- **GitHub'a gidenler:** Kod, belgeler ve kaynak indeksleri gider. Bu bilgisayardaki öğrenci verisi gönderilmez.
  Depo herkese açık olduğu için gizlilik isteniyorsa depo **Private** yapılmalı.
- **Telif:** Kaynakların hakları sahiplerine aittir. Sistem kişisel eğitim içindir. Basılı kitapların yalnızca
  adres indeksi tutulur; kitap içeriği kopyalanmaz.

## Sorun giderme

- **"Claude Code oturumu açık değil":** Terminalde `claude` çalıştırıp `/login` ile giriş yapın.
- **"Claude Code bulunamadı":** ⚙ Ayarlar'a `claude` yolunu yazın.
