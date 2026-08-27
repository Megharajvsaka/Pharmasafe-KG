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


# ─────────────────────────────────────────────────────────────────────────────
# POLYPHARMACY ENGINE  —  POST /check
# ─────────────────────────────────────────────────────────────────────────────
def check_interactions(generics_map: dict[str, list[str]]) -> dict:
    """
    Core polypharmacy DDI detection engine.

    Args:
        generics_map: {brand_name: [generic1, generic2, ...], ...}

    Algorithm:
        1. For every PAIR of brands, take the cross product of their generics
        2. For each generic pair, query Neo4j for INTERACTS_WITH relationship
        3. Return all found interactions sorted by severity

    Returns a structured result dict consumed directly by the API and frontend.
    """
    driver = get_driver()

    # Flatten: collect all brand→generic mappings
    brand_names   = list(generics_map.keys())
    all_generics  = set()
    for generics in generics_map.values():
        all_generics.update(generics)

    interactions  = []
    pairs_checked = 0
    safe_pairs    = []

    # Generate all unique brand pairs
    brand_pairs = [
        (brand_names[i], brand_names[j])
        for i in range(len(brand_names))
        for j in range(i + 1, len(brand_names))
    ]

    with driver.session() as session:
        for brand_a, brand_b in brand_pairs:
            generics_a = generics_map.get(brand_a, [])
            generics_b = generics_map.get(brand_b, [])

            found_for_pair = []

            # Check every generic combination between the two brands
            for g_a in generics_a:
                for g_b in generics_b:
                    if g_a == g_b:
                        continue
                    pairs_checked += 1

                    result = _query_interaction(session, g_a, g_b)
                    if result:
                        found_for_pair.append({
                            "brand_a":      brand_a,
                            "brand_b":      brand_b,
                            "ingredient_a": result["ingredient_a"],
                            "ingredient_b": result["ingredient_b"],
                            "severity":     result["severity"],
                            "mechanism":    result["mechanism"],
                            "explanation":  _build_explanation(
                                brand_a, result["ingredient_a"],
                                brand_b, result["ingredient_b"],
                                result["severity"], result["mechanism"]
                            ),
                        })

            if found_for_pair:
                # Keep only the highest-severity result per brand pair
                found_for_pair.sort(key=lambda x: _severity_rank(x["severity"]))
                interactions.append(found_for_pair[0])
            else:
                safe_pairs.append({
                    "brand_a": brand_a,
                    "brand_b": brand_b,
                    "note":    "No known interaction detected"
                })

    # Sort interactions: MAJOR → MODERATE → MINOR
    interactions.sort(key=lambda x: _severity_rank(x["severity"]))

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


def _query_interaction(session, generic_a: str, generic_b: str) -> dict | None:
    """
    Runs a single Cypher query to check if two generics interact.
    Direction-agnostic: checks both (a→b) and (b→a).
    Returns None if no interaction found.
    """
    CYPHER = """
    MATCH (a:Ingredient {name: $g_a})-[r:INTERACTS_WITH]-(b:Ingredient {name: $g_b})
    RETURN
        a.name           AS ingredient_a,
        b.name           AS ingredient_b,
        r.severity       AS severity,
        r.mechanism      AS mechanism
    LIMIT 1
    """
    result = session.run(CYPHER, g_a=generic_a, g_b=generic_b)
    row = result.single()

    if row:
        return {
            "ingredient_a": row["ingredient_a"],
            "ingredient_b": row["ingredient_b"],
            "severity":     row["severity"],
            "mechanism":    str(row["mechanism"] or "")[:500],
        }
    return None


def _build_explanation(brand_a, ing_a, brand_b, ing_b, severity, mechanism) -> str:
    """
    Builds the XAI explanation sentence shown to the doctor.
    This is the core explainability output of the system.
    """
    sev_text = {
        "MAJOR":    "⚠️ MAJOR RISK",
        "MODERATE": "⚠️ MODERATE RISK",
        "MINOR":    "ℹ️ MINOR INTERACTION",
    }.get(severity, "INTERACTION DETECTED")

    # Shorten mechanism if too long
    mech = mechanism.strip()
    if len(mech) > 300:
        mech = mech[:297] + "..."

    return (
        f"{sev_text}: {brand_a} and {brand_b} interact.\n\n"
        f"{brand_a} contains {ing_a.title()}. "
        f"{brand_b} contains {ing_b.title()}.\n\n"
        f"Mechanism: {mech}"
    )


def _severity_rank(sev: str) -> int:
    return {"MAJOR": 0, "MODERATE": 1, "MINOR": 2}.get(sev, 3)


def _build_summary(interactions: list) -> str:
    if not interactions:
        return "No drug interactions detected. All combinations appear safe."
    major    = sum(1 for i in interactions if i["severity"] == "MAJOR")
    moderate = sum(1 for i in interactions if i["severity"] == "MODERATE")
    minor    = sum(1 for i in interactions if i["severity"] == "MINOR")
    parts = []
    if major:    parts.append(f"{major} MAJOR")
    if moderate: parts.append(f"{moderate} MODERATE")
    if minor:    parts.append(f"{minor} MINOR")
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
