# Güncelleme Notları

En yeni sürüm en üstte. Kurulu sürüm `VERSION` dosyasında ve arayüzde başlığın yanında yazar.

> **Claude için:** Kullanıcı sistemi güncellediğinde, onun kurulu sürümünden yeni olan bölümleri ona
> kısaca ve Türkçe özetle. Her bölümdeki **"Yapmanız gereken"** satırını mutlaka söyle.
> Güncellemenin nasıl yapılacağı `CLAUDE.md` içindeki "Güncelleme" bölümündedir.

---

## 2.6.0 · 31 Ekim 2026 · Soru tipi seçimi (kolay / pekiştirme / zor)

**Yeni**
- "Beyin Çalışsın"dan önce, soru sayısının yanında **Soru tipi** seçimi: **Kolay**, **Pekiştirme**, **Zor**
  ayrı ayrı açılıp kapatılabilir (birden çok seçilebilir, en az biri seçili kalır, seçim hatırlanır).
- Beyin yalnızca seçilen tiplerde soru arar; seçilmeyen tipler için arama ve doğrulama yapmaz. Böylece daha kısa
  sürede tam istenen tipte sorular gelir. Önceki çalışmalar listesinde başlıkta seçilen tipler yazar (ör. "· zor").

**Yapmanız gereken:** Sunucuyu yeniden başlatın.

---

## 2.5.0 · 31 Ekim 2026 · Fenomen 8A/8B kitaplarından benzer sorular (sayfa ve soru no ile)

**Yeni**
- **2026 Fenomen 8. Sınıf Matematik A ve B** soru bankalarının tamamı (1914 soru) tarandı ve indekslendi.
  Her soru için kitap, sayfa, soru no, tür (Kazanım · Kalıplaşmış İkiz · Yeni Nesil), konu, varsa ikinci konu,
  ölçtüğü beceri ve zorluk kayıtlı. Kitapların soruları ve görselleri sisteme alınmadı; kitap elinizde olduğu için
  soruyu kitaptan bulup çözersiniz.
- Beyin, her konu grubuna yapamadığı soruya benzeyen **3–6 Fenomen sorusu** ekler (ör. `8A s.21 S2`, `8B Ünite 2 s.9 S1`).
- Aday sorular ekranında her grubun altında **"📘 Fenomen kitabından çöz"** kutusu var.
- PDF'te cevap anahtarından önce **"Fenomen Soru Bankasından Ek Sorular"** sayfası yer alır: konu konu, işaretlenebilir liste.
- Yeni komut: `python -m app.qbank fenomen --topic "…" --text "…"` (`--topic-all`, `--book 8A`, `--max 3`, `--topics`).
- Bankada olmayan iki konu Fenomen indeksine eklendi: Piramit ve Koni.

**Yapmanız gereken:** `baslat.bat` penceresini kapatıp yeniden başlatın, sonra sayfayı yenileyin. Yeni çalışmalarda
Fenomen önerileri kendiliğinden gelir; eski çalışmalarda görünmez.
8B'nin 2. ve sonraki ünitelerinde sayfa numarası her ünitede yeniden başlar: `8B Ünite 4 s.12` diye yazılır.

---

## 2.4.0 · 30 Ekim 2026 · Çok konulu soru analizi (karekök + üslü gibi)

**Yeni**
- Beyin, birden çok kazanımı birlikte kullanan soruları tek konuya indirgemez: çözümü adım adım kazanımlara ayırır
  (ör. √(27^(x−2)) / √(3^x) = 9 → kök bölmesi + tam kare + üslü kurallar + üs eşitliği), öğrencinin koptuğu adımı bulur.
- Teşhiste **"Kazanımlar: … + …"** ve **çözüm adımları** görünür.
- Aday set **adım zinciri** olur: her adım için öğretici soru (sırasıyla), sonra kazanımları birlikte kullanan sorular.
- Soru bankasında **ek konu** (`topics2`) etiketi ve birlikte arama: `python -m app.qbank search --topic-all "karekök,üslü"`.
  Karekök/üslü soruları etiketlendi.
- Beyin 8. sınıf müfredatında olmayan yöntem (rasyonel üs vb.) kullanmaz.

**Yapmanız gereken:** Sayfayı yenileyin. Birden çok konulu soruları yeniden "Beyin Çalışsın"a verin.
(Bankada kök içinde üslü ifade içeren soru az; bu tür sorular için yeni kaynak PDF eklemek faydalı olur.)

---

## 2.3.0 · 30 Ekim 2026 · Beyin konu takvimine göre teşhis eder (EKOK kalıbı)

**Yeni**
- Beyin, soruyu yüzeyine göre değil **öğrencinin o tarihe kadar öğrendiği kazanımla** sınıflandırır. 1. dönemde
  (Eylül–Ocak) 2. dönem konularını (Doğrusal Denklemler ve sonrası) teşhis etmez, aday olarak da önermez.
