"""
ddi_service.py
--------------
Polypharmacy DDI Analysis service.
Coordinates IGraphRepository and IDDIPredictor (SOLID DIP / OCP).
"""

from typing import Dict, List, Tuple, Any, Optional
from backend.app.domain.interfaces.graph_repository import IGraphRepository
from backend.app.domain.interfaces.predictor import IDDIPredictor


class DDIService:
    def __init__(self, graph_repo: IGraphRepository, predictor: IDDIPredictor):
        self._graph_repo = graph_repo
        self._predictor = predictor

    def check_polypharmacy(self, generics_map: Dict[str, List[str]]) -> Dict[str, Any]:
        brand_names = list(generics_map.keys())
        interactions = []
        safe_pairs = []
        pairs_checked = 0

        brand_pairs = [
            (brand_names[i], brand_names[j])
            for i in range(len(brand_names))
            for j in range(i + 1, len(brand_names))
        ]

        all_candidate_pairs: set[Tuple[str, str]] = set()
        brand_to_generic_pairs: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}

        for brand_a, brand_b in brand_pairs:
            generics_a = generics_map.get(brand_a, [])
            generics_b = generics_map.get(brand_b, [])
            pair_list = []

            for g_a in generics_a:
                for g_b in generics_b:
                    if g_a == g_b:
                        continue
                    pair_key = (min(g_a, g_b), max(g_a, g_b))
                    pair_list.append((g_a, g_b))
                    all_candidate_pairs.add(pair_key)
                    pairs_checked += 1

            brand_to_generic_pairs[(brand_a, brand_b)] = pair_list

        kg_results_by_pair = {}
        if all_candidate_pairs:
            kg_results_by_pair = self._graph_repo.query_interactions_batch(list(all_candidate_pairs))

        for brand_a, brand_b in brand_pairs:
            pair_list = brand_to_generic_pairs.get((brand_a, brand_b), [])
            found_for_pair = []
            predicted_for_pair = []

            for g_a, g_b in pair_list:
                pair_key = (min(g_a, g_b), max(g_a, g_b))
                kg_hits = kg_results_by_pair.get(pair_key, [])

                if kg_hits:
                    for hit in kg_hits:
                        found_for_pair.append({
                            "brand_a": brand_a,
                            "brand_b": brand_b,
                            "ingredient_a": hit["ingredient_a"],
                            "ingredient_b": hit["ingredient_b"],
                            "severity": hit["severity"],
                            "mechanism": hit["mechanism"],
                            "status": "documented",
                            "source": "knowledge_graph",
                            "confidence": None,
                            "evidence": [hit],
                            "explanation": self._build_explanation(brand_a, hit["ingredient_a"], brand_b, hit["ingredient_b"], hit["severity"], hit["mechanism"]),
                        })
                elif self._predictor and self._predictor.is_loaded:
                    prob = self._predictor.predict(g_a, g_b)
                    if prob is not None and prob >= 0.70:
                        predicted_for_pair.append({
                            "brand_a": brand_a,
                            "brand_b": brand_b,
                            "ingredient_a": g_a,
                            "ingredient_b": g_b,
                            "severity": "UNKNOWN",
                            "mechanism": f"Predicted potential interaction via GraphSAGE link prediction (confidence: {prob*100:.1f}%). Clinical severity unassessed.",
                            "status": "predicted",
                            "source": "gnn_predicted",
                            "confidence": prob,
                            "evidence": [{"model": "GraphSAGE", "probability": prob, "threshold": 0.70, "evidence_type": "inductive_link_prediction"}],
                            "explanation": self._build_predicted_explanation(brand_a, g_a, brand_b, g_b, prob),
                        })

            if found_for_pair:
                found_for_pair.sort(key=lambda x: self._severity_rank(x["severity"]))
                primary = dict(found_for_pair[0])
                primary["evidence"] = [item["evidence"][0] for item in found_for_pair if item.get("evidence")]
                interactions.append(primary)
            elif predicted_for_pair:
                predicted_for_pair.sort(key=lambda x: x["confidence"] or 0, reverse=True)
                interactions.append(predicted_for_pair[0])
            else:
                safe_pairs.append({
                    "brand_a": brand_a,
                    "brand_b": brand_b,
                    "note": "No documented interaction in current knowledge base. (Note: Lack of documented evidence does not guarantee clinical safety.)",
                    "status": "not_documented",
                })

        interactions.sort(key=lambda x: (self._status_rank(x.get("status")), self._severity_rank(x["severity"])))

        return {
            "total_drugs": len(brand_names),
            "brand_names": brand_names,
            "pairs_checked": pairs_checked,
            "interactions_found": len(interactions),
            "safe_pairs": len(safe_pairs),
            "interactions": interactions,
            "safe_pairs_detail": safe_pairs,
            "summary": self._build_summary(interactions),
        }

    def _build_explanation(self, brand_a, ing_a, brand_b, ing_b, severity, mechanism) -> str:
        sev_text = {
            "MAJOR": "⚠️ MAJOR RISK",
            "MODERATE": "⚠️ MODERATE RISK",
            "MINOR": "ℹ️ MINOR INTERACTION",
            "UNKNOWN": "ℹ️ AI PREDICTED (SEVERITY UNKNOWN)",
            "UNASSESSED": "ℹ️ AI PREDICTED (SEVERITY UNASSESSED)",
        }.get(severity, "INTERACTION DETECTED")

        mech = mechanism.strip()
        if len(mech) > 300:
            mech = mech[:297] + "..."

        return f"{sev_text}: {brand_a} and {brand_b} interact.\n\n{brand_a} contains {ing_a.title()}. {brand_b} contains {ing_b.title()}.\n\nMechanism: {mech}"

    def _build_predicted_explanation(self, brand_a, ing_a, brand_b, ing_b, probability) -> str:
        pct = round(probability * 100, 1)
        return (
            f"🤖 AI PREDICTED INTERACTION ({pct}% confidence): {brand_a} and {brand_b}.\n\n"
            f"{brand_a} contains {ing_a.title()}. {brand_b} contains {ing_b.title()}.\n\n"
            f"Note: This interaction is not yet indexed in the primary Knowledge Graph, "
            f"but was inferred by the Graph Neural Network (GraphSAGE link prediction). Clinical severity is unassessed."
        )

    def _severity_rank(self, sev: str) -> int:
        return {"MAJOR": 0, "MODERATE": 1, "MINOR": 2, "UNKNOWN": 3, "UNASSESSED": 3}.get(sev, 4)

    def _status_rank(self, status: str | None) -> int:
        return {"documented": 0, "predicted": 1}.get(status or "", 2)

    def _build_summary(self, interactions: list) -> str:
        if not interactions:
            return "No documented drug interactions detected in knowledge base."
        doc_major = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MAJOR")
        doc_moderate = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MODERATE")
        doc_minor = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MINOR")
        predicted = sum(1 for i in interactions if i.get("status") == "predicted")

        parts = []
        if doc_major: parts.append(f"{doc_major} MAJOR (Documented)")
        if doc_moderate: parts.append(f"{doc_moderate} MODERATE (Documented)")
        if doc_minor: parts.append(f"{doc_minor} MINOR (Documented)")
        if predicted: parts.append(f"{predicted} AI PREDICTED")

        return f"{len(interactions)} interaction(s) found: {', '.join(parts)}."
