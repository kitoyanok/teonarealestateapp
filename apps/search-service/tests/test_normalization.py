import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.base import BaseAdapter, SourceConfig
from app.utils.text import parse_rooms


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

        self.assertEqual(title, "1-к квартира, 40.6 м²")

    def test_house_title_uses_land_and_location(self):
        title = self.adapter._normalize_title(
            "Избранное",
            "house",
            "Тестовый источник",
            area=128,
            settlement_name="Мелодия",
            land_area=5,
        )

        self.assertEqual(title, "Дом 128 м²")

    def test_bad_image_url_is_rejected(self):
        self.assertIsNone(self.adapter._normalize_image_url("https://example.com", "/assets/logo.png"))
        self.assertIsNone(self.adapter._normalize_image_url("https://example.com", "/assets/icon.svg"))

    def test_rooms_parser_ignores_apartment_count_phrase(self):
        self.assertIsNone(parse_rooms("В продаже 21 квартира в жилом комплексе"))

    def test_description_with_phone_is_rejected(self):
        description = self.adapter._clean_description(
            "ЖК Контакты +7 (908) 726-63-51. В продаже квартира. Подробности по телефону.",
            title="1-к квартира, 41.39 м²",
        )
        self.assertIsNone(description)


if __name__ == "__main__":
    unittest.main()
