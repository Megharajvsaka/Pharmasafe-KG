"""
tests/test_resolver.py
----------------------
Unit tests for the Indian Brand-to-Generic resolver using standard unittest.
"""

import unittest
from phase3.app.resolver import load_resolver, resolve_brand, resolve_multiple, search_brands


class TestResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        count = load_resolver()
        assert count > 0, "Resolver failed to load mapping table"

    def test_resolve_exact_brand_combination(self):
        """Test exact resolution of multi-ingredient combination medicine."""
        res = resolve_brand("Combiflam")
        self.assertEqual(res["match_type"], "exact")
        self.assertEqual(res["confidence"], 100)
        self.assertFalse(res["review_required"])
        self.assertTrue("ibuprofen" in res["generics"])
        self.assertTrue("paracetamol" in res["generics"] or "acetaminophen" in res["generics"])

    def test_resolve_case_and_whitespace_insensitivity(self):
        """Test resolution with abnormal casing and leading/trailing whitespace."""
        res1 = resolve_brand("  combiflam  ")
        res2 = resolve_brand("COMBIFLAM")
        self.assertEqual(res1["match_type"], "exact")
        self.assertEqual(res2["match_type"], "exact")
        self.assertEqual(set(res1["generics"]), set(res2["generics"]))

    def test_resolve_alias(self):
        """Test alias expansion for standard clinical aliases."""
        res = resolve_brand("paracetamol")
        self.assertIn(res["match_type"], ["alias", "generic_direct", "exact"])
        self.assertTrue("paracetamol" in res["generics"] or "acetaminophen" in res["generics"])

    def test_resolve_direct_generic(self):
        """Test typing a generic name directly (e.g. warfarin)."""
        res = resolve_brand("warfarin")
        self.assertIn(res["match_type"], ["generic_direct", "alias", "exact"])
        self.assertIn("warfarin", res["generics"])
        self.assertEqual(res["confidence"], 100)

    def test_resolve_fuzzy_brand(self):
        """Test fuzzy resolution for minor spelling typos."""
        res = resolve_brand("Combiflamm")
        self.assertEqual(res["match_type"], "fuzzy")
        self.assertGreaterEqual(res["confidence"], 80)
        self.assertIn("ibuprofen", res["generics"])

    def test_resolve_not_found(self):
        """Test behavior on non-existent drug."""
        res = resolve_brand("NON_EXISTENT_DRUG_XYZ_123")
        self.assertEqual(res["match_type"], "not_found")
        self.assertEqual(res["confidence"], 0)
        self.assertEqual(res["generics"], [])

    def test_resolve_multiple(self):
        """Test batch resolution of multiple brand names."""
        res = resolve_multiple(["Combiflam", "Ecosprin", "Pantop 40"])
        self.assertEqual(len(res), 3)
        self.assertIn("Combiflam", res)
        self.assertIn("Ecosprin", res)
        self.assertIn("Pantop 40", res)

    def test_search_autocomplete(self):
        """Test search autocomplete prefix matching."""
        results = search_brands("Combi", limit=5)
        self.assertGreater(len(results), 0)
        self.assertTrue(any("combi" in r.lower() for r in results))


if __name__ == "__main__":
    unittest.main()
