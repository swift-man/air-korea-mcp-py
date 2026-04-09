import unittest

from air_korea_mcp.exceptions import AirKoreaError
from air_korea_mcp.location_resolution import resolve_sido_name


class LocationResolutionTests(unittest.TestCase):
    def test_resolve_direct_sido_alias(self):
        self.assertEqual("서울", resolve_sido_name("서울특별시"))

    def test_resolve_unique_dong_to_sido(self):
        self.assertEqual("서울", resolve_sido_name("우면동"))

    def test_resolve_token_intersection_to_sido(self):
        self.assertEqual("서울", resolve_sido_name("서초구 우면동"))

    def test_raise_for_ambiguous_location(self):
        with self.assertRaises(AirKoreaError) as context:
            resolve_sido_name("삼성동")

        self.assertIn("ambiguous", str(context.exception))


if __name__ == "__main__":
    unittest.main()
