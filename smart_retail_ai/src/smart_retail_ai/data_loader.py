from __future__ import annotations

import json
from dataclasses import asdict
from typing import Tuple

import numpy as np
import pandas as pd

from .config import DEFAULT_CONFIG, RetailConfig


class RetailDataLoader:
    """Generate and load synthetic-yet-realistic retail datasets."""

    def __init__(self, config: RetailConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.rng = np.random.default_rng(self.config.random_seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def ensure_data(self) -> None:
        """Create datasets on first run so the project is self-contained."""
        tx_path = self.config.data_dir / "transactions.parquet"
        cat_path = self.config.data_dir / "catalog.parquet"
        review_path = self.config.data_dir / "reviews.jsonl"

        if not tx_path.exists():
            transactions = self._generate_transactions(num_users=200, num_products=40, days=120)
            transactions.to_parquet(tx_path, index=False)
        if not cat_path.exists():
            catalog = self._generate_catalog(num_products=40)
            catalog.to_parquet(cat_path, index=False)
        if not review_path.exists():
            reviews = self._generate_reviews(num_users=120, num_products=40, samples=500)
            with review_path.open("w", encoding="utf-8") as f:
                for row in reviews:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def load_transactions(self) -> pd.DataFrame:
        self.ensure_data()
        tx_path = self.config.data_dir / "transactions.parquet"
        frame = pd.read_parquet(tx_path)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame

    def load_catalog(self) -> pd.DataFrame:
        self.ensure_data()
        cat_path = self.config.data_dir / "catalog.parquet"
        return pd.read_parquet(cat_path)

    def load_reviews(self) -> pd.DataFrame:
        self.ensure_data()
        review_path = self.config.data_dir / "reviews.jsonl"
        rows = []
        with review_path.open("r", encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Synthetic data generation helpers
    # ------------------------------------------------------------------
    def _generate_catalog(self, num_products: int) -> pd.DataFrame:
        categories = ["Smart Home", "Wellness", "Mobility", "Entertainment"]
        product_ids = np.arange(1, num_products + 1)
        catalog = pd.DataFrame(
            {
                "product_id": product_ids,
                "category": self.rng.choice(categories, size=num_products),
                "base_price": self.rng.uniform(50, 600, size=num_products).round(2),
            }
        )
        catalog["cost_of_goods"] = (catalog["base_price"] * self.rng.uniform(0.4, 0.7, size=num_products)).round(2)
        catalog["msrp"] = (catalog["base_price"] * self.rng.uniform(1.05, 1.35, size=num_products)).round(2)
        return catalog

    def _generate_transactions(self, num_users: int, num_products: int, days: int) -> pd.DataFrame:
        start = pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=days)
        timestamps = pd.date_range(start=start, periods=days, freq="D")
        records = []
        for ts in timestamps:
            daily_users = self.rng.poisson(lam=num_users // 4)
            sampled_users = self.rng.choice(np.arange(1, num_users + 1), size=max(1, daily_users), replace=False)
            for user_id in sampled_users:
                basket_size = self.rng.integers(1, 4)
                product_choices = self.rng.choice(np.arange(1, num_products + 1), size=basket_size, replace=False)
                for pid in product_choices:
                    qty = int(self.rng.integers(1, 5))
                    price = float(self.rng.uniform(60, 800))
                    records.append(
                        {
                            "transaction_id": f"TX-{ts.strftime('%Y%m%d')}-{user_id}-{pid}",
                            "user_id": int(user_id),
                            "product_id": int(pid),
                            "quantity": qty,
                            "unit_price": round(price, 2),
                            "timestamp": ts + pd.to_timedelta(int(self.rng.integers(0, 24)), unit="h"),
                        }
                    )
        df = pd.DataFrame.from_records(records)
        df["revenue"] = df["quantity"] * df["unit_price"]
        return df

    def _generate_reviews(self, num_users: int, num_products: int, samples: int) -> list[dict]:
        sentiment_phrases = [
            "great battery life and smart automation",
            "setup was confusing but support helped",
            "sleek design though premium priced",
            "voice assistant integration is seamless",
            "firmware updates broke a few routines",
            "kids love the gamified wellness challenges",
            "predictive maintenance alerts saved time",
        ]
        reviews = []
        for idx in range(samples):
            reviews.append(
                {
                    "review_id": f"RV-{idx:05d}",
                    "user_id": int(self.rng.integers(1, num_users + 1)),
                    "product_id": int(self.rng.integers(1, num_products + 1)),
                    "rating": int(self.rng.integers(1, 6)),
                    "review_text": str(self.rng.choice(sentiment_phrases)),
                }
            )
        return reviews


def summarize_dataset_shapes(config: RetailConfig | None = None) -> Tuple[int, int, int]:
    loader = RetailDataLoader(config)
    tx = loader.load_transactions()
    catalog = loader.load_catalog()
    reviews = loader.load_reviews()
    return len(tx), len(catalog), len(reviews)
