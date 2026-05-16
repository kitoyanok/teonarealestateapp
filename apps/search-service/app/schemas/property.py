from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    clientId: str
    propertyType: Literal["apartment", "house"]
    budgetMin: float | None = None
    budgetMax: float | None = None
    roomsMin: int | None = None
    roomsMax: int | None = None
    areaMin: float | None = None
    areaMax: float | None = None
    districts: list[str] = Field(default_factory=list)
    settlementNames: list[str] = Field(default_factory=list)
    completionYearMin: int | None = None
    completionYearMax: int | None = None
    finishing: str | None = None
    floorMin: int | None = None
    floorMax: int | None = None
    houseAreaMin: float | None = None
    houseAreaMax: float | None = None
    landAreaMin: float | None = None
    landAreaMax: float | None = None
    floorsCountMin: int | None = None
    floorsCountMax: int | None = None
    bedroomsMin: int | None = None
    bedroomsMax: int | None = None
    houseMaterial: str | None = None
    communications: list[str] = Field(default_factory=list)


class PropertyItem(BaseModel):
    externalId: str | None = None
    sourceName: str
    sourceUrl: str
    propertyType: Literal["apartment", "house"]
    title: str
    complexName: str | None = None
    developerName: str | None = None
    description: str | None = None
    city: str | None = "Краснодар"
    district: str | None = None
    address: str | None = None
    settlementName: str | None = None
    price: float | None = None
    pricePerMeter: float | None = None
    area: float | None = None
    rooms: int | None = None
    floor: int | None = None
    floorsTotal: int | None = None
    houseArea: float | None = None
    landArea: float | None = None
    bedrooms: int | None = None
    houseFloors: int | None = None
    houseMaterial: str | None = None
    communications: list[str] = Field(default_factory=list)
    completionYear: int | None = None
    finishing: str | None = None
    images: list[str] = Field(default_factory=list)
    rawData: dict[str, Any] | None = None
    matchScore: int | None = None
    matchReasons: list[str] = Field(default_factory=list)
    mismatchReasons: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    status: Literal["ok", "error"]
    totalFound: int = 0
    items: list[PropertyItem] = Field(default_factory=list)
    error: str | None = None
