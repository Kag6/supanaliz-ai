# features/purchase_features.py

import pandas as pd
import numpy as np
from typing import Dict, Any


def _prepare_purchase_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Purchase parser'dan gelen df üzerinde, feature hesaplamaları için
    ortak kullanılacak kolonları ve türev alanları hazırlar.
    Beklenen kolonlar:
    - Sipariş Tarihi (datetime)
    - Malzeme
    - MalzemeGrup
    - Birim
    - Sipariş Miktarı
    - Birim Maliyet USD
    - Kalem Toplam USD
    - Lead Time (days)
    - Tedarikçi Num. (opsiyonel ama çok faydalı)
    - İsim (tedarikçi adı)
    """
    required_cols = [
        "Sipariş Tarihi",
        "Malzeme",
        "MalzemeGrup",
        "Birim",
        "Sipariş Miktarı",
        "Birim Maliyet USD",
        "Kalem Toplam USD",
        "Lead Time (days)",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Purchase features için eksik kolon(lar): {missing}")

    df = df.copy()

    # Zaman alanları
    df["Yıl"] = df["Sipariş Tarihi"].dt.year
    df["Ay"] = df["Sipariş Tarihi"].dt.month
    df["YılAy"] = df["Sipariş Tarihi"].dt.to_period("M")

    return df


def compute_material_features(purchase_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ürün (Malzeme) bazlı özellikler:
    - toplam sipariş adedi (satır sayısı)
    - toplam miktar
    - toplam maliyet (USD)
    - ortalama birim maliyet (USD)
    - maliyet volatilitesi (std, CV)
    - ortalama lead time (gün)
    - lead time dağılım istatistikleri
    """
    df = _prepare_purchase_base(purchase_df)

    group_cols = ["Malzeme", "MalzemeGrup", "Birim"]

    grouped = df.groupby(group_cols, dropna=False)

    agg = grouped.agg(
        line_count=("Sipariş Miktarı", "size"),
        total_qty=("Sipariş Miktarı", "sum"),
        total_cost_usd=("Kalem Toplam USD", "sum"),
        avg_unit_cost_usd=("Birim Maliyet USD", "mean"),
        std_unit_cost_usd=("Birim Maliyet USD", "std"),
        avg_lead_time_days=("Lead Time (days)", "mean"),
        p50_lead_time=("Lead Time (days)", "median"),
        p90_lead_time=("Lead Time (days)", lambda x: x.quantile(0.9)),
        max_lead_time=("Lead Time (days)", "max"),
    ).reset_index()

    # Volatilite metriği: Coefficient of Variation (CV)
    agg["cv_unit_cost"] = agg["std_unit_cost_usd"] / agg["avg_unit_cost_usd"]
    agg["cv_unit_cost"] = agg["cv_unit_cost"].replace([np.inf, -np.inf], np.nan)

    # Risk skoru (ürün maliyet volatilitesine göre kabaca)
    # CV 0.0 → risk 0, CV 0.5+ → risk 100'e yaklaşır
    agg["cost_volatility_risk"] = (
        agg["cv_unit_cost"]
        .clip(lower=0, upper=0.5)
        .fillna(0)
        .pipe(lambda s: (s / 0.5) * 100)
    )

    return agg


