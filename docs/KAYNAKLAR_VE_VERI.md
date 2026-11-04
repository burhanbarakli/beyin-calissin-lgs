# Kaynaklar ve veri kullanımı

Bu belge, Beyin Çalışsın'ın hangi kaynakları kullandığını, öğrenci verisini nerede tuttuğunu, neyi Claude'a
(Anthropic) gönderdiğini ve neyin GitHub'a gittiğini anlatır. Son güncelleme: 1 Kasım 2026 (sürüm 2.8.0).

---

## 1. Soru bankası: sistemin içindeki sorular

`kaynaklar/LGS_Matematik/` altındaki **102 PDF, 1679 soru**. Sorular bu PDF'lerden kırpılarak çalışma kâğıdına konur.

| Tür | Kaynak | Soru | Rol |
|---|---|---|---|
| Çalışma kâğıtları (kazanım başına) | kerimhoca.com | 223 | Öğretici, açık uçlu alıştırma |
| Kazanım testleri | kerimhoca.com | 360 | Temel ve orta (cevabı beyin çözer) |
| Konu tarama testleri | kerimhoca.com | 172 | Pekiştirme, yeni nesil, cevaplı |
| LGS çıkmış sorular 2018–2026 | kerimhoca.com | 180 | Zorlayıcı, cevaplı |
| MEB LGS Çalışma Kitabı (6 ünite) | odsgm.meb.gov.tr | 504 | Pekiştirme ve zorlayıcı, cevaplı |
| MEBİ LGS denemeleri 1–12 (matematik) | kerimhoca.com (MEB) | 240 | Pekiştirme ve zorlayıcı, cevaplı |

- **İndeks:** `data/index/*.json`. Her sorunun sayfası, kırpma kutusu, konusu ve cevabı burada tutulur. PDF yolları program klasörüne göreli yazılır (`kaynaklar/...`), böylece aynı indeks Mac'te ve Windows'ta çalışır.
- **Etiketler:** Konu, beceri, rol ve 1–5 zorluk etiketleri Claude'un tahminidir. Bir soru birden çok kazanım kullanıyorsa `ek konu` (`topics2`) etiketi de vardır.
- **Cevaplar:** Cevaplar ya kaynağın cevap anahtarından gelir ya da Claude tarafından çözülür. Claude'un çözdüğü cevaplar ekranda `*` ile işaretlidir; kontrol edin.

## 2. Basılı kitap indeksleri: sistemde soru yok, yalnızca adres var

Öğrencinin elinde basılı olarak bulunan soru bankaları sisteme **alınmadı**. Bunlar lisanslı ve şifreli uygulamalarda
duruyor. Sistemde yalnızca her sorunun **adresi** (kitap, sayfa, soru no) ve Claude'un kendi yazdığı kısa
sınıflandırma bulunur.

| Kitap | Kod | Soru | Dosya |
|---|---|---|---|
| 2026 Fenomen 8. Sınıf Matematik A Soru Bankası | `8A` | 1357 | `kaynaklar/Fenomen/fenomen_8_mat_2026.tsv` |
| 2026 Fenomen 8. Sınıf Matematik B Soru Bankası | `8B` | 557 | (aynı dosya) |
| 2025 Ankara Yayıncılık 8. Sınıf Matematik Güçlendiren Soru Bankası | `Ankara` | 1009 | `kaynaklar/Ankara/ankara_8_mat_gsb_2025.tsv` |

