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



📄 2. Lisans

Bu proje özel SUPANALİZ AI organizasyonuna aittir.
Kod ve analiz modelleri ticari kullanım için lisanslıdır.

🎯 3. İletişim

Sorumlu geliştirici: SUPANALİZ AI – Veri Bilimi / ERP Analitik Ekibi
İş birliği için: kaanalp@supanaliz.com

