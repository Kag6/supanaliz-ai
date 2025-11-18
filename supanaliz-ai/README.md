Bu proje, satış ve satınalma Excel pivot dosyalarını uçtan uca işleyip, ürün bazında kârlılık, stokout riski, birim uyumsuzluğu ve yönetsel özetler üreten modüler bir analiz motorudur.

Sistem tamamen offline, Python tabanlı ve adım adım genişletilebilir bir mimari ile tasarlanmıştır.

🧱 1. Proje Yapısı
supanaliz-ai/
│
├── agents/
│   ├── matching_engine.py
│   ├── profit_features.py
│   ├── sales_agent.py
│   ├── purchase_agent.py
│   ├── decision_agent.py
│
├── parser/
│   ├── excel_loader.py
│   ├── fx_parser.py
│   ├── sales_parser.py
│   ├── purchase_parser.py
│
├── features/
│   ├── sales_features.py
│   ├── purchase_features.py
│   ├── profit_features.py   ← ANALİZ MOTORUNUN MERKEZİ
│
├── data/
│   ├── AllTimeSatisPivotLast.xls
│   ├── AllTimeSatinAlmaPivotLast.xls
│   ├── fx_rates.xlsx
│
├── pipeline_step1_test.py
├── pipeline_step2_purchase_features_test.py
├── pipeline_step3_sales_features_test.py
├── pipeline_step4_profit_features_test.py
│
└── README.md  (bu dosya)

⚙️ 2. Sistem Mimarisi

SUPANALİZ AI aşağıdaki mantık zincirine göre çalışır:

[Excel Files] 
     ↓
Parser Layer (sales_parser / purchase_parser / fx_parser)
     ↓
Feature Layer (sales_features / purchase_features)
     ↓
Matching Engine (malzeme bazında birleşim)
     ↓
Profit Engine (birim maliyet + satış fiyatı → kar hesaplama)
     ↓
Stockout Engine (stokout risk analizi)
     ↓
Decision Agent (kural tabanlı yönetsel özet)


Veri işleme zincirinin her aşaması ayrı bir Python modülüdür ve bağımsız olarak test edilebilir.

📥 3. Veri Kaynakları
3.1 Satış Pivot Dosyası

Alanlar:

Malzeme

MalKodGrup

Miktar

Miktar Br.

Genel Toplam (USD)

Belge Oluşturma Tarihi

3.2 Satınalma Pivot Dosyası

Alanlar:

Malzeme

MalzemeGrup

Sipariş Miktarı

Birim

Kalem Toplam (TL)

Kalem Toplam (USD)

Tarih

3.3 Döviz Kuru Verisi

FX_date

USD/TRY

EUR/TRY

🧩 4. Modüllerin Açıklaması
4.1 parser/
sales_parser.py

Satış pivot dosyasını okur.

Birim, miktar, USD toplamlarını normalize eder.

Eksik değer kontrolleri yapar.

meta + data döner.

purchase_parser.py

Satınalma pivot dosyasını okur.

TL maliyet → USD maliyet dönüşümü yapar.

Birimleri normalize eder.

meta + data döner.

fx_parser.py

Döviz kurlarını yükler.

Tarih bazlı dönüşümlere imkan sağlar.

4.2 agents/
matching_engine.py

Satış ve satınalma datasını malzeme bazında birleştirir.

Ürettiği kolonlar:

Malzeme
MalKodGrup
MalzemeGrup
sales_unit
purchase_unit
total_sales_qty
total_purchase_qty
total_sales_usd
total_purchase_cost_usd
match_status (both / sales_only / purchase_only / none)
stokout_risk_flag (sadece sales > purchase için)

profit_features.py

Bu modül, sistemin analitik çekirdeğidir.

Hesapladığı ana çıktılar:

Birim başı satış fiyatı

Birim başı satınalma maliyeti

Profit per unit

Profit margin %

Total profit

Unit mismatch detection

Profit quality labels:

strict_AD

matched_other_unit

unit_mismatch

missing_cost

missing_sales

no_match

Ayrıca:

✔ Core set (satılan + satın alınan ürün)
✔ Stokout analiz seti
✔ En kârlı ve en zararlı ürün listeleri
✔ Matching summary üretir

decision_agent.py

(opsiyonel, ilerleyen adımlarda)

Stokout risk skorlaması

Satınalma öncelik puanı

Satış anomalisi

Marj çöküşü tespiti

Yönetici özeti üretir

📊 5. Pipeline Betikleri

Her step bağımsız test edilebilir.

pipeline_step1_test.py

Satış + satınalma parser’ı test eder.

pipeline_step2_purchase_features_test.py

Satınalma özel feature’larını doğrular.

pipeline_step3_sales_features_test.py

Satış özelliklerini doğrular.

pipeline_step4_profit_features_test.py

→ Ana analiz çalıştırıcısı

Üretir:

Matching summary

Ürün bazlı kârlılık

En kârlı 10 ürün

En zararlı 10 ürün

Stokout riski ilk 10 ürün

▶️ 6. Çalıştırma
6.1 Sanal ortamı etkinleştirme
.\.venv\Scripts\Activate.ps1

6.2 Tüm pipeline’ı test etme
python pipeline_step4_profit_features_test.py

🧪 7. Beklenen Çıktılar
7.1 Matching Output
total_products: 3974
count_both: 323
sales_only: 698
purchase_only: 698
stockout_candidates: 116

7.2 Profit Output

Her ürün için:

Marj % (negatif/pozitif)

Birim uyumu

Toplam kâr

Profit quality etiketi

7.3 Stockout
severity = sales_qty - purchase_qty

🛠 8. Geliştirme Yol Haritası

✔ Anomaly Detector
✔ Trend Analiz Modülü
✔ Tedarikçi Performans Modülü
✔ Zaman Serisi Satış Tahminleri
✔ Streamlit Dashboard

📄 9. Lisans

Bu proje özel SUPANALİZ AI organizasyonuna aittir.
Kod ve analiz modelleri ticari kullanım için lisanslıdır.

🎯 10. İletişim

Sorumlu geliştirici: SUPANALİZ AI – Veri Bilimi / ERP Analitik Ekibi
İş birliği için: kaanalp@supanaliz.com
