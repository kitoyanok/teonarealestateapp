"""Этот файл управляет общим процессом поиска по источникам.
Проще говоря: он запускает адаптеры, собирает результаты, убирает дубликаты и сортирует объявления по релевантности."""

import asyncio

import httpx

from app.adapters.sources import build_adapters
from app.schemas.property import PropertyItem, SearchRequest
from app.services.matcher import score_property


def _passes_required_filters(item: PropertyItem, request: SearchRequest) -> bool:
    if item.price is None:
        return False
    if request.budgetMin is not None and item.price < request.budgetMin:
        return False
    if request.budgetMax is not None and item.price > request.budgetMax * 1.08:
        return False
    return True


async def run_search(request: SearchRequest) -> list[PropertyItem]:
    timeout = httpx.Timeout(12.0, connect=5.0)
    headers = {
        "User-Agent": "EstateFlowBot/0.1 (+https://localhost; realtor CRM live search)",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7"
    }

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        adapters = build_adapters(request.propertyType)
        results = await asyncio.gather(
            *(adapter.search(client, request) for adapter in adapters),
            return_exceptions=True
        )

    items: list[PropertyItem] = []
    for result in results:
        if isinstance(result, Exception):
            continue
        items.extend(result)

    unique: dict[str, PropertyItem] = {}
    for item in items:
        if _passes_required_filters(item, request):
            unique[item.sourceUrl] = score_property(item, request)

    return sorted(unique.values(), key=lambda item: item.matchScore or 0, reverse=True)[:80]
