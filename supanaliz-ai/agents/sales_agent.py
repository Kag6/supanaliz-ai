# supanaliz-ai/agents/sales_agent.py

from __future__ import annotations

import statistics
from typing import Any, Dict, List


class SalesAgent:
    """
    LLM bağımsız, kural tabanlı satış analisti.
    Girdi: sales_summary (SalesFeatureBuilder çıktısı)
    Çıktı: JSON uyumlu dict
    """

    @staticmethod
    def _month_name_tr(month: int) -> str:
        names = {
            1: "Ocak",
            2: "Şubat",
            3: "Mart",
            4: "Nisan",
            5: "Mayıs",
            6: "Haziran",
            7: "Temmuz",
            8: "Ağustos",
            9: "Eylül",
            10: "Ekim",
            11: "Kasım",
            12: "Aralık",
        }
        return names.get(month, str(month))

    def analyze(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        trend = summary.get("trend", {})
        seasonality = summary.get("seasonality", [])
        material_stats = summary.get("material_stats", [])
        monthly_series = summary.get("monthly_series", [])

        direction = trend.get("direction", "flat")
        pct_change = trend.get("pct_change", 0.0)

        # Trend yorumu
        if direction == "up":
            trend_comment = f"Satış trendi yükseliyor (yaklaşık %{pct_change:.1f} değişim)."
        elif direction == "down":
            trend_comment = f"Satış trendi düşüyor (yaklaşık %{pct_change:.1f} değişim)."
        else:
            trend_comment = "Satış trendi genel olarak yatay seyrediyor."

        # Mevsimsellik yorumu
        peak_months = [
            s for s in seasonality if s.get("normalized_index", 1.0) > 1.10
        ]
        low_months = [
            s for s in seasonality if s.get("normalized_index", 1.0) < 0.90
        ]

        if peak_months:
            peak_str = ", ".join(
                self._month_name_tr(p["month"]) for p in peak_months
            )
            season_comment = f"Talep özellikle şu aylarda yükseliyor: {peak_str}."
        else:
            season_comment = "Belirgin bir mevsimsellik zirvesi tespit edilmedi."

        if low_months:
            low_str = ", ".join(
                self._month_name_tr(p["month"]) for p in low_months
            )
            season_comment += f" Düşük talep dönemleri: {low_str}."

        # Ürün bazlı performans
        sorted_materials = sorted(
            material_stats, key=lambda x: x.get("total_sales", 0.0), reverse=True
        )
        top_materials = sorted_materials[:5]
        low_materials = sorted_materials[-5:] if len(sorted_materials) >= 5 else []

        # Basit risk puanı (0-100)
        risk_score = self._compute_risk_score(direction, monthly_series)

        # 3-6 aylık öngörü yorumu
        if direction == "up":
            forecast_comment = (
                "Trend yukarı; üretim ve stok planlamasında artan talep senaryosuna göre hareket edilmesi gerekiyor."
            )
        elif direction == "down":
            forecast_comment = (
                "Trend aşağı; stok birikimi ve iskontolu satış riskine karşı hacimlere dikkat edilmeli."
            )
        else:
            forecast_comment = (
                "Trend yatay; mevcut kapasite ve stok seviyesi çoğunlukla yeterli görünüyor."
            )

        actions: List[str] = []
        if direction == "up":
            actions.append(
                "Yüksek performanslı ürünlerde kapasite ve tedarik güvence altına alın."
            )
        if direction == "down":
            actions.append(
                "Düşen ürünlerde kampanya, paketleme veya ürün karması revizyonu düşünülmeli."
            )
        if risk_score > 70:
            actions.append(
                "Talep dalgalanmaları yüksek; güvenli stok politikası ve esnek üretim planı kurgulanmalı."
            )

        return {
            "trend_comment": trend_comment,
            "seasonality_comment": season_comment,
            "high_performers": top_materials,
            "low_performers": low_materials,
            "forecast_comment_3_6m": forecast_comment,
            "risk_score": float(risk_score),
            "actions": actions,
        }

    def _compute_risk_score(
        self, direction: str, monthly_series: List[Dict[str, Any]]
    ) -> float:
        """
        Basit risk metriği:
        - Trend aşağı → risk +
        - Aylık satış volatilitesi yüksek → risk +
        """
        if not monthly_series:
            return 50.0

        values = [m["total_sales"] for m in monthly_series]
        if len(values) < 2:
            base = 40.0
        else:
            mean = statistics.mean(values)
            if mean == 0:
                cv = 0
            else:
                cv = statistics.pstdev(values) / mean
            base = min(100.0, 40.0 + cv * 60.0)

        if direction == "down":
            base += 20.0
        elif direction == "up":
            base -= 10.0

        return max(0.0, min(100.0, base))