- **Ne var:** sayfa ve soru no, tür (Fenomen: Kazanım / Kalıplaşmış İkiz / Yeni Nesil; Ankara: test adı), konu, ek konu, Claude'un kısa beceri etiketi, 1–5 zorluk.
- **Ne yok (depoda):** soru metni, soru görseli, cevap anahtarı. İndeks yalnızca adrestir.
- **Nasıl üretildi:** Kitaplar 30–31 Ekim 2026'da kullanıcının lisanslı uygulamasında, Claude'un bilgisayar kontrolüyle sayfa sayfa incelendi. Aktivasyon kodlarını kullanıcı kendisi girdi.
- **Nasıl kullanılır:** Beyin her konu grubuna basılı kitap soruları önerir. Bunlar ekranda **📘 Kitaplardan çöz** kutusunda, PDF'te de **Kitaplardan Ek Sorular** listesinde görünür. Öğrenci soruyu kendi kitabından da bulabilir.
- **Görseller (2.9.0, özel Drive'da):** Üç kitabın PDF'i öğretmen kitaplığında da var (`FENOMEN8A2024.pdf`, `FENOMEN8B2024.pdf`, `ANKARA YAYINCILIK ... GÜÇLENDİREN SORU BANKASI.pdf`). 1 Kasım 2026'da sayfa sayfa karşılaştırıldı: içerik basılı kitapla aynı. 8A ve Ankara'da PDF sayfası = basılı sayfa; 8B PDF'i kesintisiz sayfalanmış (ünite başları PDF s.1, 79, 125, 163, 221, 259). `app/fenomen.py` her soruyu PDF sayfasına bağlar; görsel kitaplık PDF'inden o anda kırpılır ve önbellekte (`data/cache/`) durur. Görseller GitHub'a gitmez.
- **Ekran görüntüleri:** Analiz için alınan birkaç sorunun görüntüsü yalnızca bu bilgisayarda, depo dışındaki `tuna beyin/fenomen-ekran/<tarih>/` klasöründe durur. Bunlar GitHub'a ve soru bankasına konmaz.

## 2b. Öğretmen kitaplığı: yayınevlerinin öğretmene verdiği PDF'ler (özel Google Drive'da)

Yayınevlerinin öğretmene ücretsiz kullanım için verdiği PDF soru bankaları ve denemeler (yaklaşık 160 PDF,
26.000 sayfa: Nartest, Ata, Bilfen, Mozaik, Newton, Paraf, VIP, Karekök, Muba, Netbil, Okyanus, Ulti, Fenomen,
Ankara ve diğerleri). Kullanıcının beyanına göre bu kitaplar öğretmen olan eşine yayınevlerince verilmiştir.
Çoğaltılmaz; yalnızca öğrencinin yapamadığı sorulara benzer soru bulmak ve deneme hazırlamak için kullanılır.

- **Yer:** Kullanıcının özel Google Drive'ı: `H:\Drive'ım\Öğretmen Kitaplığı` ([Drive klasörü](https://drive.google.com/drive/folders/1Jax5QUF387t22rvtVXUBcWLuhTfPK-pE); bağlantıyı
  yalnızca Drive sahibi açabilir, klasör paylaşılmaz). Depoda PDF yoktur. Program klasörü `config.json` → `kitaplik_dir`
  ile bulur; Drive harf değiştirirse yalnızca bu satır değişir.
- **Veri:** OCR metni, indeks, zorluk, seviye ve kırpılmış görseller de aynı klasörün `veri/` alt klasöründedir
  (2.10.2); bilgisayarda kopya tutulmaz, GitHub'a gitmez.
- **Drive kapalıysa:** Kitaplık araması ve kitap görselleri çalışmaz; beyin soru bankası ve basılı kitap adresleriyle
  devam eder. Google Drive uygulaması açık olmalıdır.
- **İndeks:** Sayfalar Tesseract OCR (Türkçe) ile okunur. Her soruya anahtar kelime ve sayfa başlığından otomatik konu verilir. Kayıtlar Drive'daki `veri/` klasörüne yazılır: OCR metni ve soru-konu indeksi.
- **Durum (1 Kasım 2026):** 164 PDF okundu (2.9.0'da adı neredeyse aynı olduğu için atlanmış Newton Kondisyon kitabı eklendi; 32.567 kayıt). İlk tarama: 163 PDF, 29.081 sayfa. 23.208 sayfaya konu verildi: 23.166 soru tek tek, 9.096 kayıt sayfa düzeyinde (toplam 32.262 kayıt). 2.441 soruda ikinci bir konu (ek konu) var. Tüm dersler kitaplarındaki Türkçe, Fen, İnkılap, Din ve İngilizce sayfaları ile içindekiler sayfaları elendi.
- **İçerik teyidi:** Yayınevlerinden rastgele seçilen sorular okunup kontrol edildi. Bulunan hatalar düzeltildi: "karekök" içindeki "ekok", sayfa altındaki "8. Sınıf" yazısı, Fen grafik soruları. Konular OCR'a dayalı **tahmindir**. Beyin bu yüzden soruyu önermeden önce sayfa görselini açıp kendisi kontrol eder.
- **Kullanım:** Beyin kitaplık sorularını soru bankası ve basılı kitap adaylarıyla tek havuzda uyum puanına göre
  karşılaştırır (2.10.0). Uygun konudaki soruları kalıbı ayırt eden kelimelerle en az 3 aramada bulur; en az 4 yayınevinden en az 8 sorunun görselini açıp kendisi kontrol eder, mümkünse 3 farklı yayınevinden 3-5 soru önerir. Arama sonuçları yayınevlerine yayılır (kitap başına 2, yayınevi başına 4). Adres biçimi: `<Kitap> s.<PDF sayfası> S<soru no>`. Ekranda ve PDF'te sorunun kırpılmış görseli çıkar; **sayfa** bağlantısı sayfanın tamamını gösterir.
- **Zorluk seviyesi (2.10.0):** Her kayda Claude Sonnet soru metninden 1-5 zorluk verir (`python -m app.kitaplik zorluk`;
  1-2 kolay, 3 pekiştirme, 4-5 zor) → `veri/zorluk.json` ve `seviye.json` (özel Drive'da). Yöntem
  Fenomen/Ankara'nın elle etiketli zorluğuyla seçildi: 120 soruluk pilotta 3 seviyede %73 doğru, %98'inde en fazla
  bir basamak fark (Haiku %57, sayfa başlığı kuralları %8-49). Fenomen 8A/8B ve Ankara'da elle etiket kullanılır.
  Puanı olmayan kayıtta tahmin kitap türünden ya da sayfa başlığından yapılır ve `?` ile gösterilir.
- **Soru kırpma:** Soru numarası birkaç Tesseract okumasıyla (gri sayfa, renkli pikseller, sütun başı şeritleri) bulunur; kırpım numaradan başlar, aynı sütundaki sonraki soruda ya da büyük boşlukta biter. Numarası okunamayan sorularda sayfanın tamamı gösterilir.
- **GitHub'a gitmeyenler:** PDF'ler, OCR metni, sayfa görselleri ve kitaplık indeksi. Yalnızca kod (`app/kitaplik.py`) gider.
- **Komutlar:** `python -m app.kitaplik tara` (OCR; yeni PDF eklenince yalnızca yenileri okur), `siniflandir` (konu indeksi), `ozet`, `ara`, `sayfa`, `soru` (sorunun kırpılmış görseli). Gerekenler: Tesseract OCR (`C:\Program Files\Tesseract-OCR`) ve `tuna beyin/tessdata/tur.traineddata`.

## 3. Öğrenci verisi

| Veri | Yer | Ne zaman oluşur |
|---|---|---|
| Yapamadığı / yanlış yaptığı soruların fotoğrafları | `ogrenci/Sorular/<tarih>/` | Fotoğraf yüklenince |
| Beyin çalışmaları (teşhis, adaylar, akış) | `data/runs/<id>/` | Beyin çalışınca |
| Üretilen çalışma kâğıtları | `data/outputs/*.pdf` | PDF oluşturulunca |
| Verilen sorular, puanlar, öğretmen geri bildirimi, sonuçlar | `data/used_qids.json`, `data/ratings.json`, `data/feedback.json`, `data/student_results.json`, `data/answer_overrides.json` | Kullanım sırasında |
| Seçimler, kaldırılan sorular, soru tipi tercihi | Tarayıcının yerel belleği | Ekranda seçim yaptıkça |

- **Bu bilgisayarda kalır.** Yedekler güncelleme sırasında bir üst klasöre `beyin-yedek-<tarih>/` olarak alınır.
- **Claude'a (Anthropic) gönderilen:** Beyin çalışırken öğrencinin soru fotoğrafları ve incelenen soru bankası görselleri Claude Code üzerinden Claude'a gönderilir. Kullanım, bu bilgisayarda giriş yapılmış Claude hesabının aboneliğinden düşer.
- **GitHub'a gönderilmeyen:** Bu bilgisayardaki öğrenci verisi (`ogrenci/` ve `data/` altındaki çalışmalar, PDF'ler, puanlar) ve öğretmen kitaplığı (`data/kitaplik/`) GitHub'a **gönderilmez**. GitHub'a yalnızca kod, belgeler ve kaynak indeksleri (`data/index/`, `kaynaklar/`) gider.
- **Dikkat:** Depo (`burhanbarakli/beyin-calissin-lgs`) şu an **herkese açık**. Depoda daha önceden yüklenmiş öğrenci verisi de var. Gizli kalması isteniyorsa depo sahibi GitHub'da depoyu **Private** yapmalı.

## 4. Telif ve kullanım sınırları

- Kaynak PDF'lerin ve basılı kitapların hakları sahiplerine aittir: kerimhoca.com, MEB (ODSGM), Fenomen Yayıncılık, Ankara Yayıncılık ve öğretmen kitaplığındaki yayınevleri.
- Sistem, öğrencinin kişisel ve ailevi eğitimi için kullanılır. Kaynak PDF'leri, üretilen çalışma kâğıtlarını ve basılı kitap sayfalarını yeniden dağıtmayın, satmayın.
- Şifreli kitap uygulamalarının koruması aşılmaz. Kitapların tamamı ekran görüntüsüyle kopyalanmaz. İnternetteki izinsiz PDF kopyaları indirilmez.

## 5. Yeni kaynak ekleme

- **PDF kaynak** (soru bankasına girer): PDF'i `kaynaklar/LGS_Matematik/` altına koyun, `katalog.json`'a kayıt ekleyin, sonra `python -m app.indexer` çalıştırın. Etiketleri Claude `python -m app.qbank label` ile yazar.
- **Basılı kitap** (yalnızca adres indeksi): `kaynaklar/<Yayınevi>/` altına aynı sütunlarla bir TSV koyun (`kitap sayfa soru tur konu ek_konu beceri zorluk`). Ardından `app/fenomen.py` içindeki `TSVS` ve `BOOKS` listelerine ekleyin. Arama: `python -m app.qbank fenomen --book <kod>`.
