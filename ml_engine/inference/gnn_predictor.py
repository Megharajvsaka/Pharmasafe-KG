"""
gnn_predictor.py
----------------
GraphSAGE and GNN DDI prediction implementation.
Implements the IDDIPredictor interface.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import torch

from backend.app.domain.interfaces.predictor import IDDIPredictor

# Resolve root path dynamically
ROOT_DIR = Path(__file__).resolve().parents[2]
EMB_PATH_PRIMARY = ROOT_DIR / "ml_engine" / "artifacts" / "node_embeddings.pt"
EMB_PATH_FALLBACK = ROOT_DIR / "phase4" / "node_embeddings.pt"


class GNNPredictor(IDDIPredictor):
    """
    GraphSAGE GNN link predictor for inferring unseen drug-drug interactions.
    """

    def __init__(self, emb_path: Optional[Path] = None):
        self._loaded = False
        self._embeddings = None       # [num_nodes, embed_dim] tensor
        self._node_to_idx: Dict[str, int] = {}  # drug_name -> index
        self._emb_path = emb_path or (EMB_PATH_PRIMARY if EMB_PATH_PRIMARY.exists() else EMB_PATH_FALLBACK)

    def load(self) -> bool:
        """Loads embeddings from persistent .pt weights."""
        if not self._emb_path.exists():
            print(f"[WARNING] GNN embeddings not found at {self._emb_path}")
            return False

        try:
            checkpoint = torch.load(self._emb_path, map_location="cpu")
            self._embeddings = checkpoint["embeddings"]
            self._node_to_idx = checkpoint["node_to_idx"]
            self._loaded = True
            print(f"[SUCCESS] GNN embeddings loaded: {self._embeddings.shape[0]:,} drugs (dim={self._embeddings.shape[1]})")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load GNN embeddings: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, drug_a: str, drug_b: str) -> Optional[float]:
        """Predicts interaction probability between two generic drug names."""
        if not self._loaded or self._embeddings is None:
            return None

        idx_a = self._node_to_idx.get(drug_a.lower().strip())
        idx_b = self._node_to_idx.get(drug_b.lower().strip())

        if idx_a is None or idx_b is None:
            return None

        emb_a = self._embeddings[idx_a]
        emb_b = self._embeddings[idx_b]
        score = torch.dot(emb_a, emb_b).item()
        prob = torch.sigmoid(torch.tensor(score)).item()
        return round(prob, 4)

    def predict_batch(self, pairs: List[Tuple[str, str]]) -> List[Optional[float]]:
        return [self.predict(a, b) for a, b in pairs]

    def get_top_interactions(self, drug_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self._loaded or self._embeddings is None:
            return []

        idx = self._node_to_idx.get(drug_name.lower().strip())
        if idx is None:
            return []

        emb_query = self._embeddings[idx]
        scores = torch.mv(self._embeddings, emb_query)
        scores[idx] = -float("inf")

        top_scores, top_indices = torch.topk(scores, k=min(top_k, len(scores)))
        top_probs = torch.sigmoid(top_scores)

        idx_to_name = {v: k for k, v in self._node_to_idx.items()}

        return [
            {
                "drug": idx_to_name.get(top_indices[i].item(), "unknown"),
                "probability": round(top_probs[i].item(), 4),
            }
            for i in range(len(top_indices))
        ]


_predictor_instance: Optional[GNNPredictor] = None


def get_predictor() -> GNNPredictor:
    """Singleton getter for shared GNNPredictor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = GNNPredictor()
        _predictor_instance.load()
    return _predictor_instance
