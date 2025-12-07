from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - transformers optional
    pipeline = None  # type: ignore


@dataclass
class SummaryResult:
    summary_text: str
    num_inputs: int


class ReviewSummarizer:
    """Summarize unstructured customer reviews via Transformer pipelines."""

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6") -> None:
        self.model_name = model_name
        self._pipeline = None
        if pipeline is not None:
            try:  # Lazy init to avoid heavy startup when unused
                self._pipeline = pipeline("summarization", model=self.model_name)
            except Exception as exc:  # pragma: no cover - dependency/runtime specific
                print(f"[ReviewSummarizer] Failed to init HF pipeline: {exc}")
                self._pipeline = None

    def summarize(self, reviews: Iterable[str], max_chars: int = 512) -> SummaryResult:
        texts = [text.strip() for text in reviews if text and text.strip()]
        if not texts:
            raise ValueError("No review text provided for summarization")
        joined = " \n".join(texts)
        truncated = joined[:max_chars]
        if self._pipeline is not None:
            summary = self._pipeline(truncated, max_length=130, min_length=30, do_sample=False)[0][
                "summary_text"
            ]
        else:
            # Lightweight fallback heuristic: pick top sentences
            chunks = truncated.split(".")
            summary = ". ".join(chunk.strip() for chunk in chunks[:3] if chunk.strip())
        return SummaryResult(summary_text=summary.strip(), num_inputs=len(texts))
