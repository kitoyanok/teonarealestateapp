type ShareClient = {
  name: string;
  propertyType: "apartment" | "house";
};

type ShareProperty = {
  title?: string | null;
  complexName?: string | null;
  settlementName?: string | null;
  houseArea?: number | string | null;
  landArea?: number | string | null;
  price?: number | string | null;
  rooms?: number | string | null;
  area?: number | string | null;
  sourceUrl: string;
};

type ShortlistWithProperty = {
  property: ShareProperty;
};

const formatRub = (value?: unknown) => {
  const number = Number(value ?? 0);
  if (!number) {
    return "цена по запросу";
  }
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(number);
};

const firstName = (name: string) => name.trim().split(/\s+/)[0] ?? name;

export function buildShareMessage(client: ShareClient, shortlist: ShortlistWithProperty[]) {
  const greetingName = firstName(client.name);
  const isHouse = client.propertyType === "house";
  const intro = isHouse ? "несколько домов" : "несколько вариантов";

  const lines = [
    `${greetingName}, добрый день!`,
    "",
    `Подобрал для вас ${intro}:`,
    ""
  ];

  shortlist.forEach((item, index) => {
    const property = item.property;
    const title = property.title || property.complexName || property.settlementName || "Объект недвижимости";
    const details = isHouse
      ? [
          property.houseArea ? `${Number(property.houseArea)} м²` : null,
          property.landArea ? `участок ${Number(property.landArea)} соток` : null,
          formatRub(property.price)
        ].filter(Boolean).join(", ")
      : [
          property.rooms ? `${property.rooms}-комн.` : null,
          property.area ? `${Number(property.area)} м²` : null,
          formatRub(property.price)
        ].filter(Boolean).join(", ");

    lines.push(`${index + 1}. ${title}`);
    lines.push(details);
    lines.push(`Ссылка: ${property.sourceUrl}`);
    lines.push("");
  });

  lines.push("Если какой-то вариант понравится, можем подробнее разобрать условия.");
  return lines.join("\n");
}
