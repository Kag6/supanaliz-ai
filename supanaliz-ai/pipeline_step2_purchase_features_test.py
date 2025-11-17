# pipeline_step2_purchase_features_test.py

from parser.purchase_parser import parse_purchase_excel
from features.purchase_features import build_purchase_features

PURCHASE_PATH = "data/AllTimeSatinAlmaPivotLast.xls"
FX_PATH = "data/fx_rates.xlsx"


def main():
    purchase_parsed = parse_purchase_excel(PURCHASE_PATH, FX_PATH)
    purchase_df = purchase_parsed["data"]

    print("=== PURCHASE PARSED META ===")
    print(purchase_parsed["meta"])

    features = build_purchase_features(purchase_df)

    mat_fe = features["material_features"]
    sup_fe = features["supplier_features"]
    trend_fe = features["price_trend"]

    print("\n=== ÜRÜN BAZLI ÖZELLİKLER (İLK 10) ===")
    print(
        mat_fe[
            [
                "Malzeme",
                "MalzemeGrup",
                "Birim",
                "line_count",
                "total_qty",
                "total_cost_usd",
                "avg_unit_cost_usd",
                "cv_unit_cost",
                "cost_volatility_risk",
                "avg_lead_time_days",
                "p90_lead_time",
            ]
        ].head(10)
    )

    print("\n=== TEDARİKÇİ BAZLI ÖZELLİKLER (RİSK SKORUNA GÖRE SIRALI, İLK 10) ===")
    sup_sorted = sup_fe.sort_values("supplier_risk_score", ascending=False)
    print(
        sup_sorted[
            [
                *([ "Tedarikçi Num.", "İsim"] if "Tedarikçi Num." in sup_fe.columns else ["MalzemeGrup"]),
                "line_count",
                "total_cost_usd",
                "avg_lead_time_days",
                "long_lead_ratio",
                "no_delivery_ratio",
                "supplier_risk_score",
            ]
        ].head(10)
    )

    print("\n=== FİYAT TRENDİ (İLK 10) ===")
    print(
        trend_fe[
            [
                "Malzeme",
                "MalzemeGrup",
                "price_trend_slope",
                "price_trend_label",
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()