- **"Eşit toplam / değiş tokuş / … den fazla, en az"** problemleri (ör. 20 TL ve 50 TL banknotlar) artık denklem değil
  **EBOB - EKOK Problemleri** olarak teşhis edilir; benzer EKOK soruları (LGS 2023/7, 2019/20, 2024/16, MEB kitabı) gelir.
- Görev dosyasına tarih eklendi; derin analiz ajanı da aynı kurala uyar.

**Yapmanız gereken:** Sunucuyu yeniden başlatın. Daha önce yanlış konuyla teşhis edilen soruları yeniden "Beyin Çalışsın"a verin.

---

## 2.2.0 · 30 Ekim 2026 · Toplu çıkarma düğmeleri, Windows'ta boş görseller

**Yeni**
- Aday sorularda **toplu çıkarma düğmeleri**: "Öğretici soruları kaldır", "Pekiştirme sorularını kaldır", "Orta düzey soruları kaldır"
  (zorluk 2,5 – 3,6) ve "Zor / Zorlayıcı soruları kaldır" (Zorlayıcı rolündekiler ve zorluğu 3,7 ve üstü). Tek tıkla tüm konulardaki uyan aday soruları
  listeden ve seçimden kaldırır; düğmede kaç soru kalkacağı yazar. "Kaldırılanları geri getir" ile geri alınır.

**Düzeltmeler**
- Mac'te üretilen indeksler Mac'in dosya yollarını taşıdığı için Windows'ta soru görselleri boş geliyordu.
  İndeksler artık yolu program klasörüne göre yazar (`kaynaklar/...`); PDF bulunamazsa kaynak klasörünün
  alt klasörlerinde de dosya adıyla aranır. Eski indeksler için: `python -m app.indexer --relink`
  (yeniden indekslemeden yalnızca yolları düzeltir).
- Güncellemeden sonra tarayıcı eski arayüzü göstermez (Ctrl+F5 gerekmez).
- **Kaldırılanları geri getir** artık soruları seçimleriyle birlikte döndürür; önceden sorular dönüyor ama işaretleri kalkıyordu.
- Beyin çalışırken durum dosyası yazılırken okunursa sunucu penceresinde çıkan hata giderildi.

**Yapmanız gereken:** Sunucuyu yeniden başlatın ve sayfayı bir kez Ctrl+F5 ile yenileyin.

---

## 2.1.0 · 28 Ekim 2026 · MEB kitabı ve MEBİ denemeleri

**Yeni**
- Soru bankasına **MEB LGS Çalışma Kitabı (Matematik)** eklendi: 6 ünitede 504 LGS tarzı soru, cevaplı.
  Kitap ünite ünite bölündü (`kaynaklar/LGS_Matematik/14_MEB_Calisma_Kitabi/`); kitabın sonundaki 2018-2026
  merkezî sınav soruları bankada zaten olduğu için alınmadı.
- **12 MEBİ LGS denemesinin** matematik testleri eklendi (240 soru, `13_MEBI_Denemeler/`). 1-11'in cevapları
  kitapçıktaki anahtardan, 12. denemeninki (anahtarı yayımlanmamış) Claude'un çözümünden gelir.
- Yeni 744 sorunun hepsi kazanım, ölçtüğü beceri, rol ve 1-5 zorlukla etiketlendi. Beyin bu soruları
  pekiştirme ve zorlayıcı adaylarda kullanır. Bankada artık 1679 soru var.
- Beyin çalışırken büyük düğme kırmızı **⏹ Beyni Durdur** olur; durdurmadan önce onay sorulur. Beyin
  çalışırken yanlışlıkla ikinci bir çalışma başlatılamaz.

**Düzeltmeler**
- İndeksleyici: iki sütunlu sayfada boydan boya uzanan sorular, sütunlar arası sıralanan numaralar,
  üç basamaklı soru numaraları ve sayfa çerçevesi süsleri artık doğru işleniyor.

**Yapmanız gereken:** Güncellemeden sonra sunucuyu yeniden başlatın. (Güncellemeyi Claude yaparsa yeni PDF'leri,
indeks dosyalarını ve puanları da ekler; bkz. `CLAUDE.md`.)

---

## 2.0.0 · 28 Ekim 2026 · LGS ve tek ekran

**Yeni**
- Sistem artık **LGS (8. sınıf)** için. TYT/AYT kaynakları kaldırıldı; yerine kerimhoca.com'dan LGS
  matematik kaynakları geldi: çalışma kâğıtları, kazanım testleri, konu tarama testleri ve 2018-2026
  LGS çıkmış soruları (84 PDF, 935 soru). Fen sonra eklenecek.
- **Tek ekran, dört adım:** fotoğrafı yükle → 🧠 Beyin Çalışsın → aday soruları seç → 📄 PDF.
  Sınavlar, Kaynaklar, Çıktılar sekmeleri kaldırıldı. Deneme klasörü / dosya adı kuralı yok.
- Fotoğraf sürüklenir, **yapıştırılır** (Ctrl/⌘ + V) ya da seçilir; her fotoğraf için sadece
  **Yapamadı / Yanlış** seçilir. Fotoğraflar `ogrenci/Sorular/<tarih>/` altına kaydedilir.
