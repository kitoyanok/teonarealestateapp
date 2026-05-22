import re


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def parse_price(value: str) -> float | None:
    text = value.lower().replace("\xa0", " ")
    match = re.search(r"(\d[\d\s.,]{2,})\s*(млн|миллион|₽|руб)", text)
    if not match:
        return None
    raw = match.group(1).replace(" ", "").replace(",", ".")
    try:
        number = float(raw)
    except ValueError:
        return None
    unit = match.group(2)
    if unit.startswith("млн") or unit.startswith("миллион"):
        return number * 1_000_000
    return number


def parse_area(value: str) -> float | None:
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м2|м²|кв\.?\s*м)", value.lower())
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def parse_rooms(value: str) -> int | None:
    text = value.lower()
    if "студ" in text:
        return 0
    patterns = [
        r"\b(\d)\s*[- ]?к\b",
        r"\b(\d)\s*[- ]?комн",
        r"\b(\d)\s*[- ]?комнат",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            rooms = int(match.group(1))
            return rooms if 0 <= rooms <= 8 else None
    return None


def extract_year(value: str) -> int | None:
    match = re.search(r"\b(20[2-4]\d)\b", value)
    return int(match.group(1)) if match else None
