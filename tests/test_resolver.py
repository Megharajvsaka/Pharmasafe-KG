import unittest
from backend.app.services.resolver_service import get_resolver, ALIASES


class TestResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        count = get_resolver().load()
        assert count > 0, "Resolver failed to load mapping table"

    def test_resolve_exact_brand_combination(self):
        res = get_resolver().resolve_brand("Combiflam")
        self.assertEqual(res["match_type"], "exact")
        self.assertEqual(res["confidence"], 100)
        self.assertFalse(res["review_required"])
        self.assertTrue("ibuprofen" in res["generics"])
        self.assertTrue("paracetamol" in res["generics"] or "acetaminophen" in res["generics"])

    def test_resolve_case_and_whitespace_insensitivity(self):
        res1 = get_resolver().resolve_brand("  combiflam  ")
        res2 = get_resolver().resolve_brand("COMBIFLAM")
        self.assertEqual(res1["match_type"], "exact")
        self.assertEqual(res2["match_type"], "exact")
        self.assertEqual(set(res1["generics"]), set(res2["generics"]))

    def test_resolve_alias(self):
        res = get_resolver().resolve_brand("paracetamol")
        self.assertIn(res["match_type"], ["alias", "generic_direct", "exact"])
        self.assertTrue("paracetamol" in res["generics"] or "acetaminophen" in res["generics"])

    def test_resolve_direct_generic(self):
        res = get_resolver().resolve_brand("warfarin")
        self.assertIn(res["match_type"], ["generic_direct", "alias", "exact"])
        self.assertIn("warfarin", res["generics"])
        self.assertEqual(res["confidence"], 100)

    def test_resolve_fuzzy_brand(self):
        res = get_resolver().resolve_brand("Combiflamm")
        self.assertEqual(res["match_type"], "fuzzy")
        self.assertGreaterEqual(res["confidence"], 80)
        self.assertIn("ibuprofen", res["generics"])

    def test_resolve_not_found(self):
        res = get_resolver().resolve_brand("NON_EXISTENT_DRUG_XYZ_123")
        self.assertEqual(res["match_type"], "not_found")
        self.assertEqual(res["confidence"], 0)
        self.assertEqual(res["generics"], [])

    def test_resolve_multiple(self):
        res = get_resolver().resolve_multiple(["Combiflam", "Ecosprin", "Pantop 40"])
        self.assertEqual(len(res), 3)
        self.assertIn("Combiflam", res)
        self.assertIn("Ecosprin", res)
        self.assertIn("Pantop 40", res)

    def test_search_autocomplete(self):
        results = get_resolver().search_brands("Combi", limit=5)
        self.assertGreater(len(results), 0)
        self.assertTrue(any("combi" in r.lower() for r in results))


if __name__ == "__main__":
    unittest.main()
