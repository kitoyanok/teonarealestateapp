"""Этот файл проверяет очистку и нормализацию объявлений.
Проще говоря: он следит, чтобы система не принимала мусорные заголовки, чужие города и ложные характеристики."""

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

    def test_krasnodar_city_filter_rejects_other_krai_cities(self):
        self.assertFalse(
            self.adapter._is_krasnodar_city(
                "Краснодарский край, Новороссийск, 1-к квартира 40 м²",
                "https://krasnodar.example.com/catalog"
            )
        )

    def test_krasnodar_city_filter_accepts_city_district(self):
        self.assertTrue(
            self.adapter._is_krasnodar_city(
                "Краснодар, Прикубанский район, 2-к квартира 65 м²",
                "https://example.com/catalog"
            )
        )

    def test_city_district_and_characteristics_are_extracted(self):
        text = "г. Краснодар, Карасунский район, 2-к квартира 54 м², 7/16 этаж, предчистовая отделка"

        self.assertEqual(self.adapter._extract_district(text), "Карасунский")
        self.assertEqual(self.adapter._parse_floor(text), (7, 16))
        self.assertEqual(self.adapter._parse_finishing(text), "предчистовая")


if __name__ == "__main__":
    unittest.main()
