# supanaliz-ai/agents/decision_agent.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MaterialMatch:
    sales_material: Optional[str]
    sales_material_group: Optional[str]
    purchase_material: Optional[str]
    purchase_material_group: Optional[str]
    match_type: str  # "direct", "group", "none"
    sales_total: float
    purchase_total: float


class DecisionAgent:
    """
    Satış ve satınalma ajan çıktısını birleştirip yönetici özeti üretir.
    Malzeme eşleştirme motoru zorunlu parça.
    """

    def _build_material_index(
        self, material_stats: List[Dict[str, Any]], key: str
    ) -> Dict[str, Dict[str, Any]]:
        idx: Dict[str, Dict[str, Any]] = {}
        for m in material_stats:
            val = m.get(key)
            if val:
                idx[str(val)] = m
        return idx

    def _material_matching_engine(
        self,
        sales_material_stats: List[Dict[str, Any]],
        purchase_material_stats: List[Dict[str, Any]],
    ) -> List[MaterialMatch]:
        """
        1) Direkt malzeme kodu eşleşmesi
        2) Grup kodu eşleşmesi (MalzemeGrup[:-1] == MalKodGrup)
        3) Hiç eşleşmeyen → match_type = "none"
        """
        # Purchase tarafında lookup indexleri
        purchase_by_material = self._build_material_index(
            purchase_material_stats, "material"
        )
        purchase_by_group_clean: Dict[str, Dict[str, Any]] = {}
        for m in purchase_material_stats:
            group = m.get("material_group")
            if group:
                clean = str(group)[:-1] if len(str(group)) > 0 else ""
                if clean:
                    purchase_by_group_clean[clean] = m

        matches: List[MaterialMatch] = []

        for s in sales_material_stats:
            s_mat = s.get("material")
            s_grp = s.get("material_group")
            sales_total = float(s.get("total_sales", 0.0))

            # 1) Direkt malzeme eşleşmesi
            direct = purchase_by_material.get(str(s_mat)) if s_mat else None

            if direct:
                matches.append(
                    MaterialMatch(
                        sales_material=s_mat,
                        sales_material_group=s_grp,
                        purchase_material=direct.get("material"),
                        purchase_material_group=direct.get("material_group"),
                        match_type="direct",
                        sales_total=sales_total,
                        purchase_total=float(
                            direct.get("total_order_value", 0.0)
                        ),
                    )
                )
                continue

            # 2) Grup eşleşmesi
            if s_grp:
                p = purchase_by_group_clean.get(str(s_grp))
            else:
                p = None

            if p:
                matches.append(
                    MaterialMatch(
                        sales_material=s_mat,
                        sales_material_group=s_grp,
                        purchase_material=p.get("material"),
                        purchase_material_group=p.get("material_group"),
                        match_type="group",
                        sales_total=sales_total,
                        purchase_total=float(
                            p.get("total_order_value", 0.0)
                        ),
                    )
                )
            else:
                matches.append(
                    MaterialMatch(
                        sales_material=s_mat,
                        sales_material_group=s_grp,
                        purchase_material=None,
                        purchase_material_group=None,
                        match_type="none",
                        sales_total=sales_total,
                        purchase_total=0.0,
                    )
                )

        return matches

    def analyze(
        self,
        sales_summary: Dict[str, Any],
        purchase_summary: Dict[str, Any],
        sales_agent_output: Dict[str, Any],
        purchase_agent_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        DecisionAgent ana fonksiyonu.
        """

        sales_trend = sales_summary.get("trend", {})
        direction = sales_trend.get("direction", "flat")

        sales_material_stats = sales_summary.get("material_stats", [])
        purchase_material_stats = purchase_summary.get("material_stats", [])

        matches = self._material_matching_engine(
            sales_material_stats, purchase_material_stats
        )

        # Satış artışı + satınalma yetersizliği
        sales_up_purchase_risk: List[Dict[str, Any]] = []
        if direction == "up":
            for m in matches:
                if m.match_type in ("direct", "group"):
                    # Çok kaba eşik: satınalma toplamı satış toplamının %70'inden azsa risk
                    if m.purchase_total < 0.7 * m.sales_total:
                        sales_up_purchase_risk.append(
                            {
                                "material": m.sales_material,
                                "material_group": m.sales_material_group,
                                "sales_total": m.sales_total,
                                "purchase_total": m.purchase_total,
                                "match_type": m.match_type,
                                "message": "Satış artarken satınalma hacmi geride; stokout riski.",
                            }
                        )

        # Fiyat artışı + satış düşüşü (yaklaşımı kaba, ama sinyal verir)
        price_vol_comment = purchase_agent_output.get(
            "price_volatility_comment", ""
        )
        sales_down_price_risk: List[str] = []
        if direction == "down" and "yüksek" in price_vol_comment.lower():
            sales_down_price_risk.append(
                "Satış trendi aşağı, satınalma tarafında fiyat volatilitesi yüksek; fiyat baskısı kaynaklı talep kaybı riski var."
            )

        # Kritik ürün listesi: 
        #  - match_type == "none" olanlar (stokout riski)
        #  - satış güçlü, satınalma zayıf olanlar
        critical_products: List[Dict[str, Any]] = []
        for m in matches:
            if m.match_type == "none" and m.sales_total > 0:
                critical_products.append(
                    {
                        "material": m.sales_material,
                        "material_group": m.sales_material_group,
                        "reason": "Satış var, satınalma datasında eşleşen malzeme yok (stokout riski).",
                    }
                )
        # Ek olarak yukarıdaki risk listesinde olanları da ekle
        for r in sales_up_purchase_risk:
            critical_products.append(
                {
                    "material": r["material"],
                    "material_group": r["material_group"],
                    "reason": "Satış hacmi satınalmadan hızlı büyüyor; kapasite ve stok riski.",
                }
            )

        # Öncelik sırası: kritik ürünler + yüksek riskli tedarikçiler
        risky_suppliers = purchase_agent_output.get("risky_suppliers", [])
        priority_list: List[Dict[str, Any]] = []

        for c in critical_products:
            priority_list.append(
                {
                    "type": "material",
                    "id": c.get("material"),
                    "label": f"Malzeme: {c.get('material')} ({c.get('material_group')})",
                    "reason": c["reason"],
                }
            )

        for s in risky_suppliers[:5]:
            priority_list.append(
                {
                    "type": "supplier",
                    "id": s.get("supplier_id"),
                    "label": f"Tedarikçi: {s.get('supplier_name')}",
                    "reason": f"Tedarikçi risk skoru yüksek ({s.get('risk_score'):.1f}).",
                }
            )

        # Yönetici özeti
        management_summary: List[str] = []
        management_summary.append(
            sales_agent_output.get("trend_comment", "Satış trend analizi mevcut.")
        )
        management_summary.append(
            purchase_agent_output.get(
                "lead_time_comment", "Lead time analizi mevcut."
            )
        )
        if critical_products:
            management_summary.append(
                f"{len(critical_products)} adet kritik malzeme tespit edildi; stokout ve kapasite riskleri içeriyor."
            )
        if risky_suppliers:
            management_summary.append(
                f"{len(risky_suppliers)} tedarikçi yüksek risk skoruna sahip."
            )

        # 3 maddelik aksiyon planı
        action_plan: List[str] = []

        if critical_products:
            action_plan.append(
                "Kritik malzemeler için (stokout riski olanlar) satınalma planı ve güvenli stok seviyeleri ivedilikle gözden geçirilsin."
            )
        if risky_suppliers:
            action_plan.append(
                "Yüksek riskli tedarikçilerle teslimat ve fiyat koşulları yeniden müzakere edilsin; alternatif tedarikçi opsiyonları oluşturulsun."
            )
        action_plan.append(
            "Satış ve satınalma ajan çıktıları haftalık toplantılarda gözden geçirilerek üretim planı ve bütçe revizyonlarına veri sağlayacak şekilde kullanılmalı."
        )

        return {
            "matches": [m.__dict__ for m in matches],
            "sales_up_purchase_risk": sales_up_purchase_risk,
            "sales_down_price_risk": sales_down_price_risk,
            "critical_products": critical_products,
            "priority_list": priority_list,
            "management_summary": management_summary,
            "action_plan": action_plan,
        }
