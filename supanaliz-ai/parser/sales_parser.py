# parser/sales_parser.py

import pandas as pd
from typing import Dict, Any
from .excel_loader import load_excel


SALES_SHEET_NAME = "IASSALHEADLIST"


def parse_sales_excel(
    path: str,
    sheet_name: str = SALES_SHEET_NAME,
) -> Dict[str, Any]:
    """
    Satış Excel'ini okur ve analiz için temiz bir DataFrame + meta bilgiler döner.

    Zorunlu kolonlar:
    - 'Başlangıç Tarihi'
    - 'Genel Toplam (USD)'
    - 'Malzeme'
    - 'MalKodGrup'
    - 'Miktar'
    - 'Miktar Br.'
    """

    df = load_excel(path, sheet_name=sheet_name).copy()

    required_cols = [
        "Başlangıç Tarihi",
        "Genel Toplam (USD)",
        "Malzeme",
        "MalKodGrup",
        "Miktar",
        "Miktar Br.",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Satış datasında eksik kolon(lar) var: {missing}")

    # Tarih
    df["Başlangıç Tarihi"] = pd.to_datetime(
        df["Başlangıç Tarihi"], dayfirst=True, errors="coerce"
    )

    # Numerikler
    df["Genel Toplam (USD)"] = pd.to_numeric(
        df["Genel Toplam (USD)"], errors="coerce"
    )
    df["Miktar"] = pd.to_numeric(df["Miktar"], errors="coerce")

    # Birimler string
    df["Miktar Br."] = df["Miktar Br."].astype(str)

    # Yardımcı zaman kolonları
    df["Yıl"] = df["Başlangıç Tarihi"].dt.year
    df["Ay"] = df["Başlangıç Tarihi"].dt.month

    # Basic kalite metrikleri
    info = {
        "rows": len(df),
        "date_min": df["Başlangıç Tarihi"].min(),
        "date_max": df["Başlangıç Tarihi"].max(),
        "usd_sales_missing": df["Genel Toplam (USD)"].isna().sum(),
        "qty_missing": df["Miktar"].isna().sum(),
        "unit_counts": df["Miktar Br."].value_counts().to_dict(),
    }

    return {"data": df, "meta": info}
