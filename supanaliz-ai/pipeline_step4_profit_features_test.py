# pipeline_step4_profit_features_test.py

from parser.sales_parser import parse_sales_excel
from parser.purchase_parser import parse_purchase_excel
from features.profit_features import build_profit_features

SALES_PATH = "data/AllTimeSatisPivotLast.xls"
PURCHASE_PATH = "data/AllTimeSatinAlmaPivotLast.xls"
FX_PATH = "data/fx_rates.xlsx"


def main():
    # 1) Datasetleri yükle
    sales_res = parse_sales_excel(SALES_PATH)
    purchase_res = parse_purchase_excel(PURCHASE_PATH, FX_PATH)

    sales_df = sales_res["data"]
    purchase_df = purchase_res["data"]

    print("=== SALES META ===")
    print(sales_res["meta"])

    print("\n=== PURCHASE META ===")
    print(purchase_res["meta"])

    # 2) Kârlılık / matching / stokout
    features = build_profit_features(sales_df, purchase_df)

    print("\n=== MATCHING SUMMARY ===")
    print(features["matching_summary"])

    # Ana kârlılık tablosu: sadece hem satış hem satınalma olan ürünler
    profit_core = features["product_profit"]

    print("\n=== ÜRÜN BAZLI KÂRLILIK (İLK 10) ===")
    print(
        profit_core[
            [
                "Malzeme",
                "MalKodGrup",
                "sales_unit",
                "purchase_unit",
                "total_sales_qty",
                "total_purchase_qty",
                "total_sales_usd",
                "total_purchase_cost_usd",
                "sales_unit_price_usd",
                "purchase_unit_cost_usd",
                "profit_per_unit_usd",
                "profit_margin_pct",
                "total_profit_usd",
                "profit_quality",
            ]
        ].head(10)
    )

    print("\n=== EN KÂRLI ÜRÜNLER (İLK 10) ===")
    print(
        features["top_profitable"][
            [
                "Malzeme",
                "MalKodGrup",
                "sales_unit",
                "purchase_unit",
                "total_sales_qty",
                "total_sales_usd",
                "total_purchase_qty",
                "total_purchase_cost_usd",
                "total_profit_usd",
                "profit_margin_pct",
                "profit_quality",
            ]
        ].head(10)
    )

    print("\n=== EN ZARARLI / DÜŞÜK KÂRLI ÜRÜNLER (İLK 10) ===")
    print(
        features["worst_profitable"][
            [
                "Malzeme",
                "MalKodGrup",
                "sales_unit",
                "purchase_unit",
                "total_sales_qty",
                "total_sales_usd",
                "total_purchase_qty",
                "total_purchase_cost_usd",
                "total_profit_usd",
                "profit_margin_pct",
                "profit_quality",
            ]
        ].head(10)
    )

    print("\n=== STOKOUT ADAYLARI (İLK 10) ===")
    stokout = features["stokout_candidates"]
    if len(stokout) == 0:
        print("Stokout adayı ürün bulunamadı.")
    else:
        print(
            stokout[
                [
                    "Malzeme",
                    "MalKodGrup",
                    "sales_unit",
                    "total_sales_qty",
                    "total_purchase_qty",
                    "total_sales_usd",
                    "total_purchase_cost_usd",
                    "stockout_severity",
                    "profit_quality",
                ]
            ].head(10)
        )


if __name__ == "__main__":
    main()
