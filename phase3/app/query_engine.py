"""
query_engine.py
---------------
All Neo4j Cypher queries for the PharmaSafe-KG backend.

Three public functions used by the API routes:
    check_interactions(generics_map)  — polypharmacy DDI engine
    get_drug_info(brand_name)         — full drug detail page
    search_autocomplete(query)        — brand name autocomplete
"""

from phase3.app.database import get_driver
from phase4.gnn_inference import get_predictor


# ─────────────────────────────────────────────────────────────────────────────
# POLYPHARMACY ENGINE  —  POST /check
# ─────────────────────────────────────────────────────────────────────────────
def check_interactions(generics_map: dict[str, list[str]]) -> dict:
    """
    Core polypharmacy DDI detection engine.

    Args:
        generics_map: {brand_name: [generic1, generic2, ...], ...}

    Algorithm:
        1. Build candidate (g_a, g_b) pairs across all brand combinations.
        2. Run a single batched Cypher UNWIND query against Neo4j to retrieve all documented interactions.
        3. For generic pairs without KG evidence, invoke GNN inference fallback.
        4. Aggregate, rank by severity, and preserve multi-evidence details.
    """
    driver = get_driver()
    predictor = get_predictor()

    brand_names   = list(generics_map.keys())
    interactions  = []
    safe_pairs    = []
    pairs_checked = 0

    # Generate all unique brand pairs
    brand_pairs = [
        (brand_names[i], brand_names[j])
        for i in range(len(brand_names))
        for j in range(i + 1, len(brand_names))
    ]

    # Collect all unique generic pairs to query in batch
    all_candidate_pairs: set[tuple[str, str]] = set()
    brand_to_generic_pairs: dict[tuple[str, str], list[tuple[str, str]]] = {}

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

    # Execute single batched Cypher query for all candidate pairs
    kg_results_by_pair: dict[tuple[str, str], list[dict]] = {}
    if all_candidate_pairs:
        with driver.session() as session:
            kg_results_by_pair = _query_interactions_batch(session, list(all_candidate_pairs))

    # Evaluate interactions and fallback per brand pair
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
                        "brand_a":      brand_a,
                        "brand_b":      brand_b,
                        "ingredient_a": hit["ingredient_a"],
                        "ingredient_b": hit["ingredient_b"],
                        "severity":     hit["severity"],
                        "mechanism":    hit["mechanism"],
                        "status":       "documented",
                        "source":       "knowledge_graph",
                        "confidence":   None,
                        "evidence":     [hit],
                        "explanation":  _build_explanation(
                            brand_a, hit["ingredient_a"],
                            brand_b, hit["ingredient_b"],
                            hit["severity"], hit["mechanism"]
                        ),
                    })
            elif predictor and predictor.is_loaded:
                # GNN Link Prediction Fallback for KG misses
                prob = predictor.predict(g_a, g_b)
                if prob is not None and prob >= 0.70:
                    predicted_for_pair.append({
                        "brand_a":      brand_a,
                        "brand_b":      brand_b,
                        "ingredient_a": g_a,
                        "ingredient_b": g_b,
                        "severity":     "MODERATE",
                        "mechanism":    f"Predicted potential interaction via GraphSAGE link prediction (confidence: {prob*100:.1f}%).",
                        "status":       "predicted",
                        "source":       "gnn_predicted",
                        "confidence":   prob,
                        "evidence":     [{"model": "GraphSAGE", "probability": prob, "threshold": 0.70}],
                        "explanation":  _build_predicted_explanation(brand_a, g_a, brand_b, g_b, prob),
                    })

        if found_for_pair:
            # Sort KG hits by severity and keep primary while preserving all evidence
            found_for_pair.sort(key=lambda x: _severity_rank(x["severity"]))
            primary = dict(found_for_pair[0])
            primary["evidence"] = [item["evidence"][0] for item in found_for_pair if item.get("evidence")]
            interactions.append(primary)
        elif predicted_for_pair:
            # Sort predicted by highest confidence
            predicted_for_pair.sort(key=lambda x: x["confidence"] or 0, reverse=True)
            interactions.append(predicted_for_pair[0])
        else:
            safe_pairs.append({
                "brand_a": brand_a,
                "brand_b": brand_b,
                "note":    "No documented interaction in current knowledge base",
                "status":  "not_documented",
            })

    # Sort interactions: Documented MAJOR → MODERATE → MINOR → Predicted
    interactions.sort(key=lambda x: (_status_rank(x.get("status")), _severity_rank(x["severity"])))

    return {
        "total_drugs":         len(brand_names),
        "brand_names":         brand_names,
        "pairs_checked":       pairs_checked,
        "interactions_found":  len(interactions),
        "safe_pairs":          len(safe_pairs),
        "interactions":        interactions,
        "safe_pairs_detail":   safe_pairs,
        "summary":             _build_summary(interactions),
    }


def _query_interactions_batch(session, pairs: list[tuple[str, str]]) -> dict[tuple[str, str], list[dict]]:
    """
    Executes a single Cypher UNWIND query to retrieve interactions for multiple generic pairs.
    """
    CYPHER = """
    UNWIND $pairs AS p
    MATCH (a:Ingredient {name: p[0]})-[r:INTERACTS_WITH]-(b:Ingredient {name: p[1]})
    RETURN
        a.name      AS ingredient_a,
        b.name      AS ingredient_b,
        r.severity  AS severity,
        r.mechanism AS mechanism
    """
    raw_pairs = [[p[0], p[1]] for p in pairs]
    results = session.run(CYPHER, pairs=raw_pairs)

    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in results:
        ing_a = str(row["ingredient_a"])
        ing_b = str(row["ingredient_b"])
        key = (min(ing_a, ing_b), max(ing_a, ing_b))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            "ingredient_a": ing_a,
            "ingredient_b": ing_b,
            "severity":     str(row["severity"] or "MODERATE").upper(),
            "mechanism":    str(row["mechanism"] or "")[:500],
        })
    return grouped


