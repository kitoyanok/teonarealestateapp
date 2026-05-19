import type { Client, Property, SearchProfile, SendChannel } from "../entities/types";

const BAD_PROPERTY_TITLES = [
  "все новостройки",
  "избранное",
  "кабинет",
  "отзывы",
  "отзывов",
  "старт продаж",
  "скоро в продаже",
  "недорогие",
  "комфорт",
  "бизнес",
  "главная",
  "каталог"
];

export const formatMoney = (value?: number | null) => {
  if (!value) {
    return "цена по запросу";
  }
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);
};

export const formatCompactMoney = (value?: number | null) => {
  if (!value) {
    return "по запросу";
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(value % 1_000_000 ? 1 : 0)} млн ₽`;
  }
  return formatMoney(value);
};

export const channelLabel: Record<SendChannel, string> = {
  max: "MAX",
  telegram: "Telegram",
  whatsapp: "WhatsApp",
  email: "Email",
  copy: "Только скопировать"
};

export const statusLabel: Record<string, string> = {
  new: "В работе",
  searching: "В работе",
  found: "В работе",
  shortlist_ready: "Готово",
  sent: "Отправлено",
  no_results: "Нет объектов",
  error: "Нет объектов",
  closed: "Нет объектов"
};

function isBadTitle(value?: string | null) {
  const text = value?.trim().toLowerCase();
  return !text || BAD_PROPERTY_TITLES.some((item) => text.includes(item));
}

function formatArea(value?: number | null) {
  return value ? `${value} м²` : null;
}

function formatLand(value?: number | null) {
  return value ? `${value} сот.` : null;
}

function wrapProjectName(prefix: string, value?: string | null) {
  if (!value) {
    return null;
  }
  const clean = value.trim().replace(/^["«]|[»"]$/g, "");
  return `${prefix} «${clean}»`;
}

function shortAddress(value?: string | null) {
  if (!value) {
    return null;
  }
  const clean = value.trim();
  const streetMatch = clean.match(/(ул\.?\s+[А-ЯA-ZЁ][^,;]+)/i);
  if (streetMatch?.[1]) {
    return streetMatch[1];
  }
  return clean.split(",")[0] || clean;
}

function propertyLocation(property: Property) {
  if (property.propertyType === "house") {
    return wrapProjectName("в КП", property.settlementName)
      || property.address
      || (property.district ? `в районе ${property.district}` : null)
      || property.sourceName
      || null;
  }

  return wrapProjectName("в ЖК", property.complexName)
    || (shortAddress(property.address) ? `на ${shortAddress(property.address)}` : null)
    || (property.district ? `в районе ${property.district}` : null)
    || property.settlementName
    || null;
}

export function propertyTitle(property: Property) {
  if (!isBadTitle(property.title)) {
    return property.title!.trim();
  }

  if (property.propertyType === "house") {
    const houseArea = property.houseArea ? `Дом ${property.houseArea} м²` : "Дом";
    const land = property.landArea ? `, участок ${property.landArea} сот.` : "";
    const location = propertyLocation(property);
    return `${houseArea}${land}${location ? ` ${location}` : ""}`.trim();
  }

  const roomsLabel = property.rooms === 0
    ? "Студия"
    : property.rooms
      ? `${property.rooms}-к квартира`
      : "Квартира";
  const area = property.area ? `, ${property.area} м²` : "";
  const location = propertyLocation(property);
  return `${roomsLabel}${area}${location ? ` ${location}` : ""}`.trim();
}

export function propertySourceLabel(property: Property) {
  return property.developerName || property.sourceName || "Источник не указан";
}

export function propertyMeta(property: Property) {
  if (property.propertyType === "house") {
    return [
      property.houseArea ? `Дом ${property.houseArea} м²` : null,
      property.landArea ? `участок ${property.landArea} сот.` : null,
      property.settlementName ? wrapProjectName("в КП", property.settlementName) : property.district
    ].filter(Boolean).join(" · ");
  }

  return [
    property.rooms === 0 ? "студия" : property.rooms ? `${property.rooms}-комн.` : null,
    property.area ? `${property.area} м²` : null,
    property.district || shortAddress(property.address)
  ].filter(Boolean).join(" · ");
}

export function propertyDescription(property: Property) {
  if (property.description && !BAD_PROPERTY_TITLES.some((item) => property.description!.toLowerCase().includes(item))) {
    return property.description;
  }

  if (property.propertyType === "house") {
    return [
      propertyTitle(property),
      property.landArea ? `Участок ${formatLand(property.landArea)}.` : null,
      property.price ? `Цена ${formatMoney(property.price)}.` : null,
      `Источник: ${propertySourceLabel(property)}.`
    ].filter(Boolean).join(" ");
  }

  return [
    propertyTitle(property),
    property.district ? `Район ${property.district}.` : null,
    property.area ? `Площадь ${formatArea(property.area)}.` : null,
    property.rooms !== null && property.rooms !== undefined
      ? `${property.rooms === 0 ? "Студия" : `${property.rooms} комната${property.rooms > 1 ? "ы" : ""}`}.`
      : null,
    property.price ? `Цена ${formatMoney(property.price)}.` : null,
    `Источник: ${propertySourceLabel(property)}.`
  ].filter(Boolean).join(" ");
}

export function hasRealPropertyImage(property: Property) {
  return property.images.some((image) => {
    const lowered = image.toLowerCase();
    return !["logo", "favicon", "icon", "sprite", "placeholder", "avatar", "social", "telegram", "vk", "whatsapp"].some((marker) => lowered.includes(marker));
  });
}

export function profileSummary(client: Pick<Client, "propertyType"> & { searchProfile?: SearchProfile | null }) {
  const profile = client.searchProfile;
  if (!profile) {
    return "Параметры не заполнены";
  }

  const budget = profile.budgetMax ? `до ${formatCompactMoney(profile.budgetMax)}` : "бюджет не указан";
  if (client.propertyType === "house") {
    const area = profile.houseAreaMin ? `дом от ${profile.houseAreaMin} м²` : "дом";
    const land = profile.landAreaMin ? `участок от ${profile.landAreaMin} сот.` : "";
    return [budget, area, land].filter(Boolean).join(" · ");
  }

  const rooms = profile.roomsMin || profile.roomsMax
    ? `${profile.roomsMin ?? "студия"}-${profile.roomsMax ?? "4+"} комн.`
    : "комнатность не указана";
  return [budget, rooms].join(" · ");
}
