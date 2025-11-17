import pandas as pd


def build_matching_table(sales_df: pd.DataFrame, purchase_df: pd.DataFrame) -> pd.DataFrame:
    """
    Satış ve satın alma verilerini ürün bazında doğru şekilde eşleştirir.
    Kritik düzeltmeler:
    - Birim tekrarları parçalamaz (tek satır)
    - Satış sadece Malzeme bazında toplanır
    - Satınalma sadece Malzeme bazında toplanır
    - Birimler ayrı kolonlarda tutulur
    """

    # --- 1) SATIŞ AGG (SADECE MALZEME BAZLI) ---
    sales_agg = (
        sales_df
        .groupby("Malzeme", as_index=False)
        .agg(
            total_sales_qty=("Miktar", "sum"),
            total_sales_usd=("Genel Toplam (USD)", "sum"),
            sales_unit=("Miktar Br.", "first"),
            MalKodGrup=("MalKodGrup", "first"),
        )
    )
    sales_agg["avg_sales_unit_price_usd"] = (
        sales_agg["total_sales_usd"] / sales_agg["total_sales_qty"]
    )

    # --- 2) PURCHASE AGG (SADECE MALZEME BAZLI) ---
    purchase_agg = (
        purchase_df
        .groupby("Malzeme", as_index=False)
        .agg(
            total_purchase_qty=("Sipariş Miktarı", "sum"),
            total_purchase_cost_usd=("Kalem Toplam USD", "sum"),
            purchase_unit=("Birim", "first"),
            MalzemeGrup=("MalzemeGrup", "first"),
        )
    )
    purchase_agg["avg_purchase_unit_cost_usd"] = (
        purchase_agg["total_purchase_cost_usd"] / purchase_agg["total_purchase_qty"]
    )

    # --- 3) FULL OUTER KEY SET ---
    all_items = pd.DataFrame({
        "Malzeme": pd.Index(sales_agg["Malzeme"]).union(purchase_agg["Malzeme"])
    })

    # --- 4) MERGE ---
    match = (
        all_items
        .merge(sales_agg, on="Malzeme", how="left")
        .merge(purchase_agg, on="Malzeme", how="left")
    )

    # --- 5) Match Status ---
    match["match_status"] = match.apply(
        lambda row:
        "both" if pd.notna(row["total_sales_qty"]) and pd.notna(row["total_purchase_qty"])
        else "sales_only" if pd.notna(row["total_sales_qty"])
        else "purchase_only" if pd.notna(row["total_purchase_qty"])
        else "none",
        axis=1
    )

    # --- 6) Stokout risk (yalnız satış varsa değil!) ---
    match["stokout_risk_flag"] = (
        (match["match_status"] == "both") &
        (match["total_sales_qty"] > match["total_purchase_qty"])
    )

    return match


def summarize_matching(df: pd.DataFrame):
    return {
        "total_products": len(df),
        "count_both": int((df["match_status"] == "both").sum()),
        "count_sales_only": int((df["match_status"] == "sales_only").sum()),
        "count_no_purchase": int((df["match_status"] == "sales_only").sum()),
        "stockout_risk_count": int(df["stokout_risk_flag"].sum()),
    }
