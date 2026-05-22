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
    "подобрать", "фильтр", "все новостройки", "старт продаж", "скоро в продаже",
    "комфорт", "бизнес", "недорогие", "каталог"
)
BAD_DESCRIPTION_MARKERS = (
    "главная", "меню", "по алфавиту", "на карте", "скоро в продаже", "избранное", "отзывы",
    "кабинет", "скидка", "ремонт в подарок", "старт продаж", "каталог", "фильтр", "подобрать"
)
BAD_IMAGE_MARKERS = BAD_IMAGE_MARKERS + ("telegram", "vk", "whatsapp")
BAD_DESCRIPTION_PHRASES = (
    "контакты",
    "позвоните",
    "звоните",
    "заказать звонок",
    "подробнее",
    "смотреть все",
    "политика конфиденциальности",
    "в продаже",
)

KRASNODAR_CITY_PATTERNS = (
    r"\bг\.?\s*краснодар\b",
    r"\bгород\s+краснодар\b",
    r"\bкраснодар[,.\s]",
    r"\bкраснодар\s*,\s*ул",
)
KRASNODAR_URL_MARKERS = ("krasnodar", "krd", "%d0%ba%d1%80%d0%b0%d1%81%d0%bd%d0%be%d0%b4%d0%b0%d1%80")
EXCLUDED_KRAI_LOCALITIES = (
    "сочи", "адлер", "анап", "геленджик", "новороссийск", "армавир", "ейск", "туапсе",
    "горячий ключ", "славянск-на-кубани", "крымск", "тимашевск", "лабинск", "курганинск",
    "белореченск", "апшеронск", "темрюк", "абинск", "кореновск", "усть-лабинск", "динская",
    "северская", "афипский", "яблоновский", "адыгейск", "тахтамукай"
)

