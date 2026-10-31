# Kaynaklar ve veri kullanımı

Bu belge, Beyin Çalışsın'ın hangi kaynakları kullandığını, öğrenci verisini nerede tuttuğunu, neyi Claude'a
(Anthropic) gönderdiğini ve neyin GitHub'a gittiğini anlatır. Son güncelleme: 31 Ekim 2026 (sürüm 2.7.1).

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
- **Ne yok:** soru metni, soru görseli, cevap anahtarı. Kitapların hiçbir sayfası kopyalanmadı ya da kaydedilmedi.
- **Nasıl üretildi:** Kitaplar 30–31 Ekim 2026'da kullanıcının lisanslı uygulamasında, Claude'un bilgisayar kontrolüyle sayfa sayfa incelendi. Aktivasyon kodlarını kullanıcı kendisi girdi.
- **Nasıl kullanılır:** Beyin her konu grubuna 3–6 basılı kitap sorusu önerir. Bunlar ekranda **📘 Basılı kitaplardan çöz** kutusunda, PDF'te de **Basılı Soru Bankalarından Ek Sorular** listesinde görünür. Öğrenci soruyu kendi kitabından bulup çözer.
- **Ekran görüntüleri:** Analiz için alınan birkaç sorunun görüntüsü yalnızca bu bilgisayarda, depo dışındaki `tuna beyin/fenomen-ekran/<tarih>/` klasöründe durur. Bunlar GitHub'a ve soru bankasına konmaz.

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
- **GitHub'a gönderilmeyen:** Bu bilgisayardaki öğrenci verisi (`ogrenci/` ve `data/` altındaki çalışmalar, PDF'ler, puanlar) GitHub'a **gönderilmez**. GitHub'a yalnızca kod, belgeler, kaynak indeksleri (`data/index/`, `kaynaklar/`) gider.
- **Dikkat:** Depo (`burhanbarakli/beyin-calissin-lgs`) şu an **herkese açık**. Depoda daha önceden yüklenmiş öğrenci verisi de var. Gizli kalması isteniyorsa depo sahibi GitHub'da depoyu **Private** yapmalı.

## 4. Telif ve kullanım sınırları

- Kaynak PDF'lerin ve basılı kitapların hakları sahiplerine aittir: kerimhoca.com, MEB (ODSGM), Fenomen Yayıncılık, Ankara Yayıncılık.
- Sistem, öğrencinin kişisel ve ailevi eğitimi için kullanılır. Kaynak PDF'leri, üretilen çalışma kâğıtlarını ve basılı kitap sayfalarını yeniden dağıtmayın, satmayın.
- Şifreli kitap uygulamalarının koruması aşılmaz. Kitapların tamamı ekran görüntüsüyle kopyalanmaz. İnternetteki izinsiz PDF kopyaları indirilmez.

## 5. Yeni kaynak ekleme

- **PDF kaynak** (soru bankasına girer): PDF'i `kaynaklar/LGS_Matematik/` altına koyun, `katalog.json`'a kayıt ekleyin, sonra `python -m app.indexer` çalıştırın. Etiketleri Claude `python -m app.qbank label` ile yazar.
- **Basılı kitap** (yalnızca adres indeksi): `kaynaklar/<Yayınevi>/` altına aynı sütunlarla bir TSV koyun (`kitap sayfa soru tur konu ek_konu beceri zorluk`). Ardından `app/fenomen.py` içindeki `TSVS` ve `BOOKS` listelerine ekleyin. Arama: `python -m app.qbank fenomen --book <kod>`.