def _build_explanation(brand_a, ing_a, brand_b, ing_b, severity, mechanism) -> str:
    """
    Builds the XAI explanation sentence for documented KG interactions.
    """
    sev_text = {
        "MAJOR":    "⚠️ MAJOR RISK",
        "MODERATE": "⚠️ MODERATE RISK",
        "MINOR":    "ℹ️ MINOR INTERACTION",
    }.get(severity, "INTERACTION DETECTED")

    mech = mechanism.strip()
    if len(mech) > 300:
        mech = mech[:297] + "..."

    return (
        f"{sev_text}: {brand_a} and {brand_b} interact.\n\n"
        f"{brand_a} contains {ing_a.title()}. "
        f"{brand_b} contains {ing_b.title()}.\n\n"
        f"Mechanism: {mech}"
    )


def _build_predicted_explanation(brand_a, ing_a, brand_b, ing_b, probability) -> str:
    """
    Builds explanation for GNN AI-predicted interactions.
    """
    pct = round(probability * 100, 1)
    return (
        f"🤖 AI PREDICTED INTERACTION ({pct}% confidence): {brand_a} and {brand_b}.\n\n"
        f"{brand_a} contains {ing_a.title()}. "
        f"{brand_b} contains {ing_b.title()}.\n\n"
        f"Note: This interaction is not yet indexed in the primary Knowledge Graph, "
        f"but was inferred by the Graph Neural Network (GraphSAGE link prediction)."
    )


def _severity_rank(sev: str) -> int:
    return {"MAJOR": 0, "MODERATE": 1, "MINOR": 2}.get(sev, 3)


def _status_rank(status: str | None) -> int:
    return {"documented": 0, "predicted": 1}.get(status or "", 2)


def _build_summary(interactions: list) -> str:
    if not interactions:
        return "No documented drug interactions detected in knowledge base."
    doc_major    = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MAJOR")
    doc_moderate = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MODERATE")
    doc_minor    = sum(1 for i in interactions if i.get("status") == "documented" and i["severity"] == "MINOR")
    predicted    = sum(1 for i in interactions if i.get("status") == "predicted")

    parts = []
    if doc_major:    parts.append(f"{doc_major} MAJOR (Documented)")
    if doc_moderate: parts.append(f"{doc_moderate} MODERATE (Documented)")
    if doc_minor:    parts.append(f"{doc_minor} MINOR (Documented)")
    if predicted:    parts.append(f"{predicted} AI PREDICTED")

    return f"{len(interactions)} interaction(s) found: {', '.join(parts)}."



# ─────────────────────────────────────────────────────────────────────────────
# DRUG INFO  —  GET /drug/{name}
# ─────────────────────────────────────────────────────────────────────────────
def get_drug_info(brand_name: str, generics: list[str]) -> dict:
    """
    Returns full information about a drug for the detail view.
    Queries all known interactions for each of its generic ingredients.
    """
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
                    "severity":       row["severity"],
                    "mechanism":      str(row["mechanism"] or "")[:300],
                })

    # Count by severity
    major    = [i for i in all_interactions if i["severity"] == "MAJOR"]
    moderate = [i for i in all_interactions if i["severity"] == "MODERATE"]
    minor    = [i for i in all_interactions if i["severity"] == "MINOR"]

    return {
        "brand_name":      brand_name,
        "generics":        generics,
        "total_known_ddis": len(all_interactions),
        "major_count":     len(major),
        "moderate_count":  len(moderate),
        "minor_count":     len(minor),
        "interactions":    all_interactions,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH DATA  —  GET /graph/{brands}  (for Pyvis visualisation)
# ─────────────────────────────────────────────────────────────────────────────
def get_interaction_graph(generics_map: dict[str, list[str]]) -> dict:
    """
    Returns nodes and edges for the Pyvis graph visualisation.
    Called by the Streamlit frontend after a /check query.
    """
    driver = get_driver()
    nodes  = {}
    edges  = []

    all_generics = set()
    for brand, generics in generics_map.items():
        # Drug node
        nodes[brand] = {
            "id":    brand,
            "label": brand,
            "type":  "Drug",
            "color": "#4A90D9",
            "size":  20,
        }
        for g in generics:
            all_generics.add(g)
            # Ingredient node
            nodes[g] = {
                "id":    g,
                "label": g.title(),
                "type":  "Ingredient",
                "color": "#27AE60",
                "size":  15,
            }
            # CONTAINS edge
            edges.append({
                "from":   brand,
                "to":     g,
                "label":  "CONTAINS",
                "color":  "#95A5A6",
                "dashes": False,
                "width":  1,
            })

    # Find all INTERACTS_WITH edges between generics
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
                    "from":      row["a"],
                    "to":        row["b"],
                    "label":     row["sev"],
                    "color":     color,
                    "dashes":    False,
                    "width":     3 if row["sev"] == "MAJOR" else 2,
                    "title":     str(row["mech"] or "")[:200],
                    "severity":  row["sev"],
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
    }
