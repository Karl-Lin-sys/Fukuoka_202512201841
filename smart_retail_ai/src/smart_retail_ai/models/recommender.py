from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

from ..config import DEFAULT_CONFIG, RetailConfig
from ..feature_engineering import FeatureArtifacts, build_interaction_matrix


@dataclass
class Recommendation:
    product_id: int
    score: float


class MatrixFactorizationRecommender:
    """Lightweight recommender using Alternating Least Squares on implicit ratings."""

    def __init__(self, config: RetailConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.user_factors: np.ndarray | None = None
        self.item_factors: np.ndarray | None = None
        self.artifacts: FeatureArtifacts | None = None

    def fit(self, transactions_frame) -> Path:
        matrix, artifacts = build_interaction_matrix(transactions_frame)
        self.artifacts = artifacts
        num_users, num_items = matrix.shape
        components = min(self.config.recommender_components, num_users, num_items)
        user_factors = np.random.normal(0, 0.1, size=(num_users, components))
        item_factors = np.random.normal(0, 0.1, size=(num_items, components))

        reg = 0.1
        for iteration in range(self.config.recommender_iter):
            # Update user factors
            for u in range(num_users):
                item_idx = matrix[u] > 0
                if not np.any(item_idx):
                    continue
                V = item_factors[item_idx]
                ratings = matrix[u, item_idx]
                A = V.T @ V + reg * np.eye(components)
                b = V.T @ ratings
                user_factors[u] = np.linalg.solve(A, b)
            # Update item factors
            for i in range(num_items):
                user_idx = matrix[:, i] > 0
                if not np.any(user_idx):
                    continue
                U = user_factors[user_idx]
                ratings = matrix[user_idx, i]
                A = U.T @ U + reg * np.eye(components)
                b = U.T @ ratings
                item_factors[i] = np.linalg.solve(A, b)
            if (iteration + 1) % 50 == 0:
                recon = user_factors @ item_factors.T
                mask = matrix > 0
                rmse = np.sqrt(np.mean((recon[mask] - matrix[mask]) ** 2))
                print(f"[ALS] iter={iteration+1} rmse={rmse:.4f}")

        self.user_factors = user_factors
        self.item_factors = item_factors
        artifact_path = self.config.artifact_dir / "recommender_weights.npz"
        np.savez(
            artifact_path,
            user_factors=user_factors,
            item_factors=item_factors,
            product_mapping=self.artifacts.product_mapping,
            user_mapping=self.artifacts.user_mapping,
        )
        return artifact_path

    def recommend(self, user_id: int, top_k: int = 5) -> List[Recommendation]:
        if self.user_factors is None or self.item_factors is None or self.artifacts is None:
            raise RuntimeError("Model not trained")
        if user_id not in self.artifacts.user_mapping:
            raise ValueError(f"User {user_id} unknown")
        u_idx = self.artifacts.user_mapping[user_id]
        scores = self.item_factors @ self.user_factors[u_idx]
        ranked = np.argsort(scores)[::-1][:top_k]
        recommendations = []
        for idx in ranked:
            product_id = self.artifacts.inverse_product_mapping[idx]
            recommendations.append(Recommendation(product_id=product_id, score=float(scores[idx])))
        return recommendations
