# pipeline_step1_test.py

from parser.sales_parser import parse_sales_excel
from parser.purchase_parser import parse_purchase_excel

SALES_PATH = "data/AllTimeSatisPivotLast.xls"
PURCHASE_PATH = "data/AllTimeSatinAlmaPivotLast.xls"
FX_PATH = "data/fx_rates.xlsx"

def main():
    print("=== SATIŞ PARSE ===")
    sales_result = parse_sales_excel(SALES_PATH)
    print(sales_result["meta"])

    print("\n=== SATINALMA PARSE ===")
    purchase_result = parse_purchase_excel(PURCHASE_PATH, FX_PATH)
    print(purchase_result["meta"])

    # Örnek satırlar
    sales_df = sales_result["data"]
    purchase_df = purchase_result["data"]

    print("\n=== SATIŞ ÖRNEK ===")
    print(
        sales_df[[
            "Başlangıç Tarihi",
            "Malzeme",
            "MalKodGrup",
            "Miktar",
            "Miktar Br.",
            "Genel Toplam (USD)"
        ]].head()
    )

    print("\n=== SATINALMA ÖRNEK ===")
    print(
        purchase_df[[
            "Sipariş Tarihi",
            "Malzeme",
            "MalzemeGrup",
            "Birim",
            "Sipariş Miktarı",
            "Fiyat",
            "FX_USDTRY",
            "Birim Maliyet USD",
            "Kalem Toplam USD",
            "Lead Time (days)"
        ]].head()
    )


if __name__ == "__main__":
    main()