def compute_supplier_features(purchase_df: pd.DataFrame) -> pd.DataFrame:
    """
    Tedarikçi bazlı özellikler:
    - toplam satır sayısı
    - toplam miktar
    - toplam maliyet (USD)
    - ortalama birim maliyet
    - ortalama lead time
    - gecikme / uzun lead time oranı
    - teslimi olmayan satır oranı
    - tedarikçi risk skoru (0-100)
    """
    df = _prepare_purchase_base(purchase_df)

    # Tedarikçi kolonları yoksa, sadece MalzemeGrup üzerinden analiz yapılır
    if "Tedarikçi Num." in df.columns:
        supplier_cols = ["Tedarikçi Num.", "İsim"]
    else:
        supplier_cols = ["MalzemeGrup"]  # fall-back

    # Teslimi hiç olmayanları ayır
    no_delivery = df["Lead Time (days)"].isna()

    # "Uzun lead time" tanımı: 30+ gün (isteğe göre değiştirilebilir)
    long_lead = df["Lead Time (days)"] >= 30

    grouped = df.groupby(supplier_cols, dropna=False)

    agg = grouped.agg(
        line_count=("Sipariş Miktarı", "size"),
        total_qty=("Sipariş Miktarı", "sum"),
        total_cost_usd=("Kalem Toplam USD", "sum"),
        avg_unit_cost_usd=("Birim Maliyet USD", "mean"),
        avg_lead_time_days=("Lead Time (days)", "mean"),
        median_lead_time=("Lead Time (days)", "median"),
        max_lead_time=("Lead Time (days)", "max"),
        long_lead_count=("Lead Time (days)", lambda x: (x >= 30).sum()),
        no_delivery_count=("Lead Time (days)", lambda x: x.isna().sum()),
    ).reset_index()

    # Oranlar
    agg["long_lead_ratio"] = agg["long_lead_count"] / agg["line_count"]
    agg["no_delivery_ratio"] = agg["no_delivery_count"] / agg["line_count"]

    # Tedarikçi risk skoru:
    # - uzun lead time oranı (ağırlık 0.6)
    # - teslim yok oranı (ağırlık 0.4)
    # - ortalama lead time (normalize, 60 gün ve üzeri = max risk)
    lead_norm = (
        agg["avg_lead_time_days"]
        .fillna(0)
        .clip(lower=0, upper=60) / 60.0
    )

    agg["supplier_risk_score"] = (
        0.6 * agg["long_lead_ratio"].fillna(0)
        + 0.4 * agg["no_delivery_ratio"].fillna(0)
        + 0.5 * lead_norm
    )

    agg["supplier_risk_score"] = (
        agg["supplier_risk_score"]
        .clip(lower=0, upper=2.0)  # kaba güvenlik
        .pipe(lambda s: (s / 2.0) * 100)  # 0-100 skalası
    )

    return agg


def compute_price_trend(purchase_df: pd.DataFrame) -> pd.DataFrame:
    """
    Malzeme bazında aylık ortalama birim maliyet (USD) üzerinden
    kaba bir 'trend' metriği hesaplar.
    Trend = zaman'a karşı (ay index'i) birim maliyet için lineer regresyon slope'u.

    Pozitif slope → maliyet artıyor
    Negatif slope → maliyet düşüyor
    """
    df = _prepare_purchase_base(purchase_df)

    # Aylık ortalama birim maliyet
    monthly = (
        df
        .groupby(["Malzeme", "MalzemeGrup", "YılAy"], dropna=False)
        .agg(avg_unit_cost_usd=("Birim Maliyet USD", "mean"))
        .reset_index()
    )

    # Malzeme bazında zaman indeksini ayrı ayrı set etmek daha mantıklı
    monthly = monthly.sort_values(["Malzeme", "MalzemeGrup", "YılAy"])

    trends = []

    for (mat, grp), sub in monthly.groupby(["Malzeme", "MalzemeGrup"]):
        # Her malzeme-grup için kendi time_idx'ini ver
        sub = sub.sort_values("YılAy").reset_index(drop=True)
        sub["time_idx"] = range(len(sub))

        if len(sub) < 2:
            slope = np.nan
        else:
            x = sub["time_idx"].to_numpy(dtype=float)
            y = sub["avg_unit_cost_usd"].to_numpy(dtype=float)
            mask = ~np.isnan(x) & ~np.isnan(y)
            if mask.sum() < 2:
                slope = np.nan
            else:
                a, _b = np.polyfit(x[mask], y[mask], deg=1)
                slope = a

        trends.append(
            {
                "Malzeme": mat,
                "MalzemeGrup": grp,
                "price_trend_slope": slope,
            }
        )

    trend_df = pd.DataFrame(trends)

    # Trend yorumunu kaba etiketle
    eps = 1e-6
    conds = [
        trend_df["price_trend_slope"] > eps,
        trend_df["price_trend_slope"] < -eps,
    ]
    choices = ["artıyor", "düşüyor"]
    trend_df["price_trend_label"] = np.select(
        conds,
        choices,
        default="durağan",
    )

    return trend_df



def build_purchase_features(purchase_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Purchase tarafındaki tüm feature özetlerini tek noktadan üretir.
    Output JSON-friendly dict yapısı:
    {
        "material_features": [...],
        "supplier_features": [...],
        "price_trend": [...],
    }
    """
    material_fe = compute_material_features(purchase_df)
    supplier_fe = compute_supplier_features(purchase_df)
    price_trend_fe = compute_price_trend(purchase_df)

    return {
        "material_features": material_fe,
        "supplier_features": supplier_fe,
        "price_trend": price_trend_fe,
    }
