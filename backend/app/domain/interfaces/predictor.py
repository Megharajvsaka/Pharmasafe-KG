"""
predictor.py
------------
Abstract Base Class interface for DDI predictors.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any


class IDDIPredictor(ABC):
    """Interface for machine learning or statistical DDI prediction models."""

    @abstractmethod
    def load(self) -> bool:
        """Load model weights/embeddings from persistent storage."""
        pass

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Return True if model is initialized and ready for inference."""
        pass

    @abstractmethod
    def predict(self, drug_a: str, drug_b: str) -> Optional[float]:
        """Compute interaction probability score between two generic drugs."""
        pass

    @abstractmethod
    def predict_batch(self, pairs: List[Tuple[str, str]]) -> List[Optional[float]]:
        """Compute interaction scores for a batch of drug pairs."""
        pass

    @abstractmethod
    def get_top_interactions(self, drug_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top-K predicted interaction partners for a given drug."""
        pass
