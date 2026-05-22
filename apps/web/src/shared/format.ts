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
  "каталог",
  "выгода",
  "подарки",
  "вип"
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

function normalizeRoomCount(value?: number | null) {
  if (value === null || value === undefined) {
    return null;
  }
  if (value < 0 || value > 8) {
    return null;
  }
  return value;
}

function looksLikeBadDescription(value?: string | null) {
  const text = value?.trim().toLowerCase();
  if (!text) {
    return true;
  }
  if (BAD_PROPERTY_TITLES.some((item) => text.includes(item))) {
    return true;
  }
  if (["контакты", "заказать звонок", "позвоните", "звоните", "в продаже", "подобрать", "каталог"].some((item) => text.includes(item))) {
    return true;
  }
  if (/\+?\d[\d\s()\-]{9,}/.test(text)) {
    return true;
  }
  return false;
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

function extractProjectFromTitle(value?: string | null, type: Property["propertyType"] = "apartment") {
  if (!value) {
    return null;
  }
  const patterns = type === "house"
    ? [/(?:кп|коттеджный поселок|коттеджный пос[её]лок)\s*[«"]([^»"]+)[»"]/i]
    : [/(?:жк|жилой комплекс)\s*[«"]([^»"]+)[»"]/i];
  for (const pattern of patterns) {
    const match = value.match(pattern);
    if (match?.[1]) {
      return match[1].trim();
    }
  }
  return null;
}

function extractDistrictFromTitle(value?: string | null) {
  if (!value) {
    return null;
  }
  const districts = ["Прикубанский", "Центральный", "Карасунский", "Западный", "Фестивальный", "Юбилейный"];
  return districts.find((district) => value.toLowerCase().includes(district.toLowerCase())) ?? null;
}

function extractAddressFromTitle(value?: string | null) {
  if (!value) {
    return null;
  }
  const match = value.match(/(ул\.?\s+[А-ЯA-ZЁ][^,;]+)/i);
  return match?.[1]?.trim() ?? null;
}

export function propertyTitle(property: Property) {
  const rooms = normalizeRoomCount(property.rooms);

  if (property.propertyType === "house") {
    return property.houseArea ? `Дом ${property.houseArea} м²` : "Дом";
  }

  const roomsLabel = rooms === 0
    ? "Студия"
    : rooms
      ? `${rooms}-к квартира`
      : "Квартира";
  const area = property.area ? `, ${property.area} м²` : "";
  return `${roomsLabel}${area}`.trim().replace(/,$/, "");
}

export function propertyDistrictLabel(property: Property) {
  return property.district
    || extractDistrictFromTitle(property.title)
    || extractDistrictFromTitle(property.description)
    || null;
}

export function propertySourceLabel(property: Property) {
  return property.developerName || property.sourceName || "Источник не указан";
}

export function propertyMeta(property: Property) {
  const rooms = normalizeRoomCount(property.rooms);
  const district = propertyDistrictLabel(property);
  if (property.propertyType === "house") {
    return [
      property.houseArea ? `Дом ${property.houseArea} м²` : null,
      property.landArea ? `участок ${property.landArea} сот.` : null,
      district ? `район ${district}` : null,
      property.settlementName ? wrapProjectName("в КП", property.settlementName) : null
    ].filter(Boolean).join(" · ");
  }

  return [
    rooms === 0 ? "студия" : rooms ? `${rooms}-комн.` : null,
    property.area ? `${property.area} м²` : null,
    district ? `район ${district}` : shortAddress(property.address)
  ].filter(Boolean).join(" · ");
}

export function propertyDescription(property: Property) {
  const rooms = normalizeRoomCount(property.rooms);
  const district = propertyDistrictLabel(property);
  if (property.description && !looksLikeBadDescription(property.description)) {
    const description = property.description.trim();
    if (district && !description.toLowerCase().includes(district.toLowerCase())) {
      return `Район ${district}. ${description}`;
    }
    return description;
  }

  if (property.propertyType === "house") {
    return [
      propertyTitle(property) ? `${propertyTitle(property)}.` : null,
      district ? `Район ${district}.` : null,
      property.settlementName ? `Локация: ${property.settlementName}.` : null,
      property.landArea ? `Участок ${formatLand(property.landArea)}.` : null,
      property.price ? `Цена ${formatMoney(property.price)}.` : null,
      `Источник: ${propertySourceLabel(property)}.`
    ].filter(Boolean).join(" ");
  }

  return [
    propertyTitle(property) ? `${propertyTitle(property)}.` : null,
    district ? `Район ${district}.` : null,
    property.area ? `Площадь ${formatArea(property.area)}.` : null,
    rooms !== null
      ? `${rooms === 0 ? "Студия" : `${rooms}-комнатная квартира`}.`
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
