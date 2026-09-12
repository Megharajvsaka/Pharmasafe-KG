"""
graph_repository.py
-------------------
Abstract Base Class interface for biomedical Knowledge Graph queries.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any


class IGraphRepository(ABC):
    """Interface for graph database queries (Neo4j / NetworkX)."""

    @abstractmethod
    def query_interactions_batch(self, candidate_pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
        """Batch query documented DDI relationships between ingredient pairs."""
        pass

    @abstractmethod
    def get_drug_interactions(self, brand_name: str, generics: List[str]) -> Dict[str, Any]:
        """Query all known interactions and metadata for a specific drug's active ingredients."""
        pass

    @abstractmethod
    def get_interaction_subgraph(self, generics_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """Build nodes and edges payload for graph visualization."""
        pass
