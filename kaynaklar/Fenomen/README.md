# Fenomen 8. Sınıf Matematik A / B — soru adresi indeksi

`fenomen_8_mat_2026.tsv`, öğrencinin elindeki basılı **2026 Fenomen 8. Sınıf Matematik A** ve **B** soru
bankalarındaki her sorunun **adresini** ve **sınıflandırmasını** tutar. Kitapların soruları, görselleri ve cevap
anahtarları burada **yoktur**. Kitap lisanslı ve şifreli bir uygulamada (FenomenKutuphane) olduğu için yalnızca
öğrencinin kitaptan bulabilmesine yetecek bilgi yazıldı.

| Sütun | Anlamı |
|---|---|
| `kitap` | `8A` veya `8B` |
| `sayfa` | Basılı sayfa no. 8A tek numaralanır (3–318). 8B'de 1. ünite düz numaralıdır (5–78). Sonraki ünitelerde numara her ünitede yeniden başlar ve `ünite-sayfa` olarak yazılır (ör. `2-9` = 2. ünite, 9. sayfa). |
| `soru` | Sayfadaki soru numarası |
| `tur` | `K` Kazanım soruları · `I` Kalıplaşmış ikiz sorular · `Y` Orijinal yeni nesil sorular |
| `konu` | Kısa konu kodu. Tam adları `app/fenomen.py` → `TOPICS` içindedir ve sistemin konu adlarıyla aynıdır. Fenomen'de olup bankada olmayan iki konu ayrıca eklendi: `G3` Piramit, `G4` Koni. |
| `ek_konu` | Soru ikinci bir kazanımı da kullanıyorsa o kazanım (yüklenirken tam konu adına çevrilir) |
| `beceri` | Sorunun ölçtüğü beceri. Claude'un kendi kısa etiketidir, kitaptaki soru metni değildir. |
| `zorluk` | 1–5 arası; Claude'un tahmini |

Toplam 1914 soru var: 8A'dan 1357, 8B'den 557. Etiketler 30–31 Ekim 2026'da, kitap uygulamada sayfa sayfa
incelenerek yazıldı.

Kullanım:

```
python -m app.qbank fenomen --topics
python -m app.qbank fenomen --topic "ebob - ekok problemleri" --text "eşit,en az,ortak kat"
python -m app.qbank fenomen --topic-all "karekök,üslü" --book 8A --max 3
```

Beyin her konu grubuna 3–6 Fenomen sorusu önerir (`candidates.json` → `groups[].fenomen`). Bu öneriler arayüzde
"📘 Fenomen kitabından çöz" kutusunda görünür. PDF'te de cevap anahtarından önceki sayfada liste olarak yer alır.
