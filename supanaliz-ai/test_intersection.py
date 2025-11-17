import pandas as pd
from parser.sales_parser import parse_sales_excel
from parser.purchase_parser import parse_purchase_excel

sales = parse_sales_excel('data/AllTimeSatisPivotLast.xls')['data']
purchase = parse_purchase_excel('data/AllTimeSatinAlmaPivotLast.xls','data/fx_rates.xlsx')['data']

# Satıştaki ürün kodları
sales_codes = set(sales['Malzeme'].unique())

# Satınalmadaki ürün kodları
purchase_codes = set(purchase['Malzeme'].unique())

# Kesişim
intersection = sales_codes.intersection(purchase_codes)

print("Satış ürün adedi:", len(sales_codes))
print("Satınalma ürün adedi:", len(purchase_codes))
print("Her iki tarafta ortak ürün:", len(intersection))
