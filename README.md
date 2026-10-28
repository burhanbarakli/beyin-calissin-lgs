# 🧠 Beyin Çalışsın

LGS (8. sınıf) öğrencisinin **yapamadığı soruların fotoğrafına** bakıp eksik beceriyi teşhis eden ve
soru bankasındaki **gerçek sorulardan** öğretici → pekiştirme → zorlayıcı sıralı bir çalışma kâğıdı (PDF)
hazırlayan yerel web uygulaması. Şu an LGS matematik; fen sonra eklenecek.

"Beyin", uygulamanın çalıştığı bilgisayardaki **Claude Code**'dur (`claude -p`).

> 📖 **Kılavuz:** [docs/KILAVUZ.md](docs/KILAVUZ.md) · 🆕 **Yenilikler:** [GUNCELLEME.md](GUNCELLEME.md) ·
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

`kaynaklar/LGS_Matematik/` — kerimhoca.com 8. sınıf matematik dosyaları (84 PDF, 935 soru):

| Tür | Soru | Rol |
|---|---|---|
| Çalışma kâğıtları (kazanım başına) | 223 | Öğretici — açık uçlu alıştırma |
| Kazanım testleri | 360 | İlk yarı temel, ikinci yarı orta (cevabı beyin çözer) |
| Konu tarama testleri | 172 | Pekiştirme — yeni nesil, cevaplı |
| LGS çıkmış sorular 2018-2026 | 180 | Zorlayıcı — cevaplı |

Tarama ve çıkmış soruların hepsi Claude tarafından kazanım, ölçtüğü beceri ve 1-5 zorlukla
etiketlenmiştir. `katalog.json` her PDF'in türünü, ünitesini ve kazanımını verir.

## Kurulum

- Python 3.10+ ve **Claude Code** (bir kez `claude` → `/login`).
- Windows: `baslat.bat`'a çift tıklayın. Mac/Linux: `python3 -m pip install -r requirements.txt`, sonra
  `python3 -m app.server`. Tarayıcıda `http://localhost:8765` açılır.

## Mimari

| Dosya | Görev |
|---|---|
| `app/server.py` | FastAPI sunucusu: yükleme, beyin, adaylar, PDF |
| `app/static/` | Tek ekranlık arayüz (bağımlılıksız) |
| `app/indexer.py` | Kaynak PDF → soru indeksi (sayfa, kırpma kutusu, konu, seviye, cevap anahtarı) |
| `app/qbank.py` | Soru bankası arama/görsel/etiket CLI'ı: `python -m app.qbank --help` |
| `app/runner.py` | Claude Code'u headless başlatır, akışı `data/runs/<id>/` altına kaydeder |
| `app/pdfgen.py` | Vektör kırpımlarla A4 PDF |
| `brain/BRAIN.md` | Beynin görev talimatı |
| `.claude/agents/soru-analisti.md` | Derin analiz ajanı |

Claude'un izinleri `app/runner.py` içindeki `ALLOWED_TOOLS` listesiyle sınırlıdır: dosya okuma/yazma
ve `python` komutları.

İndeksi yeniden üretmek: `python -m app.indexer --force` (cevaplar ve etiketler korunur).

## Gizlilik

Beyin çalışırken öğrencinin soru fotoğrafları Claude'a (Anthropic) gönderilir. Fotoğraflar yerelde
`ogrenci/Sorular/` altında, çalışmalar ve PDF'ler `data/` altında durur.

## Sorun giderme

- **"Claude Code oturumu açık değil":** Terminalde `claude` çalıştırıp `/login` ile giriş yapın.
- **"Claude Code bulunamadı":** ⚙ Ayarlar'a `claude` yolunu yazın.
