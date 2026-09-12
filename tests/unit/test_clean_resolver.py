from backend.app.services.resolver_service import get_resolver, ALIASES

def test_resolver_exact():
    res = get_resolver()
    result = res.resolve_brand("Combiflam")
    assert result["match_type"] in ["exact", "alias"]
    assert "ibuprofen" in result["generics"]
    assert "paracetamol" in result["generics"] or "acetaminophen" in result["generics"]

def test_resolver_alias():
    res = get_resolver()
    result = res.resolve_brand("Ecosprin")
    assert "aspirin" in result["generics"] or "acetylsalicylic acid" in result["generics"]

def test_search_autocomplete():
    res = get_resolver()
    matches = res.search_brands("Combi", limit=5)
    assert len(matches) > 0
    assert any("combi" in m.lower() for m in matches)
