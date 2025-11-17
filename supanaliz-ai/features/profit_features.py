# features/profit_features.py

import pandas as pd
import numpy as np
from typing import Dict, Any
from agents.matching_engine import build_matching_table, summarize_matching


# ---------------------------------------------------
# 1) KÂR HESABI
# ---------------------------------------------------
def compute_profitability(matching_df: pd.DataFrame) -> pd.DataFrame:
    df = matching_df.copy()

    df["has_sales"] = df["total_sales_qty"].notna()
    df["has_purchase"] = df["total_purchase_qty"].notna()

    # Satış fiyatı
    df["sales_unit_price_usd"] = (
        df["avg_sales_unit_price_usd"]
        if "avg_sales_unit_price_usd" in df.columns
        else df["total_sales_usd"] / df["total_sales_qty"]
    )

    # Maliyet
    df["purchase_unit_cost_usd"] = (
        df["avg_purchase_unit_cost_usd"]
        if "avg_purchase_unit_cost_usd" in df.columns
        else df["total_purchase_cost_usd"] / df["total_purchase_qty"]
    )

    df["sales_unit_price_usd"].replace([np.inf, -np.inf], np.nan, inplace=True)
    df["purchase_unit_cost_usd"].replace([np.inf, -np.inf], np.nan, inplace=True)

    df["profit_per_unit_usd"] = df["sales_unit_price_usd"] - df["purchase_unit_cost_usd"]
    df["profit_margin_pct"] = (
        df["profit_per_unit_usd"] / df["purchase_unit_cost_usd"] * 100.0
    )

    df["profit_margin_pct"].replace([np.inf, -np.inf], np.nan, inplace=True)
    df["total_profit_usd"] = df["profit_per_unit_usd"] * df["total_sales_qty"]

    df["unit_mismatch_flag"] = df["sales_unit"].ne(df["purchase_unit"])

    def _profit_quality(r):
        if r["has_sales"] and r["has_purchase"]:
            if r["sales_unit"] == "AD" and r["purchase_unit"] == "AD":
                return "strict_AD"
            elif r["unit_mismatch_flag"]:
                return "unit_mismatch"
            else:
                return "matched_other_unit"
        elif r["has_sales"] and not r["has_purchase"]:
            return "missing_cost"
        elif not r["has_sales"] and r["has_purchase"]:
            return "missing_sales"
        return "no_match"

    df["profit_quality"] = df.apply(_profit_quality, axis=1)

    return df


# ---------------------------------------------------
# 2) ANA FONKSİYON
# ---------------------------------------------------
def build_profit_features(sales_df: pd.DataFrame, purchase_df: pd.DataFrame) -> Dict[str, Any]:

    matching_df = build_matching_table(sales_df, purchase_df)
    base_summary = summarize_matching(matching_df)

    profit_df = compute_profitability(matching_df)

    # Core set = satış + satınalma + maliyet kolonları dolu
    core_mask = (
        profit_df["has_sales"]
        & profit_df["has_purchase"]
        & profit_df["total_purchase_qty"].notna()
        & profit_df["total_purchase_cost_usd"].notna()
    )

    profit_core = profit_df[core_mask].copy()

    # STOUT
    stokout_mask = (
        (profit_core["total_purchase_qty"].notna())
        & (profit_core["total_sales_qty"] > profit_core["total_purchase_qty"])
    )

    stokout_df = profit_core[stokout_mask].copy()
    stokout_df["stockout_severity"] = (
        stokout_df["total_sales_qty"] - stokout_df["total_purchase_qty"]
    )

    # Kârlılık sıralaması
    profit_ok = profit_core[
        profit_core["profit_quality"].isin(
            ["strict_AD", "matched_other_unit", "unit_mismatch"]
        )
    ].copy()

    top_profitable = profit_ok.sort_values("total_profit_usd", ascending=False).head(20)
    worst_profitable = profit_ok.sort_values("total_profit_usd", ascending=True).head(20)

    summary = {
        **base_summary,
        "total_products_with_cost_and_sales": len(profit_core),
        "stockout_candidates_count": len(stokout_df),
    }

    return {
        "matching_summary": summary,
        "product_profit": profit_core,
        "stokout_candidates": stokout_df,
        "top_profitable": top_profitable,
        "worst_profitable": worst_profitable,
    }
