# Beyin Çalışsın — proje rehberi

LGS (8. sınıf) öğrencisinin yapamadığı soruların fotoğraflarına göre, soru bankasından (kerimhoca.com
çalışma kağıtları, kazanım testleri, konu tarama testleri, 2018-2026 LGS çıkmış soruları, MEB LGS Çalışma Kitabı
ve MEBİ LGS denemeleri) benzer ve öğretici
sorular seçip PDF çalışma kâğıdı üreten yerel web uygulaması. Şu an yalnızca matematik var; fen sonra eklenecek.
"Beyin" = bu bilgisayardaki Claude Code'un headless (`claude -p`) çalıştırılması.

Kurulu sürüm: `VERSION`. Sürüm notları: `GUNCELLEME.md`. Kullanıcı kılavuzu: `docs/KILAVUZ.md`.

## Kullanıcıya yardım eden Claude isen (kurulum / güncelleme / "ne yeni?")

Bu klasörü kullanıcı (öğretmen/veli) kendi bilgisayarında çalıştırıyor ve kurulum/güncelleme için seni kullanıyor.
Teknik terimleri azalt, Türkçe ve adım adım konuş.

### Güncelleme ("sistemi güncelle", "GitHub'dan yeni sürümü al" vb.)

Repo: `https://github.com/burhanbarakli/beyin-calissin-lgs` (özel; eski TYT/AYT sürümü `beyin-calissin`). Repoda kodla birlikte **öğrenci verisi**
(`ogrenci/`, `data/`) ve kaynak PDF'ler (`kaynaklar/`) de vardır. Kullanıcı kendi bilgisayarında fotoğraf
yükleyip beyin çalıştırdığı için `ogrenci/` ve `data/` **onun güncel verisidir — asla üzerine yazma, silme.**

1. Kurulu sürümü oku: `VERSION` (yoksa 1.0.0 say).
2. Sunucu açıksa kullanıcıdan siyah `baslat.bat` penceresini kapatmasını iste (ya da 8765 portundaki python sürecini durdur).
3. **Yedek al:** `ogrenci/`, `data/` ve `config.json`'u bir üst klasöre `beyin-yedek-<tarih>/` olarak kopyala.
4. **Sadece kodu güncelle:**
   - Klasör bir git deposuysa (`.git` var):
     `git fetch origin` ardından
     `git checkout origin/main -- app brain docs .claude/agents kaynaklar/Fenomen kaynaklar/Ankara README.md CLAUDE.md GUNCELLEME.md VERSION requirements.txt baslat.bat config.example.json`
     (`git pull` KULLANMA — kullanıcının veri değişiklikleriyle çakışır.)
   - Git deposu değilse (ZIP ile kurulmuş): repoyu geçici bir klasöre indir (`git clone` ya da ZIP) ve yalnızca
     yukarıdaki kod yollarını bu klasörün üzerine kopyala. `ogrenci/`, `data/`, `kaynaklar/`, `config.json`'a dokunma.
     Yeni sürümde `kaynaklar/` altında olmayan yeni bir PDF varsa onu da ekleyebilirsin (mevcutları silme).
   - Her iki durumda da **yeni kaynaklar** için: `kaynaklar/LGS_Matematik/katalog.json`'u yenisiyle değiştir, yerelde
     olmayan PDF'leri ve `data/index/` altında yerelde olmayan indeks dosyalarını kopyala (var olan indeksleri ezme).
     `data/ratings.json`'a yalnızca yerelde olmayan qid'leri ekle (birleştir, mevcut kayıtları değiştirme).
5. `python -m pip install -r requirements.txt` (sessizce; yeni paket yoksa bir şey değişmez).
6. Yeni `VERSION`'ı oku; `GUNCELLEME.md`'de **eski sürümden yeni olan bölümleri** kullanıcıya kısaca özetle ve
   her bölümdeki **"Yapmanız gereken"** satırını söyle.
7. `baslat.bat`'ı başlat (ya da kullanıcıya çift tıklamasını söyle) ve sağ üstte "Claude Code bulundu" yazısını kontrol ettir.
8. Bir şey ters giderse 3. adımdaki yedekten `ogrenci/` ve `data/`'yı geri koy.

### "Ne yeni?" / "Bu sürümde neler var?"

`GUNCELLEME.md`'yi oku ve en üstteki (ya da kullanıcının sorduğu) sürümü özetle. Ayrıntılı kullanım için `docs/KILAVUZ.md`.

### İlk kurulum

