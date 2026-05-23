"""Этот файл проверяет правильность расчета совпадения для квартир и домов.
Проще говоря: он страхует систему от ошибок в логике ранжирования объектов."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.property import PropertyItem, SearchRequest
from app.services.matcher import score_property


class MatcherTests(unittest.TestCase):
    def test_apartment_filters_keep_apartment_context(self):
        request = SearchRequest(
            clientId="1",
            propertyType="apartment",
            budgetMax=8_000_000,
            roomsMin=1,
            roomsMax=2,
            areaMin=35,
            districts=["Прикубанский"],
        )
        item = PropertyItem(
            sourceName="Тест",
            sourceUrl="https://example.com/a1",
            propertyType="apartment",
            title="1-к квартира, 40.6 м² в ЖК «Nova Vita»",
            price=5_275_000,
            area=40.6,
            rooms=1,
            district="Прикубанский",
        )

        scored = score_property(item, request)

        self.assertGreaterEqual(scored.matchScore or 0, 60)
        self.assertIn("Цена подходит", scored.matchReasons)
        self.assertIn("Комнатность подходит", scored.matchReasons)

    def test_house_filters_keep_house_context(self):
        request = SearchRequest(
            clientId="1",
            propertyType="house",
            budgetMax=10_000_000,
            houseAreaMin=100,
            landAreaMin=4,
            settlementNames=["Немецкая деревня"],
        )
        item = PropertyItem(
            sourceName="Тест",
            sourceUrl="https://example.com/h1",
            propertyType="house",
            title="Дом 128 м², участок 5 сот. в Немецкой деревне",
            price=9_350_000,
            houseArea=128,
            landArea=5,
            settlementName="Немецкая деревня",
        )

        scored = score_property(item, request)

        self.assertGreaterEqual(scored.matchScore or 0, 50)
        self.assertIn("Площадь дома подходит", scored.matchReasons)
        self.assertIn("Участок подходит", scored.matchReasons)
        self.assertIn("Локация подходит", scored.matchReasons)


if __name__ == "__main__":
    unittest.main()
