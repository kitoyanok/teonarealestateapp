import hashlib
import json
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.schemas.property import PropertyItem, SearchRequest
from app.utils.text import clean_text, extract_year, parse_area, parse_price, parse_rooms

BAD_IMAGE_MARKERS = ("logo", "favicon", "icon", "sprite", "placeholder", "avatar", "brand", "social")
BAD_TITLE_MARKERS = (
    "кабинет", "избранное", "отзывы", "отзывов", "наверх", "главная", "меню",
    "ипотека", "акции", "ремонт в подарок", "скидка", "все квартиры", "все дома",
    "подобрать", "фильтр"
)
BAD_DESCRIPTION_MARKERS = ("главная", "меню", "по алфавиту", "на карте", "скоро в продаже", "избранное", "отзывы")


@dataclass(frozen=True)
class SourceConfig:
    name: str
    base_url: str
    start_urls: tuple[str, ...]
    property_type: str
    source_type: str
    adapter_key: str


class BaseAdapter:
    def __init__(self, config: SourceConfig):
        self.config = config

    async def search(self, client: httpx.AsyncClient, request: SearchRequest) -> list[PropertyItem]:
        items: list[PropertyItem] = []
        for url in self.config.start_urls:
            if not await self._can_fetch(client, url):
                continue
            html = await self._fetch(client, url)
            if not html:
                continue
            items.extend(self._parse_html(url, html, request))
        return items

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> str | None:
        try:
            response = await client.get(url, follow_redirects=True)
            if response.status_code >= 400:
                return None
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None
            return response.text
        except httpx.HTTPError:
            return None

    async def _can_fetch(self, client: httpx.AsyncClient, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            response = await client.get(robots_url, follow_redirects=True)
            if response.status_code >= 400:
                return True
            parser = RobotFileParser()
            parser.parse(response.text.splitlines())
            return parser.can_fetch("EstateFlowBot", url) and parser.can_fetch("*", url)
        except Exception:
            return False

    def _parse_html(self, url: str, html: str, request: SearchRequest) -> list[PropertyItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = self._parse_json_ld(url, soup, request)
        items.extend(self._parse_visible_cards(url, soup, request))

        unique: dict[str, PropertyItem] = {}
        for item in items:
            if item.price is None:
                continue
            unique[item.sourceUrl] = item
        return list(unique.values())[:40]

    def _parse_json_ld(self, url: str, soup: BeautifulSoup, request: SearchRequest) -> list[PropertyItem]:
        items: list[PropertyItem] = []
        for script in soup.select('script[type="application/ld+json"]'):
            text = script.string or script.get_text(strip=True)
            if not text:
                continue
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            for node in self._flatten_json_ld(data):
                item = self._item_from_json_ld(url, node, request)
                if item:
                    items.append(item)
        return items

    def _flatten_json_ld(self, data: object) -> list[dict]:
        nodes: list[dict] = []
        if isinstance(data, list):
            for item in data:
                nodes.extend(self._flatten_json_ld(item))
        elif isinstance(data, dict):
            graph = data.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    nodes.extend(self._flatten_json_ld(item))
            nodes.append(data)
        return nodes

    def _item_from_json_ld(self, url: str, node: dict, request: SearchRequest) -> PropertyItem | None:
        node_type = str(node.get("@type", "")).lower()
        if not any(kind in node_type for kind in ["product", "offer", "apartment", "house", "residence", "realestate"]):
            return None

        raw_title = clean_text(str(node.get("name") or node.get("headline") or ""))
        description = self._normalize_description(clean_text(str(node.get("description") or "")) or None, request, self.config.name)
        offers = node.get("offers") if isinstance(node.get("offers"), dict) else {}
        raw_price = node.get("price") or offers.get("price") or offers.get("lowPrice")
        price = float(raw_price) if str(raw_price).replace(".", "", 1).isdigit() else parse_price(f"{raw_title} {description}")
        item_url = str(node.get("url") or offers.get("url") or url)
        image = node.get("image")
        raw_images = [image] if isinstance(image, str) else image if isinstance(image, list) else []

        text = f"{raw_title} {description or ''}"
        area = parse_area(text)
        rooms = parse_rooms(text)
        title = self._normalize_title(raw_title, request.propertyType, self.config.name, area=area, rooms=rooms)
        images = [normalized for item in raw_images[:6] if (normalized := self._normalize_image_url(url, str(item)))]

        return PropertyItem(
            externalId=self._external_id(item_url),
            sourceName=self.config.name,
            sourceUrl=urljoin(url, item_url),
            propertyType=request.propertyType,
            title=title,
            description=description,
            price=price,
            area=area,
            rooms=rooms,
            houseArea=area if request.propertyType == "house" else None,
            completionYear=extract_year(text),
            images=images,
            rawData={"sourceType": "json-ld", "adapter": self.config.adapter_key}
        )

    def _parse_visible_cards(self, url: str, soup: BeautifulSoup, request: SearchRequest) -> list[PropertyItem]:
        items: list[PropertyItem] = []
        candidates = soup.select("a[href]")
        for link in candidates:
            card = link
            for _ in range(3):
                parent = card.parent
                if not parent:
                    break
                parent_text = clean_text(parent.get_text(" ", strip=True))
                if len(parent_text) > 80:
                    card = parent
                    break
                card = parent

            text = clean_text(card.get_text(" ", strip=True))
            if len(text) < 30 or not re.search(r"(₽|руб|млн)", text.lower()):
                continue

            href = link.get("href") or url
            item_url = urljoin(url, href)
            raw_title = clean_text(link.get_text(" ", strip=True)) or text[:120]
            image = card.select_one("img")
            image_url = image.get("src") or image.get("data-src") if image else None
            price = parse_price(text)
            area = parse_area(text)
            rooms = parse_rooms(text)

            if not price:
                continue

            title = self._normalize_title(raw_title, request.propertyType, self.config.name, area=area, rooms=rooms)
            description = self._normalize_description(text, request, self.config.name)
            normalized_image = self._normalize_image_url(url, image_url) if image_url else None

            items.append(
                PropertyItem(
                    externalId=self._external_id(item_url),
                    sourceName=self.config.name,
                    sourceUrl=item_url,
                    propertyType=request.propertyType,
                    title=title[:280],
                    description=description,
                    price=price,
                    pricePerMeter=round(price / area, 2) if price and area else None,
                    area=area if request.propertyType == "apartment" else None,
                    rooms=rooms if request.propertyType == "apartment" else None,
                    houseArea=area if request.propertyType == "house" else None,
                    completionYear=extract_year(text),
                    images=[normalized_image] if normalized_image else [],
                    rawData={"sourceType": "visible-card", "adapter": self.config.adapter_key}
                )
            )
        return items

    def _normalize_image_url(self, base_url: str, image_url: str | None) -> str | None:
        if not image_url:
            return None
        absolute = urljoin(base_url, image_url).strip()
        lowered = absolute.lower()
        if lowered.endswith(".svg"):
            return None
        if any(marker in lowered for marker in BAD_IMAGE_MARKERS):
            return None
        if not any(ext in lowered for ext in (".jpg", ".jpeg", ".png", ".webp")):
            return None
        return absolute

    def _normalize_title(
        self,
        value: str,
        property_type: str,
        source_name: str,
        *,
        area: float | None = None,
        rooms: int | None = None
    ) -> str:
        title = clean_text(value)[:180]
        if not title or any(marker in title.lower() for marker in BAD_TITLE_MARKERS):
            title = ""

        if property_type == "apartment":
            if title:
                return title
            if rooms is not None and area:
                rooms_label = "Студия" if rooms == 0 else f"{rooms}-комн. квартира"
                return f"{rooms_label}, {area} м²"
            return f"Квартира от {source_name}"

        if title:
            return title
        if area:
            return f"Дом {area} м²"
        return f"Дом от {source_name}"

    def _normalize_description(self, text: str | None, request: SearchRequest, source_name: str) -> str | None:
        cleaned = clean_text(text or "")
        if not cleaned:
            return f"{'Квартира' if request.propertyType == 'apartment' else 'Дом'} от источника {source_name}."

        parts = [part.strip() for part in re.split(r"[.!?]", cleaned) if part.strip()]
        deduped: list[str] = []
        seen: set[str] = set()
        for part in parts:
            lowered = part.lower()
            if lowered in seen or any(marker in lowered for marker in BAD_DESCRIPTION_MARKERS):
                continue
            seen.add(lowered)
            deduped.append(part)

        normalized = ". ".join(deduped)[:700]
        return normalized or f"{'Квартира' if request.propertyType == 'apartment' else 'Дом'} от источника {source_name}."

    def _external_id(self, value: str) -> str:
        digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
        return f"{self.config.adapter_key}:{digest}"
