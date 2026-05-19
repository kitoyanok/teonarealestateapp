import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.base import BaseAdapter, SourceConfig


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.adapter = BaseAdapter(
            SourceConfig(
                name="Тестовый источник",
                base_url="https://example.com",
                start_urls=("https://example.com",),
                property_type="apartment",
                source_type="test",
                adapter_key="test",
            )
        )

    def test_bad_apartment_title_is_replaced_with_structured_title(self):
        title = self.adapter._normalize_title(
            "Все новостройки",
            "apartment",
            "Тестовый источник",
            area=40.6,
            rooms=1,
            complex_name="Nova Vita",
        )

        self.assertEqual(title, "1-к квартира, 40.6 м² в ЖК «Nova Vita»")

    def test_house_title_uses_land_and_location(self):
        title = self.adapter._normalize_title(
            "Избранное",
            "house",
            "Тестовый источник",
            area=128,
            settlement_name="Мелодия",
            land_area=5,
        )

        self.assertEqual(title, "Дом 128 м², участок 5 сот. в КП «Мелодия»")

    def test_bad_image_url_is_rejected(self):
        self.assertIsNone(self.adapter._normalize_image_url("https://example.com", "/assets/logo.png"))
        self.assertIsNone(self.adapter._normalize_image_url("https://example.com", "/assets/icon.svg"))


if __name__ == "__main__":
    unittest.main()
