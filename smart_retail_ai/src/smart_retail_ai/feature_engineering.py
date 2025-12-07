from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd

from .config import DEFAULT_CONFIG, RetailConfig


@dataclass
class FeatureArtifacts:
    product_mapping: dict[int, int]
    user_mapping: dict[int, int]
    inverse_product_mapping: dict[int, int]
    inverse_user_mapping: dict[int, int]


def build_demand_timeseries(
    transactions: pd.DataFrame,
    config: RetailConfig | None = None,
) -> pd.DataFrame:
    """Aggregate daily revenue per product."""

    _ = config or DEFAULT_CONFIG
    frame = transactions.copy()
    frame["date"] = frame["timestamp"].dt.floor("D")
    daily = (
        frame.groupby(["date", "product_id"], as_index=False)["revenue"]
        .sum()
        .sort_values("date")
    )
    pivot = daily.pivot(index="date", columns="product_id", values="revenue").fillna(0.0)
    return pivot


def sliding_window(
    series: pd.Series,
    lookback: int,
    horizon: int,
) -> Tuple[np.ndarray, np.ndarray]:
    values = series.to_numpy(dtype=np.float32)
    if len(values) <= lookback + horizon:
        raise ValueError("Time series is shorter than lookback + horizon window")
    X, y = [], []
    for idx in range(lookback, len(values) - horizon + 1):
        X.append(values[idx - lookback : idx])
        y.append(values[idx : idx + horizon])
    return np.stack(X), np.stack(y)


def build_interaction_matrix(
    transactions: pd.DataFrame,
    min_rating: float = 1.0,
) -> Tuple[np.ndarray, FeatureArtifacts]:
    frame = transactions.copy()
    frame["rating"] = frame.groupby(["user_id", "product_id"])["quantity"].transform("sum")
    frame = frame[["user_id", "product_id", "rating"]].drop_duplicates()
    frame["rating"] = frame["rating"].clip(lower=min_rating)

    users = sorted(frame["user_id"].unique())
    products = sorted(frame["product_id"].unique())
    user_map = {uid: idx for idx, uid in enumerate(users)}
    prod_map = {pid: idx for idx, pid in enumerate(products)}
    inv_user = {idx: uid for uid, idx in user_map.items()}
    inv_prod = {idx: pid for pid, idx in prod_map.items()}

    matrix = np.zeros((len(users), len(products)), dtype=np.float32)
    for row in frame.itertuples():
        matrix[user_map[row.user_id], prod_map[row.product_id]] = float(row.rating)

    return matrix, FeatureArtifacts(prod_map, user_map, inv_prod, inv_user)


def build_review_corpus(reviews: pd.DataFrame) -> list[str]:
    return [str(text) for text in reviews["review_text"].fillna("") if text]