`docs/KILAVUZ.md` → "0. İlk kurulum" bölümünü izle (Python 3.12, Claude Code + `/login`, `baslat.bat`).

## Beyin olarak çalışıyorsan

Prompt sana hangi talimat dosyasını (`brain/BRAIN.md`) uygulayacağını ve `RUN_DIR`'i söyler. O dosyayı oku ve
adımları izle. Soru bankası komutları için: `python -m app.qbank --help`. Kaynak kodu değiştirme; sadece
`RUN_DIR` içine yaz. Derin analiz modunda `soru-analisti` alt ajanını (`.claude/agents/soru-analisti.md`) kullanırsın.
**Yukarıdaki "Kullanıcıya yardım eden Claude" bölümü sana uygulanmaz.**

## Yapı

- `app/server.py` — FastAPI sunucusu + `app/static/` tek ekranlık arayüzü (Chrome'dan `http://localhost:8765`):
  fotoğraf yükle (`ogrenci/Sorular/<tarih>/`) → beyin → adayları seç → PDF; altta önceki çalışmalar
- `kaynaklar/LGS_Matematik/` — kaynak PDF'ler (ünite klasörleri + `00_LGS_Cikmis_Sorular`, `13_MEBI_Denemeler`,
  `14_MEB_Calisma_Kitabi` — MEB kitabı ünite ünite bölünmüş, s. 7-298); `katalog.json` her PDF'in türünü, ünitesini
  ve kazanımını verir (yeni PDF eklerken buraya da kayıt ekle). İsteğe bağlı alanlar: `id` (kitap kimliği),
  `key` (ayrı yerde duran cevap anahtarı `{"1": "C"}`), `ignore_rects` (kırpıma girmesin diye sayfa süsleri)
- `kaynaklar/Fenomen/fenomen_8_mat_2026.tsv` + `app/fenomen.py` — öğrencinin basılı Fenomen 8A/8B soru bankalarının
  sayfa/soru no indeksi (konu, tür, beceri, zorluk; soru metni ve görsel yok). `python -m app.qbank fenomen`;
  beyin gruplara `fenomen` önerisi ekler, arayüz ve PDF listeler. Güncellemede bu klasörü de kopyala.
- `kaynaklar/Ankara/ankara_8_mat_gsb_2025.tsv` — aynı biçimde Ankara Yayıncılık 2025 8. Sınıf Matematik Güçlendiren
  Soru Bankası indeksi (1009 soru, kitap kodu `Ankara`). `app/fenomen.py` iki kitap setini birlikte okur;
  `qbank fenomen --book Ankara`. Güncellemede bu klasörü de kopyala.
- `app/indexer.py` — kaynak PDF'lerden yapay zekâsız soru indeksi (sayfa, kırpma kutusu, konu, seviye, cevap
  anahtarı) → `data/index/*.json`. Metni bozuk PDF'lerde soruları renkli numara kutularından bulur.
- `app/qbank.py` — soru bankası sorgu/CLI aracı (beyin bunu kullanır), birleşik zorluk hesabı;
  `label` komutu Claude'un soru etiketlerini (konu, beceri, rol, zorluk) işler — etiketler yeniden indekslemede korunur
- `app/runner.py` — Claude Code işlerini başlatır, stream-json akışını `data/runs/<id>/` altına kaydeder
- `app/pdfgen.py` — seçilen soruları vektör olarak A4 PDF'e dizer, cevap anahtarı ekler
- `app/pack.py` — paylaşım paketi (kod + veri + kaynaklar) oluşturur
- `brain/BRAIN.md` — beyin görev talimatı; `.claude/agents/soru-analisti.md` — derin analiz ajanı

## Geliştirme notları

- Python 3.10+; bağımlılıklar `requirements.txt`. Çalıştırma: `python -m app.server` (veya `baslat.bat`).
  Bu Mac'te proje içi `.venv` (Python 3.12) var: `.venv/bin/python -m app.server`.
- İndeksi yeniden üretmek: `python -m app.indexer --force` (cevaplar ve etiketler korunur).
  İndekslerde PDF yolu program klasörüne göreli yazılır; başka bilgisayarın yolunu taşıyan eski indeksler için
  `python -m app.indexer --relink` (yalnızca yolları düzeltir).
- Windows'ta konsol kodlaması sorun çıkarır: CLI çıktıları `sys.stdout.reconfigure(encoding="utf-8")` ile yazılır.
- Yeni sürüm çıkarırken: `VERSION`'ı artır, `GUNCELLEME.md`'ye en üste bölüm ekle (Yeni / Düzeltmeler / Yapmanız gereken).