DISTRICT_ALIASES = (
    ("Прикубанский", ("прикубанский", "прик")),
    ("Карасунский", ("карасунский", "кмр", "гидростроителей", "гмр", "пашковский")),
    ("Западный", ("западный", "юмр", "юбилейный")),
    ("Центральный", ("центральный", "центр", "цмр", "черемушки", "чмр")),
    ("Фестивальный", ("фестивальный", "фмр")),
    ("Юбилейный", ("юбилейный", "юмр")),
    ("Гидростроителей", ("гидростроителей", "гмр")),
)


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
        soup = BeautifulSoup(html, "lxml")
        items = self._parse_json_ld(url, soup, request)
        items.extend(self._parse_visible_cards(url, soup, request))

        unique: dict[str, PropertyItem] = {}
        for item in items:
            if item.price is None:
                continue
            if item.city != "Краснодар":
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
        raw_description = clean_text(str(node.get("description") or ""))
        offers = node.get("offers") if isinstance(node.get("offers"), dict) else {}
        raw_price = node.get("price") or offers.get("price") or offers.get("lowPrice")
        price = float(raw_price) if str(raw_price).replace(".", "", 1).isdigit() else parse_price(raw_title)
        item_url = str(node.get("url") or offers.get("url") or url)
        image = node.get("image")
        raw_images = [image] if isinstance(image, str) else image if isinstance(image, list) else []
        brand = node.get("brand")
        developer_name = clean_text(brand.get("name")) if isinstance(brand, dict) else clean_text(str(brand or "")) or None
        text = clean_text(f"{raw_title} {node.get('description') or ''}")
        if not self._is_krasnodar_city(text, urljoin(url, item_url)):
            return None
        area = parse_area(text)
        rooms = parse_rooms(text)
        land_area = self._parse_land_area(text)
        complex_name = self._extract_complex_name(text, request.propertyType)
        district = self._extract_district(text)
        address = self._extract_address(text)
        settlement_name = self._extract_settlement_name(text, request.propertyType)
        title = self._normalize_title(
            raw_title,
            request.propertyType,
            self.config.name,
            area=area,
            rooms=rooms,
            complex_name=complex_name,
            district=district,
            address=address,
            settlement_name=settlement_name,
            land_area=land_area
        )
        images = [normalized for item in raw_images[:6] if (normalized := self._normalize_image_url(url, str(item)))]
        description = self._normalize_description(
            request,
            self.config.name,
            title=title,
            raw_description=raw_description,
            raw_text=text,
            price=price,
            area=area,
            rooms=rooms,
            district=district,
            address=address,
            settlement_name=settlement_name,
            land_area=land_area
        )

        return PropertyItem(
            externalId=self._external_id(item_url),
            sourceName=self.config.name,
            sourceUrl=urljoin(url, item_url),
            propertyType=request.propertyType,
            title=title,
            complexName=complex_name,
            developerName=developer_name,
            description=description,
            district=district,
            address=address,
            settlementName=settlement_name,
            price=price,
            pricePerMeter=round(price / area, 2) if price and area else None,
            area=area,
            rooms=rooms,
            houseArea=area if request.propertyType == "house" else None,
            landArea=land_area if request.propertyType == "house" else None,
            floor=self._parse_floor(text)[0],
            floorsTotal=self._parse_floor(text)[1],
            bedrooms=self._parse_bedrooms(text),
            houseFloors=self._parse_house_floors(text),
            houseMaterial=self._parse_house_material(text),
            communications=self._parse_communications(text),
            completionYear=extract_year(text),
            finishing=self._parse_finishing(text),
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
            if not self._is_krasnodar_city(text, item_url):
                continue
            raw_title = clean_text(link.get_text(" ", strip=True)) or text[:120]
            image = card.select_one("img")
            image_url = image.get("src") or image.get("data-src") if image else None
            description_parts = [
                clean_text(node.get_text(" ", strip=True))
                for node in card.select("p, li, .description, .text, .caption")
            ]
            raw_description = max(description_parts, key=len, default="")
            price = parse_price(text)
            area = parse_area(text)
            rooms = parse_rooms(text)

            if not price:
                continue

            land_area = self._parse_land_area(text)
            complex_name = self._extract_complex_name(text, request.propertyType)
            district = self._extract_district(text)
            address = self._extract_address(text)
            settlement_name = self._extract_settlement_name(text, request.propertyType)
            title = self._normalize_title(
                raw_title,
                request.propertyType,
                self.config.name,
                area=area,
                rooms=rooms,
                complex_name=complex_name,
                district=district,
                address=address,
                settlement_name=settlement_name,
                land_area=land_area
            )
            description = self._normalize_description(
                request,
                self.config.name,
                title=title,
                raw_description=raw_description,
                raw_text=text,
                price=price,
                area=area,
                rooms=rooms,
                district=district,
                address=address,
                settlement_name=settlement_name,
                land_area=land_area
            )
            normalized_image = self._normalize_image_url(url, image_url) if image_url else None

            items.append(
                PropertyItem(
                    externalId=self._external_id(item_url),
                    sourceName=self.config.name,
                    sourceUrl=item_url,
                    propertyType=request.propertyType,
                    title=title[:280],
                    complexName=complex_name,
                    description=description,
                    price=price,
                    pricePerMeter=round(price / area, 2) if price and area else None,
                    district=district,
                    address=address,
                    settlementName=settlement_name,
                    area=area if request.propertyType == "apartment" else None,
                    rooms=rooms if request.propertyType == "apartment" else None,
                    houseArea=area if request.propertyType == "house" else None,
                    landArea=land_area if request.propertyType == "house" else None,
                    floor=self._parse_floor(text)[0] if request.propertyType == "apartment" else None,
                    floorsTotal=self._parse_floor(text)[1] if request.propertyType == "apartment" else None,
                    bedrooms=self._parse_bedrooms(text) if request.propertyType == "house" else None,
                    houseFloors=self._parse_house_floors(text) if request.propertyType == "house" else None,
                    houseMaterial=self._parse_house_material(text) if request.propertyType == "house" else None,
                    communications=self._parse_communications(text) if request.propertyType == "house" else [],
                    completionYear=extract_year(text),
                    finishing=self._parse_finishing(text) if request.propertyType == "apartment" else None,
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
        rooms: int | None = None,
        complex_name: str | None = None,
        district: str | None = None,
        address: str | None = None,
        settlement_name: str | None = None,
        land_area: float | None = None
    ) -> str:
        title = clean_text(value)[:180]
        if not title or any(marker in title.lower() for marker in BAD_TITLE_MARKERS):
            title = ""

        if property_type == "apartment":
            rooms_label = "Студия" if rooms == 0 else f"{rooms}-к квартира" if rooms is not None else "Квартира"
            area_label = f", {area} м²" if area else ""
            return f"{rooms_label}{area_label}".strip(", ")

        house_area = f"Дом {area} м²" if area else "Дом"
        return house_area

    def _normalize_description(
        self,
        request: SearchRequest,
        source_name: str,
        *,
        title: str,
        raw_description: str | None,
        raw_text: str | None,
        price: float | None,
        area: float | None,
        rooms: int | None,
        district: str | None,
        address: str | None,
        settlement_name: str | None,
        land_area: float | None
    ) -> str:
        location = district or address or settlement_name
        price_text = self._format_price(price)
        cleaned = self._clean_description(raw_description or raw_text or "", title=title)
        if cleaned:
            return cleaned

        if request.propertyType == "house":
            parts = [f"{title}."]
            if land_area:
                parts.append(f"Участок {land_area} соток.")
            if price_text:
                parts.append(f"Цена {price_text}.")
            parts.append(f"Источник: {source_name}.")
            return " ".join(parts)

        parts = [f"{title}."]
        if location:
            parts.append(f"Локация: {location}.")
        if area:
            parts.append(f"Площадь {area} м².")
        if rooms is not None:
            parts.append(f"{'Студия' if rooms == 0 else f'{rooms} комн.'}.")
        if price_text:
            parts.append(f"Цена {price_text}.")
        parts.append(f"Источник: {source_name}.")
        return " ".join(parts)

    def _clean_description(self, value: str, *, title: str) -> str | None:
        text = clean_text(value)
        if not text:
            return None
        lowered = text.lower()
        if any(marker in lowered for marker in BAD_DESCRIPTION_MARKERS):
            return None
        if any(phrase in lowered for phrase in BAD_DESCRIPTION_PHRASES):
            return None
        if re.search(r"\+?\d[\d\-\s()]{9,}", text):
            return None

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[•·|]+", ". ", text)
        text = re.sub(r"\b\d+\s*от\s*\d+[,\d\s]*₽", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\bот\s*\d+[,\d\s]*₽", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b\d+\s*(?:квартир|объектов|предложений)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*[—–-]\s*", " — ", text)
        text = re.sub(r"([.,!?]){2,}", r"\1", text)
        text = re.sub(r"\s+([.,!?])", r"\1", text)

        sentences = re.split(r"(?<=[.!?])\s+", text)
        kept: list[str] = []
        title_lower = title.lower()
        for sentence in sentences:
            clean_sentence = clean_text(sentence.strip(" ."))
            lowered_sentence = clean_sentence.lower()
            if len(clean_sentence) < 30:
                continue
            if len(re.findall(r"\d", clean_sentence)) > max(10, len(clean_sentence) // 3):
                continue
            if any(marker in lowered_sentence for marker in BAD_DESCRIPTION_MARKERS):
                continue
            if any(phrase in lowered_sentence for phrase in BAD_DESCRIPTION_PHRASES):
                continue
            if title_lower and lowered_sentence == title_lower:
                continue
            kept.append(clean_sentence)
            if len(" ".join(kept)) >= 260:
                break

        description = " ".join(kept).strip()
        if not description:
            return None
        if not description.endswith((".", "!", "?")):
            description += "."
        return description[:320]

    def _extract_complex_name(self, text: str, property_type: str) -> str | None:
        patterns = [
            r"(?:жк|жилой комплекс)\s*[«\"]?([^»\"\n,.]{2,80})",
            r"(?:кп|коттеджный поселок|коттеджный пос[её]лок)\s*[«\"]?([^»\"\n,.]{2,80})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = clean_text(match.group(1))
                if name and not any(marker in name.lower() for marker in BAD_TITLE_MARKERS):
                    return name
        if property_type == "apartment":
            quoted = re.search(r"жк\s*[«\"]([^»\"]+)[»\"]", text, re.IGNORECASE)
            if quoted:
                return clean_text(quoted.group(1))
        return None

    def _extract_district(self, text: str) -> str | None:
        lowered = text.lower()
        for district, aliases in DISTRICT_ALIASES:
            if any(re.search(rf"(^|[^а-яa-z]){re.escape(alias)}([^а-яa-z]|$)", lowered) for alias in aliases):
                return district
        return None

    def _extract_address(self, text: str) -> str | None:
        match = re.search(r"(ул\.?\s+[А-ЯA-ZЁ][^,;.]{2,60})", text, re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
        return None

    def _extract_settlement_name(self, text: str, property_type: str) -> str | None:
        if property_type != "house":
            return None
        match = re.search(r"(?:кп|коттеджный поселок|коттеджный пос[её]лок)\s*[«\"]?([^»\"\n,.]{2,80})", text, re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
        if "немецк" in text.lower():
            return "Немецкая деревня"
        return None

    def _parse_land_area(self, text: str) -> float | None:
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*сот", text.lower())
        if not match:
            return None
        return float(match.group(1).replace(",", "."))

    def _is_krasnodar_city(self, text: str, url: str) -> bool:
        lowered = clean_text(text).lower()
        lowered_url = url.lower()
        if any(locality in lowered for locality in EXCLUDED_KRAI_LOCALITIES):
            return False
        if any(re.search(pattern, lowered) for pattern in KRASNODAR_CITY_PATTERNS):
            return True
        if self._extract_district(text):
            return True
        return any(marker in lowered_url for marker in KRASNODAR_URL_MARKERS)

    def _parse_floor(self, text: str) -> tuple[int | None, int | None]:
        lowered = text.lower()
        match = re.search(r"(?<!\d)(\d{1,2})\s*/\s*(\d{1,2})\s*эт", lowered)
        if match:
            return int(match.group(1)), int(match.group(2))
        match = re.search(r"этаж\s*(\d{1,2})\s*(?:из|/)\s*(\d{1,2})", lowered)
        if match:
            return int(match.group(1)), int(match.group(2))
        match = re.search(r"(\d{1,2})\s*этаж(?:\s*из\s*(\d{1,2}))?", lowered)
        if match:
            floor = int(match.group(1))
            total = int(match.group(2)) if match.group(2) else None
            return floor, total
        match = re.search(r"(\d{1,2})\s*-\s*(\d{1,2})\s*этаж", lowered)
        if match:
            return None, int(match.group(2))
        match = re.search(r"(\d{1,2})\s*этажа?", lowered)
        if match:
            return None, int(match.group(1))
        return None, None

    def _parse_finishing(self, text: str) -> str | None:
        lowered = text.lower()
        if "white box" in lowered or "предчист" in lowered:
            return "предчистовая"
        if "чистовая" in lowered or "с отделкой" in lowered or "ремонт" in lowered:
            return "с отделкой"
        if "без отделки" in lowered:
            return "без отделки"
        return None

    def _parse_bedrooms(self, text: str) -> int | None:
        match = re.search(r"([1-8])\s*спаль", text.lower())
        return int(match.group(1)) if match else None

    def _parse_house_floors(self, text: str) -> int | None:
        lowered = text.lower()
        match = re.search(r"([1-4])\s*(?:этажа?|уровн)", lowered)
        return int(match.group(1)) if match else None

    def _parse_house_material(self, text: str) -> str | None:
        lowered = text.lower()
        materials = (
            ("монолит-кирпич", ("монолит-кирпич", "монолит кирпич")),
            ("кирпич", ("кирпич", "кирпичный")),
            ("монолит", ("монолит", "монолитный")),
            ("газобетон", ("газобетон", "газоблок")),
            ("керамический блок", ("керамический блок", "керамоблок")),
            ("каркас", ("каркас", "каркасный")),
        )
        for label, markers in materials:
            if any(marker in lowered for marker in markers):
                return label
        return None

    def _parse_communications(self, text: str) -> list[str]:
        lowered = text.lower()
        communications: list[str] = []
        for label, markers in (
            ("газ", ("газ", "газифиц")),
            ("электричество", ("электричество", "свет", "эл-во")),
            ("вода", ("вода", "водоснабжение")),
            ("канализация", ("канализация", "септик")),
        ):
            if any(marker in lowered for marker in markers):
                communications.append(label)
        return communications

    def _prefixed_project_name(self, value: str | None, prefix: str) -> str | None:
        if not value:
            return None
        cleaned = value.strip().strip("\"«»")
        return f"{prefix} «{cleaned}»"

    def _format_price(self, value: float | None) -> str | None:
        if value is None:
            return None
        return f"{int(value):,} ₽".replace(",", " ")

    def _external_id(self, value: str) -> str:
        digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
        return f"{self.config.adapter_key}:{digest}"