- Roller: **Öğretici** (çalışma kâğıdı) → **Pekiştirme** (test, tarama) → **Zorlayıcı** (LGS çıkmış).
- **Önceki çalışmalar** listesi: her çalışmanın fotoğrafları ve PDF'leri; tekrar açılabilir, silinebilir.

**Düzeltmeler**
- Soru kırpımları yeniden yapıldı: sağ sütundaki şekillerin kenarı kesilmiyor, alttaki sorunun
  şekli kırpıma girmiyor, sayfa ortasındaki şerit görünmüyor. LGS sorularında numara "7. ." gibi
  çift noktalı çıkmıyor.
- PDF'te bölüm başlığı (ör. "Zorlayıcı Sorular") sayfa dibinde sorusundan ayrı kalmıyor.
- Sağ üstteki durum yazısı Claude Code'da giriş yapılıp yapılmadığını da gösteriyor; giriş yoksa
  beyin başlatılmıyor.

**Kaldırılanlar:** sınav analizi, cevap anahtarı okuma, toplu zorluk puanlama, elle soru arama,
öğrenci sonuç girişi, Kolay/Uygun/Zor geri bildirimi (yalnızca "✕ bir daha önerme" kaldı).

**Yapmanız gereken:** Sunucu penceresini kapatıp yeniden başlatın. Eski `ogrenci/Denemeler/`
klasörü silinmedi ama artık kullanılmıyor.

---

## 1.2.0 · 4 Ekim 2026 · Derin analiz

**Yeni**
- **🔬 Derin analiz:** Beyin panelinde, butonun üstünde yeni bir kutu. İşaretlenirse *soru analisti* ajanı devreye girer:
  - Öğrencinin her yanlış sorusunu baştan çözüp **adım düzeyinde teşhis** koyar: kopma noktası, hata türü (kavram/işlem/okuma/süre), kök neden.
  - Seçilen her adayı da çözerek **denetler**: cevap doğru mu, kesim tam mı, hedef beceriyi ölçüyor mu. Geçenler **✓ denetlendi** rozetiyle görünür.
  - Daha yavaş ve maliyeti normal modun yaklaşık 2-3 katı. Önerilen kullanım: Sonnet + derin analiz, bir deneme için yaklaşık 1-2 $.
- Beynin canlı akışında artık tek bir "Bitti" satırı var (toplam süre ve maliyet).

**Yapmanız gereken:** Güncellemeden sonra siyah pencereyi kapatıp `baslat.bat`'ı yeniden açın.

---

## 1.1.0 · 4 Ekim 2026 · Hızlı yükleme ve model seçimi

**Yeni**
- **Hızlı fotoğraf yükleme (Sınavlar sekmesi):** Sadece durum seçilir:
  - **Yapamadı / Yanlış / Doğru-Tereddütlü**. Fotoğraflar toplu olarak sürüklenip bırakılır, yükleme kendiliğinden başlar.
  - Ders, konu, soru no ve cevap **isteğe bağlı**; beyin bunları fotoğraftan kendisi bulur.
  - **Doğru yapılan soruları yüklemeye gerek yok.**
  - Beyin durumları önceliklendirir: Yapamadı > Yanlış > Doğru-Tereddütlü. Eski "Zorlandı" etiketli fotoğraflar "Tereddütlü" sayılır.
- **Model seçimi:** Beyin panelinde Opus (en iyi) / Sonnet (dengeli) / Haiku (en ucuz). Kalıcı varsayılan Ayarlar'da.
- **Silme:** Çıktılar sekmesinde PDF'ler ve beyin çalışmaları tek tek ya da toplu silinebilir. Silinen PDF'teki sorular tekrar önerilebilir hâle gelir.

**Düzeltmeler**
- PDF'in hep eski seçilen sorularla çıkması düzeltildi. Artık her beyin çalışmasının kendi seçimi var; sepeti boşaltma (🗑) butonu eklendi.
- Claude masaüstü uygulaması güncellenince "Claude Code bulunamadı" hatası çıkıyordu; düzeltildi.

**Yapmanız gereken:** `baslat.bat`'ı yeniden açın. Sağ üstte yeşil **"Claude Code bulundu"** yazısını kontrol edin.

---

## 1.0.0 · 30 Eylül 2026 · İlk sürüm

- Yerel web uygulaması (`baslat.bat` → `http://localhost:8765`).
- MEB kaynaklarından 33.000 soruluk bank, cevap anahtarları, birleşik zorluk (kitap + Claude puanı + öğretmen + öğrenci).
- Beyin: yanlış soru fotoğraflarından teşhis, seviyeli aday listesi, PDF çalışma kâğıdı.
- Öğretmen geri bildirimi (Kolay / Uygun / Zor / ✕ Kullanma) ve öğrenci sonuç girişi.
- Resimli kılavuz: `docs/KILAVUZ.md`.
