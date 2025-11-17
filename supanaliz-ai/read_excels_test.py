import pandas as pd

sales_path = r"C:\Users\kaan.gokce\Desktop\AllTimeSatisPivotLast.xls"
purchase_path = r"C:\Users\kaan.gokce\Desktop\AllTimeSatinAlmaPivotLast.xls"

sales = pd.read_excel(sales_path, sheet_name="IASSALHEADLIST", engine="xlrd")
purchase = pd.read_excel(purchase_path, sheet_name="IASPURHEADLISTTREE", engine="xlrd")

# Sadece gerekli kolonları al
sales_groups = sales["MalKodGrup"].dropna().astype(str).unique()
purchase_groups = purchase["MalzemeGrup"].dropna().astype(str).unique()

# Kesişim
intersection = set(sales_groups).intersection(set(purchase_groups))

print("Satış MalKodGrup benzersiz:", len(sales_groups))
print("Satınalma MalzemeGrup benzersiz:", len(purchase_groups))
print("Kesişen grup sayısı:", len(intersection))

print("\nEşleşmeyen satış grupları:")
print(set(sales_groups) - set(purchase_groups))

print("\nEşleşmeyen satınalma grupları:")
print(set(purchase_groups) - set(sales_groups))

# Ek bilgi isteği: Miktar sütunu ve birim örnekleri
print("\n=== SATIŞ 'Miktar' ÖRNEKLERİ ===")
print(sales["Miktar"].head())
print("\n=== SATIŞ 'Miktar' DTYPE ===")
print(sales["Miktar"].dtype)
print("\n=== SATIŞ 'Miktar Br.' ÖRNEK BİRİMLER (ilk 10) ===")
print(sales["Miktar Br."].unique()[:10])

# Purchase tarafı - miktar ve birim bilgisi
print("\n=== SATINALMA 'Sipariş Miktarı' ÖRNEKLERİ ===")
print(purchase["Sipariş Miktarı"].head())
print("\n=== SATINALMA 'Sipariş Miktarı' DTYPE ===")
print(purchase["Sipariş Miktarı"].dtype)
print("\n=== SATINALMA 'Birim' ÖRNEK BİRİMLER (ilk 10) ===")
print(purchase["Birim"].unique()[:10])
