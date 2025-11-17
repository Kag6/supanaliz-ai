from parser.sales_parser import parse_sales_excel
from parser.purchase_parser import parse_purchase_excel
from features.profit_features import build_profit_features

sales = parse_sales_excel('data/AllTimeSatisPivotLast.xls')['data']
purchase = parse_purchase_excel('data/AllTimeSatinAlmaPivotLast.xls','data/fx_rates.xlsx')['data']

features = build_profit_features(sales, purchase)

profit_core = features['product_profit']
print("profit_core:", len(profit_core))
