import type { Client, Property, SearchProfile, SendChannel } from "../entities/types";

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

export function propertyTitle(property: Property) {
  return property.title || property.complexName || property.settlementName || "Объект недвижимости";
}

export function propertyMeta(property: Property) {
  if (property.propertyType === "house") {
    return [
      property.houseArea ? `${property.houseArea} м²` : null,
      property.landArea ? `участок ${property.landArea} сот.` : null,
      property.houseFloors ? `${property.houseFloors} эт.` : null
    ].filter(Boolean).join(" · ");
  }

  return [
    property.rooms === 0 ? "студия" : property.rooms ? `${property.rooms}-комн.` : null,
    property.area ? `${property.area} м²` : null,
    property.floor && property.floorsTotal ? `${property.floor}/${property.floorsTotal} этаж` : null
  ].filter(Boolean).join(" · ");
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
