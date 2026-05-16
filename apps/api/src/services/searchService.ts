import {
  createSearchRun,
  failSearchRun,
  finishSearchRun,
  getClientForSearch,
  updateClientStatus,
  upsertClientFoundProperty,
  upsertProperty
} from "../repositories/sql.js";
import { config } from "../config.js";

type SearchItem = {
  externalId?: string;
  sourceName?: string;
  sourceUrl: string;
  propertyType: "apartment" | "house";
  title?: string;
  complexName?: string;
  developerName?: string;
  description?: string;
  city?: string;
  district?: string;
  address?: string;
  settlementName?: string;
  price?: number;
  pricePerMeter?: number;
  area?: number;
  rooms?: number;
  floor?: number;
  floorsTotal?: number;
  houseArea?: number;
  landArea?: number;
  bedrooms?: number;
  houseFloors?: number;
  houseMaterial?: string;
  communications?: string[];
  completionYear?: number;
  finishing?: string;
  images?: string[];
  rawData?: unknown;
  matchScore?: number;
  matchReasons?: string[];
  mismatchReasons?: string[];
};

type SearchResponse = {
  status: "ok" | "error";
  totalFound: number;
  items: SearchItem[];
  error?: string;
};

type SearchClient = {
  id: string;
  propertyType: "apartment" | "house";
  searchProfile: Record<string, unknown> | null;
};

type SearchRunRef = {
  id: string;
};

type PropertyRef = {
  id: string;
};

const numeric = (value: unknown) => {
  if (value === null || value === undefined || value === "") {
    return undefined;
  }
  return Number(value);
};

function buildSearchRequest(client: SearchClient, profile: Record<string, unknown>) {
  return {
    clientId: client.id,
    propertyType: client.propertyType,
    budgetMin: numeric(profile.budgetMin),
    budgetMax: numeric(profile.budgetMax),
    roomsMin: profile.roomsMin ?? undefined,
    roomsMax: profile.roomsMax ?? undefined,
    areaMin: numeric(profile.areaMin),
    areaMax: numeric(profile.areaMax),
    districts: profile.districts ?? [],
    settlementNames: profile.settlementNames ?? [],
    completionYearMin: profile.completionYearMin ?? undefined,
    completionYearMax: profile.completionYearMax ?? undefined,
    finishing: profile.finishing ?? undefined,
    floorMin: profile.floorMin ?? undefined,
    floorMax: profile.floorMax ?? undefined,
    houseAreaMin: numeric(profile.houseAreaMin),
    houseAreaMax: numeric(profile.houseAreaMax),
    landAreaMin: numeric(profile.landAreaMin),
    landAreaMax: numeric(profile.landAreaMax),
    floorsCountMin: profile.floorsCountMin ?? undefined,
    floorsCountMax: profile.floorsCountMax ?? undefined,
    bedroomsMin: profile.bedroomsMin ?? undefined,
    bedroomsMax: profile.bedroomsMax ?? undefined,
    houseMaterial: profile.houseMaterial ?? undefined,
    communications: profile.communications ?? []
  };
}

function cleanItem(item: SearchItem) {
  return {
    externalId: item.externalId,
    sourceName: item.sourceName,
    sourceUrl: item.sourceUrl,
    propertyType: item.propertyType,
    title: item.title,
    complexName: item.complexName,
    developerName: item.developerName,
    description: item.description,
    city: item.city,
    district: item.district,
    address: item.address,
    settlementName: item.settlementName,
    price: item.price,
    pricePerMeter: item.pricePerMeter,
    area: item.area,
    rooms: item.rooms,
    floor: item.floor,
    floorsTotal: item.floorsTotal,
    houseArea: item.houseArea,
    landArea: item.landArea,
    bedrooms: item.bedrooms,
    houseFloors: item.houseFloors,
    houseMaterial: item.houseMaterial,
    communications: item.communications ?? [],
    completionYear: item.completionYear,
    finishing: item.finishing,
    images: item.images ?? [],
    rawData: item.rawData === undefined ? undefined : (item.rawData as object)
  };
}

export async function runClientSearch(clientId: string, realtorId: string) {
  const client = (await getClientForSearch(clientId, realtorId)) as SearchClient | null;
  if (!client || !client.searchProfile) {
    throw new Error("Client search profile not found");
  }

  const searchRun = (await createSearchRun(client.id, client.propertyType)) as SearchRunRef;
  await updateClientStatus(client.id, "searching");

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    const response = await fetch(`${config.searchServiceUrl}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildSearchRequest(client, client.searchProfile)),
      signal: controller.signal
    });
    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`Search service returned ${response.status}`);
    }

    const payload = (await response.json()) as SearchResponse;
    if (payload.status !== "ok") {
      throw new Error(payload.error ?? "Search service error");
    }

    let saved = 0;
    for (const item of payload.items.filter((property) => property.sourceUrl)) {
      const property = (await upsertProperty(cleanItem(item))) as PropertyRef;
      await upsertClientFoundProperty(client.id, property.id, item);
      saved += 1;
    }

    const status = saved > 0 ? "found" : "no_results";
    await finishSearchRun(searchRun.id, payload.totalFound, saved);
    await updateClientStatus(client.id, status);

    return { totalFound: payload.totalFound, totalSaved: saved, status };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown search error";
    await failSearchRun(searchRun.id, message);
    await updateClientStatus(client.id, "error");
    return { totalFound: 0, totalSaved: 0, status: "error", error: message };
  }
}
