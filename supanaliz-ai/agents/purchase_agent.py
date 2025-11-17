# supanaliz-ai/agents/purchase_agent.py

from __future__ import annotations

from typing import Any, Dict, List


class PurchaseAgent:
    """
    LLM bağımsız, kural tabanlı satınalma analisti.
    Girdi: purchase_summary (PurchaseFeatureBuilder çıktısı)
    Çıktı: JSON uyumlu dict
    """

    def analyze(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        lead_stats = summary.get("lead_time_stats", {})
        supplier_stats = summary.get("supplier_stats", [])
        material_stats = summary.get("material_stats", [])
        order_totals = summary.get("order_totals", [])

        avg_lead = lead_stats.get("overall_avg_lead_time_days")
        lead_std = lead_stats.get("overall_std_lead_time_days")

        # Lead time risk yorumu
        if avg_lead is None:
            lead_comment = "Lead time verisi yetersiz; teslimat performansı analiz edilemiyor."
            lead_risk_score = 50.0
        else:
            if avg_lead <= 15:
                lead_comment = f"Ortalama lead time yaklaşık {avg_lead:.1f} gün, oldukça makul."
                lead_risk_score = 30.0
            elif avg_lead <= 30:
                lead_comment = f"Ortalama lead time {avg_lead:.1f} gün seviyesinde; kritik ürünler için güvenli stok gözden geçirilmeli."
                lead_risk_score = 50.0
            else:
                lead_comment = f"Ortalama lead time {avg_lead:.1f} günü aşıyor; ciddi tedarik riski var."
                lead_risk_score = 75.0

        # Fiyat volatilitesi yorumu (global bakış)
        vol_scores: List[float] = []
        for mat in material_stats:
            avg_p = mat.get("avg_unit_price")
            std_p = mat.get("unit_price_std")
            if avg_p and std_p:
                cv = std_p / avg_p
                vol_scores.append(cv)

        if vol_scores:
            avg_cv = sum(vol_scores) / len(vol_scores)
            if avg_cv < 0.15:
                price_comment = "Genel olarak birim fiyatlarda volatilite düşük."
            elif avg_cv < 0.30:
                price_comment = "Birim fiyat volatilitesi orta seviyede; kritik tedarikçilerle kontrat şartları gözden geçirilebilir."
            else:
                price_comment = "Birim fiyatlarda yüksek oynaklık var; sözleşme ve alternatif tedarikçi stratejisi gerekiyor."
        else:
            price_comment = "Fiyat volatilitesi için yeterli veri yok."

        # Tedarikçi bazlı risk listesi (yüksek risk_score)
        risky_suppliers = [
            s for s in supplier_stats if s.get("risk_score", 0) >= 60
        ]
        risky_suppliers = sorted(
            risky_suppliers,
            key=lambda x: x.get("risk_score", 0),
            reverse=True,
        )

        # PO bazında anomali (en büyük 5 sipariş)
        large_orders = sorted(
            order_totals, key=lambda x: x.get("order_total", 0), reverse=True
        )[:5]

        # Stokout risk sinyali:
        # Çok uzun lead time + yüksek toplam sipariş değerine sahip ürünler
        stockout_signals: List[Dict[str, Any]] = []
        for mat in material_stats:
            if mat.get("avg_lead_time_days") and mat["avg_lead_time_days"] > 30:
                stockout_signals.append(
                    {
                        "material": mat.get("material"),
                        "material_group": mat.get("material_group"),
                        "avg_lead_time_days": mat.get("avg_lead_time_days"),
                        "total_order_value": mat.get("total_order_value"),
                    }
                )

        actions: List[str] = []
        if lead_risk_score >= 60:
            actions.append(
                "Uzun lead time'a sahip kritik malzemeler için alternatif tedarikçi arayışı başlatılmalı."
            )
        if risky_suppliers:
            actions.append(
                "Yüksek risk skoruna sahip tedarikçilerle sözleşme, fiyat ve teslimat şartları yeniden müzakere edilmeli."
            )
        if stockout_signals:
            actions.append(
                "Lead time'ı uzun olan malzemeler için güvenli stok seviyeleri netleştirilmeli."
            )

        return {
            "lead_time_comment": lead_comment,
            "price_volatility_comment": price_comment,
            "lead_time_risk_score": float(lead_risk_score),
            "risky_suppliers": risky_suppliers,
            "large_orders": large_orders,
            "stockout_signals": stockout_signals,
            "actions": actions,
        }
