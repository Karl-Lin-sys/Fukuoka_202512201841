from __future__ import annotations

import argparse
import logging

import numpy as np

from .config import RetailConfig
from .data_loader import RetailDataLoader
from .feature_engineering import build_review_corpus
from .models import DemandForecaster, MatrixFactorizationRecommender, ReviewSummarizer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def _configure(args: argparse.Namespace) -> RetailConfig:
    config = RetailConfig()
    if args.lookback:
        config.sequence_lookback = args.lookback
    if args.horizon:
        config.forecast_horizon = args.horizon
    if args.epochs:
        config.forecast_epochs = args.epochs
    if args.batch_size:
        config.forecast_batch_size = args.batch_size
    if args.components:
        config.recommender_components = args.components
    return config


def run_pipeline(args: argparse.Namespace | None = None) -> None:
    parser = argparse.ArgumentParser(description="Smart Retail AI orchestration")
    parser.add_argument("--product-id", type=int, default=None, help="Product ID to forecast")
    parser.add_argument("--epochs", type=int, default=None, help="Override training epochs")
    parser.add_argument("--lookback", type=int, default=None, help="Sequence length for LSTM")
    parser.add_argument("--horizon", type=int, default=None, help="Forecast horizon")
    parser.add_argument("--batch-size", type=int, default=None, help="Forecast batch size")
    parser.add_argument("--components", type=int, default=None, help="Latent factors for ALS recommender")
    parser.add_argument("--top-k", type=int, default=5, help="Number of recommendations to preview")
    parser.add_argument(
        "--max-reviews", type=int, default=50, help="How many reviews to summarize for sample artifact"
    )
    if args is None:
        parsed = parser.parse_args()
    else:
        parsed = args
    config = _configure(parsed)

    loader = RetailDataLoader(config)
    loader.ensure_data()
    tx = loader.load_transactions()
    reviews = loader.load_reviews()

    # --------------------- Demand Forecasting ---------------------
    if parsed.product_id is not None:
        product_id = parsed.product_id
    else:
        product_id = int(tx.groupby("product_id")["revenue"].sum().idxmax())
    logger.info("Training LSTM forecaster for product_id=%s", product_id)
    forecaster = DemandForecaster(config)
    forecast_artifact = forecaster.fit(tx, product_id=product_id, epochs=config.forecast_epochs)
    last_values = tx.loc[tx["product_id"] == product_id].sort_values("timestamp")["revenue"].tail(
        config.sequence_lookback
    )
    preview = forecaster.forecast(last_values, horizon=config.forecast_horizon)
    logger.info("Sample forecast: %s", np.round(preview, 2).tolist())

    # --------------------- Recommendations ------------------------
    logger.info("Training matrix factorization recommender")
    recommender = MatrixFactorizationRecommender(config)
    rec_artifact = recommender.fit(tx)
    sample_user = int(tx["user_id"].mode()[0])
    recs = recommender.recommend(sample_user, top_k=parsed.top_k)
    logger.info("Top-%s recommendations for user %s: %s", parsed.top_k, sample_user, recs)

    # --------------------- NLP Summaries --------------------------
    logger.info("Summarizing %s customer reviews", parsed.max_reviews)
    summarizer = ReviewSummarizer()
    corpus = build_review_corpus(reviews.head(parsed.max_reviews))
    summary = summarizer.summarize(corpus)
    summary_path = config.artifact_dir / "review_summary.txt"
    summary_path.write_text(summary.summary_text, encoding="utf-8")
    logger.info("Saved review summary to %s", summary_path)

    logger.info("Artifacts saved: %s, %s, %s", forecast_artifact, rec_artifact, summary_path)


if __name__ == "__main__":
    run_pipeline()
