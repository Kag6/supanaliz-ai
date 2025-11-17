# features/sales_features.py

import pandas as pd
import numpy as np
from typing import Dict, Any


def _prepare_sales_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Satış parser'dan gelen df üzerinde sales features hesaplamaları için 
    ortak kolonları ve türev alanları hazırlar.
    Beklenen kolonlar:
    - Başlangıç Tarihi
    - Malzeme
    - MalKodGrup
    - Miktar
    - Genel Toplam (USD)
    """

    required_cols = [
        "Başlangıç Tarihi",
        "Malzeme",
        "MalKodGrup",
        "Miktar",
        "Genel Toplam (USD)",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Sales features için eksik kolon(lar): {missing}")

    df = df.copy()

    df["Yıl"] = df["Başlangıç Tarihi"].dt.year
    df["Ay"] = df["Başlangıç Tarihi"].dt.month
    df["YılAy"] = df["Başlangıç Tarihi"].dt.to_period("M")

    # Ortalama birim fiyat (USD)
    df["unit_price_usd"] = df["Genel Toplam (USD)"] / df["Miktar"]
    df["unit_price_usd"] = df["unit_price_usd"].replace([np.inf, -np.inf], np.nan)

    return df


def compute_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aylık satış hacmi, miktar ve USD bazlı satış toplamları.
    """

    df = _prepare_sales_base(df)

    monthly = (
        df.groupby(["Malzeme", "MalKodGrup", "YılAy"], dropna=False)
        .agg(
            total_qty=("Miktar", "sum"),
            total_sales_usd=("Genel Toplam (USD)", "sum"),
            avg_unit_price_usd=("unit_price_usd", "mean"),
        )
        .reset_index()
    )

    return monthly


def compute_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Malzeme bazında zaman içinde USD satış trendi (slope).
    """

    monthly = compute_monthly_sales(df)
    monthly = monthly.sort_values(["Malzeme", "MalKodGrup", "YılAy"])

    # Time index malzeme bazında verilecek
    trends = []

    for (mat, grp), sub in monthly.groupby(["Malzeme", "MalKodGrup"]):
        sub = sub.sort_values("YılAy").reset_index(drop=True)
        sub["time_idx"] = range(len(sub))

        if len(sub) < 2:
            slope = np.nan
        else:
            x = sub["time_idx"].to_numpy(dtype=float)
            y = sub["total_sales_usd"].to_numpy(dtype=float)
            mask = ~np.isnan(x) & ~np.isnan(y)
            if mask.sum() < 2:
                slope = np.nan
            else:
                a, _b = np.polyfit(x[mask], y[mask], deg=1)
                slope = a

        trends.append(
            {
                "Malzeme": mat,
                "MalKodGrup": grp,
                "sales_trend_slope": slope,
            }
        )

    trend_df = pd.DataFrame(trends)

    # slope yorumlama
    eps = 1e-6
    conds = [
        trend_df["sales_trend_slope"] > eps,
        trend_df["sales_trend_slope"] < -eps,
    ]
    choices = ["artıyor", "düşüyor"]

    trend_df["sales_trend_label"] = np.select(
        conds, choices, default="durağan"
    )

    return trend_df


def compute_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ay bazlı mevsimsellik matrisi:
    Her ürün için ay ortalama satış / yıllık ortalama satış oranı.
    (1.0 üzeri → o ay güçlü, altı → zayıf)
    """

    df = _prepare_sales_base(df)

    monthly = (
        df.groupby(["Malzeme", "MalKodGrup", "Ay"], dropna=False)
        .agg(avg_monthly_sales_usd=("Genel Toplam (USD)", "mean"))
        .reset_index()
    )

    yearly = (
        df.groupby(["Malzeme", "MalKodGrup"])
        .agg(yearly_avg_sales_usd=("Genel Toplam (USD)", "mean"))
        .reset_index()
    )

    season = monthly.merge(yearly, on=["Malzeme", "MalKodGrup"], how="left")
    season["seasonality_index"] = (
        season["avg_monthly_sales_usd"] / season["yearly_avg_sales_usd"]
    )
    season["seasonality_index"] = season["seasonality_index"].replace(
        [np.inf, -np.inf], np.nan
    )

    return season


def compute_top_performers(df: pd.DataFrame, n=20) -> pd.DataFrame:
    """
    USD bazlı en çok satan ürünler.
    """

    df = _prepare_sales_base(df)

    rank = (
        df.groupby(["Malzeme", "MalKodGrup"], dropna=False)
        .agg(
            total_qty=("Miktar", "sum"),
            total_sales_usd=("Genel Toplam (USD)", "sum"),
            avg_unit_price_usd=("unit_price_usd", "mean"),
        )
        .sort_values("total_sales_usd", ascending=False)
        .head(n)
        .reset_index()
    )

    return rank


def compute_risky_decliners(df: pd.DataFrame, n=20) -> pd.DataFrame:
    """
    Düşüş trendi olan ürünlerden en riskli olanlar.
    """

    trend_df = compute_sales_trend(df)
    risky = trend_df.sort_values("sales_trend_slope").head(n)

    return risky


def build_sales_features(sales_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Tüm satış features’larını tek fonksiyonla üretir.
    """

    monthly = compute_monthly_sales(sales_df)
    trend = compute_sales_trend(sales_df)
    season = compute_seasonality(sales_df)
    top = compute_top_performers(sales_df)
    risky = compute_risky_decliners(sales_df)

    return {
        "monthly_sales": monthly,
        "trend": trend,
        "seasonality": season,
        "top_performers": top,
        "risky_decliners": risky,
    }
