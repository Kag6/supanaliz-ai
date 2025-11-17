# supanaliz-ai/api/main.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from parser import parse_sales_excel, parse_purchase_excel
from features import SalesFeatureBuilder, PurchaseFeatureBuilder
from agents import SalesAgent, PurchaseAgent, DecisionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supanaliz-api")


# ==============
# Pydantic Modeller (basitleştirilmiş)
# ==============

class SalesParseRequest(BaseModel):
    path: str = Field(..., description="Satış Excel dosya yolu")
    sheet_name: Optional[str] = Field(
        default=None, description="Opsiyonel sheet adı (örn: IASSALHEADLIST)"
    )


class PurchaseParseRequest(BaseModel):
    path: str = Field(..., description="Satınalma Excel dosya yolu")
    sheet_name: Optional[str] = Field(
        default=None, description="Opsiyonel sheet adı"
    )


class SalesSummaryModel(BaseModel):
    meta: Dict[str, Any]
    monthly_series: List[Dict[str, Any]]
    trend: Dict[str, Any]
    seasonality: List[Dict[str, Any]]
    aggregates: Dict[str, Any]
    material_stats: List[Dict[str, Any]]
    warnings: Optional[List[str]] = []


class PurchaseSummaryModel(BaseModel):
    meta: Dict[str, Any]
    order_totals: List[Dict[str, Any]]
    lead_time_stats: Dict[str, Any]
    material_stats: List[Dict[str, Any]]
    supplier_stats: List[Dict[str, Any]]
    warnings: Optional[List[str]] = []


class SalesAgentOutputModel(BaseModel):
    trend_comment: str
    seasonality_comment: str
    high_performers: List[Dict[str, Any]]
    low_performers: List[Dict[str, Any]]
    forecast_comment_3_6m: str
    risk_score: float
    actions: List[str]


class PurchaseAgentOutputModel(BaseModel):
    lead_time_comment: str
    price_volatility_comment: str
    lead_time_risk_score: float
    risky_suppliers: List[Dict[str, Any]]
    large_orders: List[Dict[str, Any]]
    stockout_signals: List[Dict[str, Any]]
    actions: List[str]


class DecisionRequest(BaseModel):
    sales_summary: SalesSummaryModel
    purchase_summary: PurchaseSummaryModel
    sales_agent_output: SalesAgentOutputModel
    purchase_agent_output: PurchaseAgentOutputModel


class DecisionOutputModel(BaseModel):
    matches: List[Dict[str, Any]]
    sales_up_purchase_risk: List[Dict[str, Any]]
    sales_down_price_risk: List[str]
    critical_products: List[Dict[str, Any]]
    priority_list: List[Dict[str, Any]]
    management_summary: List[str]
    action_plan: List[str]


app = FastAPI(
    title="SUPANALİZ AI – Offline Decision Lab API",
    version="0.1.0",
    description="Satış + Satınalma + DecisionAgent için offline FastAPI backend.",
)


# ==============
# Endpointler
# ==============

@app.post("/sales/parse", response_model=SalesSummaryModel)
def sales_parse(req: SalesParseRequest):
    df, warnings = parse_sales_excel(req.path, sheet_name=req.sheet_name)
    builder = SalesFeatureBuilder()
    summary = builder.build_features(df)
    summary["warnings"] = warnings
    return summary


@app.post("/purchase/parse", response_model=PurchaseSummaryModel)
def purchase_parse(req: PurchaseParseRequest):
    df, warnings = parse_purchase_excel(req.path, sheet_name=req.sheet_name)
    builder = PurchaseFeatureBuilder()
    summary = builder.build_features(df)
    summary["warnings"] = warnings
    return summary


@app.post("/agent/sales", response_model=SalesAgentOutputModel)
def sales_agent(summary: SalesSummaryModel):
    agent = SalesAgent()
    output = agent.analyze(summary.dict())
    return output


@app.post("/agent/purchase", response_model=PurchaseAgentOutputModel)
def purchase_agent(summary: PurchaseSummaryModel):
    agent = PurchaseAgent()
    output = agent.analyze(summary.dict())
    return output


@app.post("/agent/decision", response_model=DecisionOutputModel)
def decision_agent(req: DecisionRequest):
    agent = DecisionAgent()
    output = agent.analyze(
        sales_summary=req.sales_summary.dict(),
        purchase_summary=req.purchase_summary.dict(),
        sales_agent_output=req.sales_agent_output.dict(),
        purchase_agent_output=req.purchase_agent_output.dict(),
    )
    return output
