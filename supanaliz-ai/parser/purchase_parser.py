# parser/purchase_parser.py

import pandas as pd
from typing import Dict, Any
from .excel_loader import load_excel
from .fx_parser import load_fx_rates


PURCHASE_SHEET_NAME = "IASPURHEADLISTTREE"


def parse_purchase_excel(
    path: str,
    fx_path: str,
    sheet_name: str = PURCHASE_SHEET_NAME,
) -> Dict[str, Any]:
    """
    Satınalma Excel'ini ve kur tablosunu okur, temizlenmiş DataFrame döner.

    Zorunlu kolonlar:
    - 'Sipariş Tarihi'
    - 'Teslim Tarihi'
    - 'Sipariş Miktarı'
    - 'Fiyat'
    - 'Malzeme'
    - 'MalzemeGrup'
    - 'Birim'
    """

    df = load_excel(path, sheet_name=sheet_name).copy()

    required_cols = [
        "Sipariş Tarihi",
        "Teslim Tarihi",
        "Sipariş Miktarı",
        "Fiyat",
        "Malzeme",
        "MalzemeGrup",
        "Birim",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Satınalma datasında eksik kolon(lar) var: {missing}")

    # Tarihler
    df["Sipariş Tarihi"] = pd.to_datetime(
        df["Sipariş Tarihi"], dayfirst=True, errors="coerce"
    )
    df["Teslim Tarihi"] = pd.to_datetime(
        df["Teslim Tarihi"], dayfirst=True, errors="coerce"
    )

    # 1975 -> geçersiz teslim tarihi
    mask_1975 = df["Teslim Tarihi"].dt.year == 1975
    df.loc[mask_1975, "Teslim Tarihi"] = pd.NaT

    # Numerikler
    df["Sipariş Miktarı"] = pd.to_numeric(df["Sipariş Miktarı"], errors="coerce")
    df["Fiyat"] = pd.to_numeric(df["Fiyat"], errors="coerce")

    # Kalem toplamı (lokal para birimi)
    df["Kalem Toplam TL"] = df["Sipariş Miktarı"] * df["Fiyat"]

    # Lead time (gün)
    df["Lead Time (days)"] = (
        df["Teslim Tarihi"] - df["Sipariş Tarihi"]
    ).dt.days
    # Teslim yoksa lead time NaN zaten

    # Birim string
    df["Birim"] = df["Birim"].astype(str)

    # Kur serisini yükle
    fx_daily = load_fx_rates(fx_path)  # Tarih indexli Series

    # Her sipariş tarihi için kur çek
    # (tarih indexli seride direkt loc ile – önceden ffill/bfill yaptık)
    def get_fx(date):
        if pd.isna(date):
            return pd.NA
        try:
            return fx_daily.loc[date.normalize()]
        except KeyError:
            # Teoride olmamalı, asfreq+ffill+bfill yaptık
            return pd.NA

    df["FX_USDTRY"] = df["Sipariş Tarihi"].apply(get_fx)

    # USD cinsinden birim maliyet ve toplam maliyet
    df["Birim Maliyet USD"] = df["Fiyat"] / df["FX_USDTRY"]
    df["Kalem Toplam USD"] = df["Kalem Toplam TL"] / df["FX_USDTRY"]

    info = {
        "rows": len(df),
        "date_min": df["Sipariş Tarihi"].min(),
        "date_max": df["Sipariş Tarihi"].max(),
        "qty_missing": df["Sipariş Miktarı"].isna().sum(),
        "price_missing": df["Fiyat"].isna().sum(),
        "fx_missing": df["FX_USDTRY"].isna().sum(),
        "unit_counts": df["Birim"].value_counts().to_dict(),
    }

    return {"data": df, "meta": info}
