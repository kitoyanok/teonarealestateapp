import { Router } from "express";
import { requireAuth } from "../middleware/auth.js";
import {
  addToShortlist,
  createClientWithProfile,
  createShareMessage,
  deleteClient,
  getClientAccess,
  getClientDetails,
  getFoundProperties,
  getFoundProperty,
  getShortlist,
  listClients,
  markSent,
  removeFromShortlist,
  updateClientWithProfile
} from "../repositories/sql.js";
import { buildShareMessage } from "../services/messageService.js";
import { runClientSearch } from "../services/searchService.js";
import { serialize } from "../services/serializers.js";
import { clientSchema } from "../services/validation.js";

export const clientsRouter = Router();

clientsRouter.use(requireAuth);

type ClientDetails = {
  id: string;
  name: string;
  propertyType: "apartment" | "house";
  sendChannel: string;
  sendContact?: string | null;
  shortlistItems: Array<{
    property: {
      sourceUrl: string;
      title?: string | null;
      complexName?: string | null;
      settlementName?: string | null;
      houseArea?: number | string | null;
      landArea?: number | string | null;
      price?: number | string | null;
      rooms?: number | string | null;
      area?: number | string | null;
    };
  }>;
};

function profileData(input: ReturnType<typeof clientSchema.parse>["searchProfile"]) {
  return {
    budgetMin: input.budgetMin,
    budgetMax: input.budgetMax,
    roomsMin: input.roomsMin,
    roomsMax: input.roomsMax,
    areaMin: input.areaMin,
    areaMax: input.areaMax,
    districts: input.districts,
    settlementNames: input.settlementNames,
    completionYearMin: input.completionYearMin,
    completionYearMax: input.completionYearMax,
    finishing: input.finishing || null,
    floorMin: input.floorMin,
    floorMax: input.floorMax,
    houseAreaMin: input.houseAreaMin,
    houseAreaMax: input.houseAreaMax,
    landAreaMin: input.landAreaMin,
    landAreaMax: input.landAreaMax,
    floorsCountMin: input.floorsCountMin,
    floorsCountMax: input.floorsCountMax,
    bedroomsMin: input.bedroomsMin,
    bedroomsMax: input.bedroomsMax,
    houseMaterial: input.houseMaterial || null,
    communications: input.communications
  };
}

function dbPayload(input: ReturnType<typeof clientSchema.parse>) {
  return {
    name: input.name,
    phone: input.phone,
    email: input.email || null,
    sendChannel: input.sendChannel,
    sendContact: input.sendContact || null,
    propertyType: input.propertyType,
    comment: input.comment || null,
    searchProfile: profileData(input.searchProfile)
  };
}

async function assertClientAccess(clientId: string, realtorId: string) {
  const client = await getClientAccess(clientId, realtorId);
  if (!client) {
    const error = new Error("Client not found");
    (error as Error & { status?: number }).status = 404;
    throw error;
  }
  return client;
}

clientsRouter.get("/", async (req, res, next) => {
  try {
    const search = String(req.query.search ?? "").trim();
    const status = String(req.query.status ?? "").trim();
    const clients = await listClients(req.userId!, search, status);
    res.json(serialize(clients));
  } catch (error) {
    next(error);
  }
});

clientsRouter.post("/", async (req, res, next) => {
  try {
    const input = clientSchema.parse(req.body);
    const clientRef = await createClientWithProfile(req.userId!, dbPayload(input));
    const searchResult = await runClientSearch(clientRef.id, req.userId!);
    const client = await getClientDetails(clientRef.id, req.userId!);
    res.status(201).json(serialize({ client, searchResult }));
  } catch (error) {
    next(error);
  }
});

clientsRouter.get("/:id", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const client = (await getClientDetails(req.params.id, req.userId!)) as ClientDetails | null;
    res.json(serialize(client));
  } catch (error) {
    next(error);
  }
});

clientsRouter.put("/:id", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const input = clientSchema.parse(req.body);
    await updateClientWithProfile(req.params.id, dbPayload(input));
    const client = (await getClientDetails(req.params.id, req.userId!)) as ClientDetails | null;
    res.json(serialize(client));
  } catch (error) {
    next(error);
  }
});

clientsRouter.delete("/:id", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    await deleteClient(req.params.id);
    res.json({ ok: true });
  } catch (error) {
    next(error);
  }
});

clientsRouter.post("/:id/search", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const result = await runClientSearch(req.params.id, req.userId!);
    const client = (await getClientDetails(req.params.id, req.userId!)) as ClientDetails | null;
    res.json(serialize({ client, result }));
  } catch (error) {
    next(error);
  }
});

clientsRouter.get("/:id/found-properties", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const found = await getFoundProperties(req.params.id);
    res.json(serialize(found));
  } catch (error) {
    next(error);
  }
});

clientsRouter.get("/:id/shortlist", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const shortlist = await getShortlist(req.params.id);
    res.json(serialize(shortlist));
  } catch (error) {
    next(error);
  }
});

clientsRouter.post("/:id/shortlist/:propertyId", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const found = await getFoundProperty(req.params.id, req.params.propertyId);
    if (!found) {
      return res.status(404).json({ message: "Property was not found for this client" });
    }

    const item = await addToShortlist(req.params.id, req.params.propertyId);
    res.status(201).json(serialize(item));
  } catch (error) {
    next(error);
  }
});

clientsRouter.delete("/:id/shortlist/:propertyId", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    await removeFromShortlist(req.params.id, req.params.propertyId);
    res.json({ ok: true });
  } catch (error) {
    next(error);
  }
});

clientsRouter.post("/:id/share-message", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const client = (await getClientDetails(req.params.id, req.userId!)) as ClientDetails | null;
    if (!client) {
      return res.status(404).json({ message: "Client not found" });
    }
    if (client.shortlistItems.length === 0) {
      return res.status(400).json({ message: "Подборка пока пустая" });
    }

    const messageText = buildShareMessage(client, client.shortlistItems);
    const shareMessage = await createShareMessage(client.id, client.sendChannel, client.sendContact ?? null, messageText);
    res.json(serialize({ messageText, shareMessage }));
  } catch (error) {
    next(error);
  }
});

clientsRouter.post("/:id/mark-sent", async (req, res, next) => {
  try {
    await assertClientAccess(req.params.id, req.userId!);
    const client = await markSent(req.params.id);
    res.json(serialize(client));
  } catch (error) {
    next(error);
  }
});
