from parser.purchase_parser import parse_purchase_excel

PURCHASE_PATH = "data/AllTimeSatinAlmaPivotLast.xls"
FX_PATH = "data/fx_rates.xlsx"

res = parse_purchase_excel(PURCHASE_PATH, FX_PATH)
df = res["data"]

print("=== FX DÖNÜŞÜM KONTROLÜ (5 ÖRNEK) ===")

sample = df[[
    "Sipariş Tarihi",
    "Fiyat",
    "Sipariş Miktarı",
    "Kalem Toplam TL",
    "FX_USDTRY",
    "Birim Maliyet USD",
    "Kalem Toplam USD"
]].head(5)

print(sample)

# Manuel kontrol: TL / FX == USD ?
sample["manual_usd_unit"] = sample["Fiyat"] / sample["FX_USDTRY"]
sample["manual_usd_total"] = sample["Kalem Toplam TL"] / sample["FX_USDTRY"]

print("\n=== MANUEL HESAP ===")
print(sample[["manual_usd_unit", "manual_usd_total"]])
