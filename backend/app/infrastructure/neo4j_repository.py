"""
neo4j_repository.py
-------------------
Neo4j repository implementation of IGraphRepository.
All queries parameterized to prevent Cypher injection.
"""

from typing import List, Tuple, Dict, Any
from backend.app.core.neo4j import get_driver
from backend.app.domain.interfaces.graph_repository import IGraphRepository


class Neo4jGraphRepository(IGraphRepository):
    """Encapsulates all Cypher queries executed against Neo4j AuraDB."""

    def query_interactions_batch(self, candidate_pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
        driver = get_driver()
        CYPHER = """
        UNWIND $pairs AS p
        MATCH (a:Ingredient {name: p[0]})-[r:INTERACTS_WITH]-(b:Ingredient {name: p[1]})
        RETURN
            a.name      AS ingredient_a,
            b.name      AS ingredient_b,
            r.severity  AS severity,
            r.mechanism AS mechanism
        """
        raw_pairs = [[p[0], p[1]] for p in candidate_pairs]
        with driver.session() as session:
            results = session.run(CYPHER, pairs=raw_pairs)

            grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
            for row in results:
                ing_a = str(row["ingredient_a"])
                ing_b = str(row["ingredient_b"])
                key = (min(ing_a, ing_b), max(ing_a, ing_b))
                if key not in grouped:
                    grouped[key] = []
                grouped[key].append({
                    "ingredient_a": ing_a,
                    "ingredient_b": ing_b,
                    "severity": str(row["severity"] or "MODERATE").upper(),
                    "mechanism": str(row["mechanism"] or "")[:500],
                })
            return grouped

    def get_drug_interactions(self, brand_name: str, generics: List[str]) -> Dict[str, Any]:
        driver = get_driver()
        all_interactions = []
        with driver.session() as session:
            for generic in generics:
                CYPHER = """
                MATCH (i:Ingredient {name: $name})-[r:INTERACTS_WITH]-(other:Ingredient)
                RETURN
                    i.name           AS source,
                    other.name       AS target,
                    r.severity       AS severity,
                    r.mechanism      AS mechanism
                ORDER BY
                    CASE r.severity
                        WHEN 'MAJOR'    THEN 0
                        WHEN 'MODERATE' THEN 1
                        ELSE 2
                    END
                LIMIT 20
                """
                results = list(session.run(CYPHER, name=generic))
                for row in results:
                    all_interactions.append({
                        "source_generic": row["source"],
                        "target_generic": row["target"],
                        "severity": row["severity"],
                        "mechanism": str(row["mechanism"] or "")[:300],
                    })

        major = [i for i in all_interactions if i["severity"] == "MAJOR"]
        moderate = [i for i in all_interactions if i["severity"] == "MODERATE"]
        minor = [i for i in all_interactions if i["severity"] == "MINOR"]

        return {
            "brand_name": brand_name,
            "generics": generics,
            "total_known_ddis": len(all_interactions),
            "major_count": len(major),
            "moderate_count": len(moderate),
            "minor_count": len(minor),
            "interactions": all_interactions,
        }

    def get_interaction_subgraph(self, generics_map: Dict[str, List[str]]) -> Dict[str, Any]:
        driver = get_driver()
        nodes = {}
        edges = []
        all_generics = set()

        for brand, generics in generics_map.items():
            nodes[brand] = {
                "id": brand,
                "label": brand,
                "type": "Drug",
                "color": "#4A90D9",
                "size": 20,
            }
            for g in generics:
                all_generics.add(g)
                nodes[g] = {
                    "id": g,
                    "label": g.title(),
                    "type": "Ingredient",
                    "color": "#27AE60",
                    "size": 15,
                }
                edges.append({
                    "from": brand,
                    "to": g,
                    "label": "CONTAINS",
                    "color": "#95A5A6",
                    "dashes": False,
                    "width": 1,
                })

        generic_list = list(all_generics)
        with driver.session() as session:
            if len(generic_list) >= 2:
                CYPHER = """
                UNWIND $drugs AS d1
                UNWIND $drugs AS d2
                WITH d1, d2 WHERE d1 < d2
                MATCH (a:Ingredient {name: d1})-[r:INTERACTS_WITH]-(b:Ingredient {name: d2})
                RETURN a.name AS a, b.name AS b, r.severity AS sev, r.mechanism AS mech
                """
                results = list(session.run(CYPHER, drugs=generic_list))
                for row in results:
                    color = {"MAJOR": "#E74C3C", "MODERATE": "#F39C12", "MINOR": "#27AE60"}.get(row["sev"], "#95A5A6")
                    edges.append({
                        "from": row["a"],
                        "to": row["b"],
                        "label": row["sev"],
                        "color": color,
                        "dashes": False,
                        "width": 3 if row["sev"] == "MAJOR" else 2,
                        "title": str(row["mech"] or "")[:200],
                        "severity": row["sev"],
                    })

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
        }
