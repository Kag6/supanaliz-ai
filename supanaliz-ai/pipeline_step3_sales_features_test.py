# pipeline_step3_sales_features_test.py

from parser.sales_parser import parse_sales_excel
from features.sales_features import build_sales_features

SALES_PATH = "data/AllTimeSatisPivotLast.xls"

def main():
    sales_parsed = parse_sales_excel(SALES_PATH)
    sales_df = sales_parsed["data"]

    print("=== SALES PARSED META ===")
    print(sales_parsed["meta"])

    features = build_sales_features(sales_df)

    print("\n=== AYLIK SATIŞLAR (İLK 10) ===")
    print(features["monthly_sales"].head(10))

    print("\n=== SATIŞ TRENDİ (İLK 10) ===")
    print(features["trend"].head(10))

    print("\n=== MEVSİMSELLİK (İLK 10) ===")
    print(features["seasonality"].head(10))

    print("\n=== EN ÇOK SATAN ÜRÜNLER (TOP 10) ===")
    print(features["top_performers"].head(10))

    print("\n=== EN RİSKLİ DÜŞEN TREND (İLK 10) ===")
    print(features["risky_decliners"].head(10))


if __name__ == "__main__":
    main()
