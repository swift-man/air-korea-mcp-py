import unittest

from air_korea_mcp.exceptions import AirKoreaError
from air_korea_mcp.location_resolution import resolve_sido_name


class LocationResolutionTests(unittest.TestCase):
    def test_resolve_direct_sido_alias(self):
        self.assertEqual("서울", resolve_sido_name("서울특별시"))

    def test_resolve_unique_dong_to_sido(self):
        self.assertEqual("서울", resolve_sido_name("우면동"))

    def test_resolve_base_name_without_dong_suffix(self):
        self.assertEqual("서울", resolve_sido_name("우면"))

    def test_resolve_token_intersection_to_sido(self):
        self.assertEqual("서울", resolve_sido_name("서초구 우면동"))

    def test_resolve_base_name_without_suffix_in_multi_token_input(self):
        self.assertEqual("경기", resolve_sido_name("분당구 수내"))

    def test_raise_for_ambiguous_location(self):
        with self.assertRaises(AirKoreaError) as context:
            resolve_sido_name("삼성동")

        message = str(context.exception)
        self.assertIn("ambiguous", message)
        self.assertIn("서울특별시 강남구 삼성동", message)
        self.assertIn("대전광역시 동구 삼성동", message)

    def test_raise_for_ambiguous_location_with_suffixless_guidance(self):
        with self.assertRaises(AirKoreaError) as context:
            resolve_sido_name("판교")

        message = str(context.exception)
        self.assertIn("ambiguous", message)
        self.assertIn("경기도 성남시 분당구 판교동", message)
        self.assertIn("충청남도 서천군 판교면", message)

    def test_raise_with_guidance_for_unsupported_foreign_location(self):
        with self.assertRaises(AirKoreaError) as context:
            resolve_sido_name("도쿄")

        message = str(context.exception)
        self.assertIn("not supported", message)
        self.assertIn("South Korea regions only", message)
        self.assertIn("우면동", message)


if __name__ == "__main__":
    unittest.main()
