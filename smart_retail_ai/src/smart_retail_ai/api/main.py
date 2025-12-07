from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..config import RetailConfig
from ..data_loader import RetailDataLoader
from ..feature_engineering import build_review_corpus
from ..models import DemandForecaster, MatrixFactorizationRecommender, ReviewSummarizer

app = FastAPI(title="Smart Retail AI", description="PropTech-ready AI microservices", version="0.1.0")

_BASE_CONFIG = RetailConfig()
_loader = RetailDataLoader(_BASE_CONFIG)


class ForecastRequest(BaseModel):
    history: List[float] = Field(..., min_length=3, description="Recent revenue history for the product")
    horizon: int = Field(7, ge=1, le=30)
    product_id: Optional[int] = Field(None, description="Product to forecast; defaults to top seller")
    epochs: Optional[int] = Field(None, ge=1, le=25)


class ForecastResponse(BaseModel):
    product_id: int
    horizon: int
    predictions: List[float]
    artifact_path: str


class RecommendRequest(BaseModel):
    user_id: int
    top_k: int = Field(5, ge=1, le=20)


class RecommendationItem(BaseModel):
    product_id: int
    score: float


class RecommendResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
    artifact_path: str


class SummarizeRequest(BaseModel):
    reviews: Optional[List[str]] = None
    max_chars: int = Field(512, ge=64, le=2048)


class SummarizeResponse(BaseModel):
    summary: str
    used_reviews: int


class HealthResponse(BaseModel):
    transactions: int
    catalog: int
    reviews: int
    config: dict


@app.on_event("startup")
def _startup() -> None:
    _loader.ensure_data()


def _clone_config(**overrides) -> RetailConfig:
    cfg = replace(_BASE_CONFIG)
    for key, value in overrides.items():
        if value is not None and hasattr(cfg, key):
            setattr(cfg, key, value)
    return cfg


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    tx = _loader.load_transactions()
    catalog = _loader.load_catalog()
    reviews = _loader.load_reviews()
    return HealthResponse(
        transactions=len(tx),
        catalog=len(catalog),
        reviews=len(reviews),
        config=_BASE_CONFIG.to_dict(),
    )


@app.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest) -> ForecastResponse:
    tx = _loader.load_transactions()
    if request.product_id is not None and request.product_id not in tx["product_id"].unique():
        raise HTTPException(status_code=404, detail="Unknown product_id")
    product_id = request.product_id or int(tx.groupby("product_id")["revenue"].sum().idxmax())

    cfg = _clone_config(forecast_horizon=request.horizon, forecast_epochs=request.epochs)
    forecaster = DemandForecaster(cfg)
    artifact_path = forecaster.fit(tx, product_id=product_id, epochs=cfg.forecast_epochs)

    history = request.history
    required = cfg.sequence_lookback
    if len(history) < required:
        fallback = (
            tx.loc[tx["product_id"] == product_id]
            .sort_values("timestamp")
            ["revenue"]
            .tail(required)
            .tolist()
        )
        history = fallback
    preds = forecaster.forecast(history[-required:], horizon=cfg.forecast_horizon)
    return ForecastResponse(
        product_id=product_id,
        horizon=cfg.forecast_horizon,
        predictions=np.round(preds, 2).tolist(),
        artifact_path=str(artifact_path),
    )


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    tx = _loader.load_transactions()
    if request.user_id not in tx["user_id"].unique():
        raise HTTPException(status_code=404, detail="Unknown user_id")
    cfg = _clone_config()
    recommender = MatrixFactorizationRecommender(cfg)
    artifact_path = recommender.fit(tx)
    recs = recommender.recommend(request.user_id, top_k=request.top_k)
    payload = [RecommendationItem(product_id=r.product_id, score=round(r.score, 4)) for r in recs]
    return RecommendResponse(user_id=request.user_id, recommendations=payload, artifact_path=str(artifact_path))


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    reviews_df = _loader.load_reviews()
    texts = request.reviews or build_review_corpus(reviews_df.head(request.max_chars))
    summarizer = ReviewSummarizer()
    summary = summarizer.summarize(texts, max_chars=request.max_chars)
    return SummarizeResponse(summary=summary.summary_text, used_reviews=summary.num_inputs)
