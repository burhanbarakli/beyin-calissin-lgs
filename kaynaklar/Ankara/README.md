# Ankara Yayıncılık 2025 8. Sınıf Matematik Güçlendiren Soru Bankası — soru adresi indeksi

`ankara_8_mat_gsb_2025.tsv`, öğrencinin elindeki basılı **2025 Ankara Yayıncılık 8. Sınıf Matematik Güçlendiren
Soru Bankası**'ndaki her sorunun **adresini** ve **sınıflandırmasını** tutar. Kitabın soruları, görselleri ve cevap
anahtarı burada **yoktur**. Kitap lisanslı ve şifreli bir uygulamada (AnkaraYayincilikKutuphane, Fernus KitapX)
olduğu için yalnızca öğrencinin kitaptan bulabilmesine yetecek bilgi yazıldı.

Sütunlar `kaynaklar/Fenomen/fenomen_8_mat_2026.tsv` ile aynıdır:

| Sütun | Anlamı |
|---|---|
| `kitap` | Her satırda `Ankara` |
| `sayfa` | Basılı sayfa no (11–314). Uygulamadaki sayfa numarasıyla aynıdır. |
| `soru` | Sayfadaki soru numarası |
| `tur` | Testin adı: **Konu Testi** (kazanım, temel-orta) · **Geçiş Testi** (yeni nesil, orta-zor) · **Beceri Temelli Test** (ünite sonu, zor). Test numaraları her ünitede yeniden başlar; adresi sayfa ve soru no belirler. |
| `konu` | Kısa konu kodu. Tam adları `app/fenomen.py` → `TOPICS` içindedir ve sistemin konu adlarıyla aynıdır. |
| `ek_konu` | Soru ikinci bir kazanımı da kullanıyorsa o kazanım (ör. karekök sorusunda `Temel Kurallar` = üslü ifadeler). Yüklenirken tam konu adına çevrilir. `Yüzdeler`, `Oran`, `Birim Dönüşümü` gibi 7. sınıf önkoşulları olduğu gibi kalır. |
| `beceri` | Sorunun ölçtüğü beceri. Claude'un kendi kısa etiketidir, kitaptaki soru metni değildir. |
| `zorluk` | 1–5 arası; Claude'un tahmini |

Toplam **1009 soru**. Etiketler 31 Ekim 2026'da kitap uygulamada sayfa sayfa incelenerek yazıldı. Ünite kapakları
(75–76, 137–138, 181–182, 233–234, 275–276) ve cevap anahtarı (315+) alınmadı.

Ünite sırası: Çarpanlar ve Katlar (11–40) · Üslü İfadeler (41–74) · Kareköklü İfadeler (77–116) · Veri Analizi
(117–136) · Olasılık (139–156) · Cebirsel İfadeler ve Özdeşlikler (157–180) · Doğrusal Denklemler (183–220) ·
Eşitsizlikler (221–232) · Üçgenler (235–262) · Eşlik ve Benzerlik (263–274) · Dönüşüm Geometrisi (277–290) ·
Geometrik Cisimler (291–314).

Kullanım (Fenomen ile aynı komut):

```
python -m app.qbank fenomen --book Ankara --topic "ebob - ekok problemleri" --text "eşit,en az"
python -m app.qbank fenomen --topic-all "karekök,üslü" --min 3
```

Beyin, her konu grubuna önerdiği basılı kitap sorularında (`groups[].fenomen`) Fenomen ve Ankara sorularını birlikte
kullanır. Arayüzde "📘 Basılı kitaplardan çöz" kutusunda, PDF'te cevap anahtarından önceki listede görünür.
