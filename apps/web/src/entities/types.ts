// Здесь описаны типы данных frontend.
// Проще говоря: файл подсказывает коду, как выглядит пользователь, клиент, объект недвижимости и другие сущности.

export type User = {
  id: string;
  login: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
};

export type PropertyType = "apartment" | "house";
export type SendChannel = "max" | "telegram" | "whatsapp" | "email" | "copy";

export type SearchProfile = {
  id: string;
  clientId: string;
  budgetMin?: number | null;
  budgetMax?: number | null;
  roomsMin?: number | null;
  roomsMax?: number | null;
  areaMin?: number | null;
  areaMax?: number | null;
  districts: string[];
  settlementNames: string[];
  completionYearMin?: number | null;
  completionYearMax?: number | null;
  finishing?: string | null;
  floorMin?: number | null;
  floorMax?: number | null;
  houseAreaMin?: number | null;
  houseAreaMax?: number | null;
  landAreaMin?: number | null;
  landAreaMax?: number | null;
  floorsCountMin?: number | null;
  floorsCountMax?: number | null;
  bedroomsMin?: number | null;
  bedroomsMax?: number | null;
  houseMaterial?: string | null;
  communications: string[];
};

export type Property = {
  id: string;
  externalId?: string | null;
  sourceName?: string | null;
  sourceUrl: string;
  propertyType: PropertyType;
  title?: string | null;
  complexName?: string | null;
  developerName?: string | null;
  description?: string | null;
  city?: string | null;
  district?: string | null;
  address?: string | null;
  settlementName?: string | null;
  price?: number | null;
  pricePerMeter?: number | null;
  area?: number | null;
  rooms?: number | null;
  floor?: number | null;
  floorsTotal?: number | null;
  houseArea?: number | null;
  landArea?: number | null;
  bedrooms?: number | null;
  houseFloors?: number | null;
  houseMaterial?: string | null;
  communications: string[];
  completionYear?: number | null;
  finishing?: string | null;
  images: string[];
};

export type FoundProperty = {
  id: string;
  clientId: string;
  propertyId: string;
  matchScore?: number | null;
  matchReasons: string[];
  mismatchReasons: string[];
  isHidden: boolean;
  createdAt: string;
  property: Property;
};

export type ShortlistItem = {
  id: string;
  clientId: string;
  propertyId: string;
  createdAt: string;
  property: Property;
};

export type SearchRun = {
  id: string;
  status: string;
  totalFound: number;
  totalSaved: number;
  errorMessage?: string | null;
  startedAt: string;
  finishedAt?: string | null;
};

export type Client = {
  id: string;
  name: string;
  phone?: string | null;
  email?: string | null;
  sendChannel: SendChannel;
  sendContact?: string | null;
  status: string;
  propertyType: PropertyType;
  comment?: string | null;
  createdAt: string;
  updatedAt: string;
  searchProfile?: SearchProfile | null;
  foundProperties?: FoundProperty[];
  shortlistItems?: ShortlistItem[];
  searchRuns?: SearchRun[];
  _count?: {
    foundProperties: number;
    shortlistItems: number;
  };
};

export type DashboardSummary = {
  clientsInWork: number;
  foundObjects: number;
  shortlistItems: number;
  readyToSend: number;
};

export type ActivityPoint = {
  key: string;
  label: string;
  clients: number;
  found: number;
  shortlisted: number;
  sent: number;
  ready: number;
};
