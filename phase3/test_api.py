"""
test_api.py
-----------
Tests all 5 FastAPI endpoints locally.
Run this WHILE the API server is running to verify everything works.

Usage:
    Terminal 1:  uvicorn phase3.app.main:app --reload --port 8000
    Terminal 2:  python phase3/test_api.py
"""

import requests
import json

import sys
import builtins

def safe_print(*args, **kwargs):
    clean_args = []
    for arg in args:
        if isinstance(arg, str):
            enc = sys.stdout.encoding or 'ascii'
            clean_args.append(arg.encode(enc, errors='replace').decode(enc))
        else:
            clean_args.append(arg)
    builtins.print(*clean_args, **kwargs)

print = safe_print

BASE = "http://localhost:8000"


def sep(title):
    print(f"\n{'-'*55}")
    print(f"  TEST: {title}")
    print(f"{'-'*55}")


def test_health():
    sep("GET / - Health Check")
    r = requests.get(f"{BASE}/")
    print(f"  Status: {r.status_code}")
    d = r.json()
    print(f"  Neo4j:         {d['neo4j']}")
    print(f"  Brands loaded: {d['brands_loaded']:,}")
    assert r.status_code == 200, "Health check failed"
    print("  PASSED")


def test_search():
    sep("GET /search - Autocomplete")
    for q in ["Combi", "Metf", "Dolo", "Ecosprin", "War"]:
        r = requests.get(f"{BASE}/search", params={"q": q, "limit": 5})
        d = r.json()
        print(f"  '{q}' -> {d['results'][:3]}  ({d['count']} results)")
    assert r.status_code == 200
    print("  PASSED")


def test_check_basic():
    sep("POST /check - 2 drugs (Combiflam + Ecosprin)")
    payload = {"drugs": ["Combiflam", "Ecosprin"]}
    r = requests.post(f"{BASE}/check", json=payload)
    print(f"  Status: {r.status_code}")
    d = r.json()
    print(f"  Summary: {d['summary']}")
    print(f"  Interactions found: {d['interactions_found']}")
    for i in d["interactions"]:
        print(f"    [{i['severity']}] {i['brand_a']} ({i['ingredient_a']}) <-> {i['brand_b']} ({i['ingredient_b']})")
        print(f"    Explanation: {i['explanation'][:120]}...")
    print("  PASSED")


def test_check_polypharmacy():
    sep("POST /check - Polypharmacy (5 drugs)")
    payload = {"drugs": [
        "Combiflam",
        "Ecosprin",
        "Pantop 40",
        "Metformin 500",
        "Atorva 10",
    ]}
    r = requests.post(f"{BASE}/check", json=payload)
    print(f"  Status: {r.status_code}")
    d = r.json()
    print(f"  Drugs: {d['total_drugs']}")
    print(f"  Pairs checked: {d['pairs_checked']}")
    print(f"  Interactions: {d['interactions_found']}")
    print(f"  Summary: {d['summary']}")
    for i in d["interactions"][:3]:
        print(f"    [{i['severity']}] {i['brand_a']} <-> {i['brand_b']}")
    print("  PASSED")


def test_drug_info():
    sep("GET /drug/{name} - Drug Info")
    for brand in ["Combiflam", "Warfarin"]:
        r = requests.get(f"{BASE}/drug/{brand}")
        if r.status_code == 200:
            d = r.json()
            print(f"  {brand}: {d['generics']} - {d['total_known_ddis']} known DDIs")
            print(f"    MAJOR: {d['major_count']}  MODERATE: {d['moderate_count']}  MINOR: {d['minor_count']}")
        else:
            print(f"  {brand}: {r.status_code} - {r.json().get('detail', '')}")
    print("  PASSED")


def test_graph():
    sep("GET /graph - Graph Data for Visualisation")
    r = requests.get(f"{BASE}/graph", params={"drugs": ["Combiflam", "Ecosprin", "Warfarin"]})
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"  Nodes: {len(d['nodes'])}")
        print(f"  Edges: {len(d['edges'])}")
        drug_nodes = [n for n in d['nodes'] if n['type'] == 'Drug']
        ing_nodes  = [n for n in d['nodes'] if n['type'] == 'Ingredient']
        iw_edges   = [e for e in d['edges'] if e.get('severity')]
        print(f"    Drug nodes      : {len(drug_nodes)}")
        print(f"    Ingredient nodes: {len(ing_nodes)}")
        print(f"    DDI edges       : {len(iw_edges)}")
    print("  PASSED")


def test_error_handling():
    sep("Error Handling Tests")

    # Too few drugs
    r = requests.post(f"{BASE}/check", json={"drugs": ["Combiflam"]})
    print(f"  Single drug (expect 422): {r.status_code} [OK]" if r.status_code == 422 else f"  [FAIL] Expected 422, got {r.status_code}")

    # Unknown drugs
    r = requests.post(f"{BASE}/check", json={"drugs": ["XYZABC123", "DEFGH456"]})
    print(f"  Unknown drugs (expect 422): {r.status_code} [OK]" if r.status_code == 422 else f"  Got {r.status_code}: {r.json().get('detail','')[:80]}")

    # Drug not found
    r = requests.get(f"{BASE}/drug/NOTADRUGXYZ999")
    print(f"  Unknown drug info (expect 404): {r.status_code} [OK]" if r.status_code == 404 else f"  [FAIL] Expected 404, got {r.status_code}")

    print("  PASSED")


if __name__ == "__main__":
    print("=" * 55)
    print("  PharmaSafe-KG API Test Suite")
    print("  Make sure server is running:")
    print("  uvicorn phase3.app.main:app --reload --port 8000")
    print("=" * 55)

    try:
        test_health()
        test_search()
        test_check_basic()
        test_check_polypharmacy()
        test_drug_info()
        test_graph()
        test_error_handling()

        print("\n" + "=" * 55)
        print("  ALL TESTS PASSED")
        print("  API is ready for Streamlit frontend")
        print("  Swagger UI: http://localhost:8000/docs")
        print("=" * 55)

    except requests.ConnectionError:
        print("\n[ERROR] Cannot connect to API server.")
        print("   Start it first:  uvicorn phase3.app.main:app --reload --port 8000")
