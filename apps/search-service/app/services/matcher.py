from app.schemas.property import PropertyItem, SearchRequest


def _inside_min_max(value: float | int | None, minimum: float | int | None, maximum: float | int | None) -> bool:
    if value is None:
        return False
    if minimum is not None and value < minimum:
        return False
    if maximum is not None and value > maximum:
        return False
    return True


def _text_match(value: str | None, variants: list[str]) -> bool:
    if not value or not variants:
        return False
    text = value.lower()
    return any(item.lower() in text for item in variants if item)


def score_property(item: PropertyItem, request: SearchRequest) -> PropertyItem:
    score = 0
    reasons: list[str] = []
    mismatches: list[str] = []

    if item.propertyType == "apartment":
        if _inside_min_max(item.price, request.budgetMin, request.budgetMax):
            score += 30
            reasons.append("Цена подходит")
        elif item.price and request.budgetMax and item.price > request.budgetMax:
            mismatches.append(f"Цена выше бюджета на {int(item.price - request.budgetMax):,} ₽".replace(",", " "))

        if _inside_min_max(item.rooms, request.roomsMin, request.roomsMax):
            score += 20
            reasons.append("Комнатность подходит")

        if _inside_min_max(item.area, request.areaMin, request.areaMax):
            score += 15
            reasons.append("Площадь подходит")

        if _text_match(item.district, request.districts) or _text_match(item.address, request.districts):
            score += 20
            reasons.append("Район подходит")
        elif not request.districts:
            score += 12

        if _inside_min_max(item.completionYear, request.completionYearMin, request.completionYearMax):
            score += 10
            reasons.append("Срок сдачи подходит")
        elif request.completionYearMin is None and request.completionYearMax is None:
            score += 6

        if request.finishing and item.finishing and request.finishing.lower() in item.finishing.lower():
            score += 5
            reasons.append("Отделка подходит")
        elif not request.finishing:
            score += 3
    else:
        if _inside_min_max(item.price, request.budgetMin, request.budgetMax):
            score += 30
            reasons.append("Цена подходит")
        elif item.price and request.budgetMax and item.price > request.budgetMax:
            mismatches.append(f"Цена выше бюджета на {int(item.price - request.budgetMax):,} ₽".replace(",", " "))

        if _inside_min_max(item.houseArea, request.houseAreaMin, request.houseAreaMax):
            score += 15
            reasons.append("Площадь дома подходит")

        if _inside_min_max(item.landArea, request.landAreaMin, request.landAreaMax):
            score += 15
            reasons.append("Участок подходит")

        location_variants = request.settlementNames or request.districts
        if _text_match(item.settlementName, location_variants) or _text_match(item.address, location_variants):
            score += 20
            reasons.append("Локация подходит")
        elif not location_variants:
            score += 12

        matched_communications = [name for name in request.communications if name.lower() in " ".join(item.communications).lower()]
        if request.communications and matched_communications:
            score += min(10, int(10 * len(matched_communications) / len(request.communications)))
            reasons.append("Коммуникации подходят")
        elif not request.communications:
            score += 6

        floors_ok = _inside_min_max(item.houseFloors, request.floorsCountMin, request.floorsCountMax)
        bedrooms_ok = _inside_min_max(item.bedrooms, request.bedroomsMin, request.bedroomsMax)
        if floors_ok or bedrooms_ok:
            score += 10
            reasons.append("Этажность или спальни подходят")

    item.matchScore = max(0, min(100, score))
    item.matchReasons = reasons
    item.mismatchReasons = mismatches
    return item
