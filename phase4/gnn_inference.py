"""
gnn_inference.py  —  pharmasafe-kg/phase4/gnn_inference.py
-----------------------------------------------------------
Loads the trained GraphSAGE model and provides a predict()
function used by the FastAPI /check endpoint.

This runs on CPU (no GPU needed for inference — only training needs GPU).
The trained weights from Colab are loaded once at API startup.

Usage in FastAPI:
    from phase4.gnn_inference import GNNPredictor
    predictor = GNNPredictor()
    predictor.load()
    prob = predictor.predict("warfarin", "ibuprofen")
"""

import torch
import torch.nn.functional as F
from pathlib import Path

ROOT         = Path(__file__).parent.parent
WEIGHTS_PATH = ROOT / "phase4" / "graphsage_weights.pt"
EMB_PATH     = ROOT / "phase4" / "node_embeddings.pt"


class GNNPredictor:
    """
    Wraps the trained GraphSAGE model for DDI inference.

    Two inference modes:
    1. Fast (embedding lookup): uses pre-computed embeddings from Colab.
       ~1ms per prediction. Works for all nodes seen during training.

    2. Fallback: returns None if either drug not in training vocabulary.
       The API falls back to the Neo4j direct lookup in this case.
    """

    def __init__(self):
        self._loaded      = False
        self._embeddings  = None       # [num_nodes, embed_dim] tensor
        self._node_to_idx = {}         # drug_name → index
        self._meta        = {}         # training metadata

    def load(self) -> bool:
        """
        Loads embeddings from disk. Call once at FastAPI startup.
        Returns True if successful, False if weights not found (training not done yet).
        """
        if not EMB_PATH.exists():
            print(f"⚠️  GNN embeddings not found at {EMB_PATH}")
            print("   Run Phase 4 Colab training first, then copy node_embeddings.pt here.")
            print("   API will use Neo4j direct lookup only (no GNN predictions).")
            return False

        checkpoint = torch.load(EMB_PATH, map_location="cpu")
        self._embeddings  = checkpoint["embeddings"]    # [N, D]
        self._node_to_idx = checkpoint["node_to_idx"]   # {name: idx}
        self._loaded      = True

        print(f"✅ GNN embeddings loaded: {self._embeddings.shape[0]:,} drugs, "
              f"dim={self._embeddings.shape[1]}")
        return True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, drug_a: str, drug_b: str) -> float | None:
        """
        Predicts interaction probability between two generic drug names.

        Returns:
            float: probability 0.0–1.0 (higher = more likely to interact)
            None:  if either drug not in GNN vocabulary
        """
        if not self._loaded:
            return None

        idx_a = self._node_to_idx.get(drug_a.lower().strip())
        idx_b = self._node_to_idx.get(drug_b.lower().strip())

        if idx_a is None or idx_b is None:
            return None

        # Dot product of embeddings → sigmoid → probability
        emb_a = self._embeddings[idx_a]
        emb_b = self._embeddings[idx_b]
        score = torch.dot(emb_a, emb_b).item()
        prob  = torch.sigmoid(torch.tensor(score)).item()
        return round(prob, 4)

    def predict_batch(self, pairs: list[tuple[str, str]]) -> list[float | None]:
        """Predicts interaction probabilities for a batch of drug pairs."""
        return [self.predict(a, b) for a, b in pairs]

    def get_top_interactions(self, drug_name: str, top_k: int = 10) -> list[dict]:
        """
        Returns the top-k most likely interaction partners for a drug.
        Used for exploratory analysis and paper experiments.
        """
        if not self._loaded:
            return []

        idx = self._node_to_idx.get(drug_name.lower().strip())
        if idx is None:
            return []

        emb_query   = self._embeddings[idx]           # [D]
        scores      = torch.mv(self._embeddings, emb_query)  # [N] dot products
        scores[idx] = -float("inf")                   # exclude self

        top_scores, top_indices = torch.topk(scores, k=min(top_k, len(scores)))
        top_probs = torch.sigmoid(top_scores)

        # Reverse lookup: idx → name
        idx_to_name = {v: k for k, v in self._node_to_idx.items()}

        return [
            {
                "drug":        idx_to_name.get(top_indices[i].item(), "unknown"),
                "probability": round(top_probs[i].item(), 4),
            }
            for i in range(len(top_indices))
        ]


# Singleton instance — loaded once at API startup
_predictor: GNNPredictor | None = None


def get_predictor() -> GNNPredictor:
    """Returns the shared GNNPredictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = GNNPredictor()
        _predictor.load()
    return _predictor
