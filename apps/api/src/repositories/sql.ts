import bcrypt from "bcryptjs";
import type { PoolClient } from "pg";
import { pool, query } from "../db/pool.js";

type ClientPayload = {
  name: string;
  phone: string;
  email?: string | null;
  sendChannel: string;
  sendContact?: string | null;
  propertyType: "apartment" | "house";
  comment?: string | null;
  searchProfile: Record<string, unknown>;
};

const profileColumns = [
  "budget_min",
  "budget_max",
  "rooms_min",
  "rooms_max",
  "area_min",
  "area_max",
  "districts",
  "settlement_names",
  "completion_year_min",
  "completion_year_max",
  "finishing",
  "floor_min",
  "floor_max",
  "house_area_min",
  "house_area_max",
  "land_area_min",
  "land_area_max",
  "floors_count_min",
  "floors_count_max",
  "bedrooms_min",
  "bedrooms_max",
  "house_material",
  "communications"
] as const;

function camelize<T>(value: T): T {
  if (Array.isArray(value)) {
    return value.map(camelize) as T;
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [
        key.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase()),
        camelize(item)
      ])
    ) as T;
  }
  return value;
}

async function withClient<T>(callback: (client: PoolClient) => Promise<T>) {
  const client = await pool.connect();
  try {
    return await callback(client);
  } finally {
    client.release();
  }
}

export async function ensureSeedUser(login: string, password: string) {
  const existing = await query<{ id: string }>("SELECT id FROM users WHERE login = $1 LIMIT 1", [login]);
  if (existing.rowCount) {
    return existing.rows[0];
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const created = await query<{ id: string }>(
    `INSERT INTO users (login, password_hash, name, email, phone)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING id`,
    [login, passwordHash, "Риелтор EstateFlow", "realtor@example.com", "+7 (999) 123-45-67"]
  );
  return created.rows[0];
}

export async function findUserByLogin(login: string) {
  const result = await query(
    `SELECT id, login, password_hash, name, email, phone
     FROM users
     WHERE login = $1
     LIMIT 1`,
    [login]
  );
  return camelize(result.rows[0] ?? null);
}

export async function findUserById(id: string) {
  const result = await query(
    `SELECT id, login, password_hash, name, email, phone
     FROM users
     WHERE id = $1
     LIMIT 1`,
    [id]
  );
  return camelize(result.rows[0] ?? null);
}

export async function getClientAccess(clientId: string, realtorId: string) {
  const result = await query(
    `SELECT id
     FROM clients
     WHERE id = $1 AND realtor_id = $2
     LIMIT 1`,
    [clientId, realtorId]
  );
  return result.rows[0] ?? null;
}

export async function listClients(realtorId: string, search = "", status = "") {
  const result = await query(
    `SELECT
       c.id,
       c.name,
       c.phone,
       c.email,
       c.send_channel,
       c.send_contact,
       c.status,
       c.property_type,
       c.comment,
       c.created_at,
       c.updated_at,
       row_to_json(sp.*) AS search_profile,
       json_build_object(
         'foundProperties', COALESCE(fp.count, 0),
         'shortlistItems', COALESCE(si.count, 0)
       ) AS _count
     FROM clients c
     LEFT JOIN LATERAL (
       SELECT *
       FROM client_search_profiles
       WHERE client_id = c.id
     ) sp ON TRUE
     LEFT JOIN LATERAL (
       SELECT COUNT(*)::int AS count
       FROM client_found_properties
       WHERE client_id = c.id AND is_hidden = FALSE
     ) fp ON TRUE
     LEFT JOIN LATERAL (
       SELECT COUNT(*)::int AS count
       FROM shortlist_items
       WHERE client_id = c.id
     ) si ON TRUE
     WHERE c.realtor_id = $1
       AND ($2 = '' OR c.name ILIKE '%' || $2 || '%' OR c.phone ILIKE '%' || $2 || '%' OR COALESCE(c.email, '') ILIKE '%' || $2 || '%')
       AND ($3 = '' OR c.status = $3)
     ORDER BY c.updated_at DESC`,
    [realtorId, search, status]
  );
  return camelize(result.rows);
}

function profileValues(profile: Record<string, unknown>) {
  return [
    profile.budgetMin ?? null,
    profile.budgetMax ?? null,
    profile.roomsMin ?? null,
    profile.roomsMax ?? null,
    profile.areaMin ?? null,
    profile.areaMax ?? null,
    profile.districts ?? [],
    profile.settlementNames ?? [],
    profile.completionYearMin ?? null,
    profile.completionYearMax ?? null,
    profile.finishing ?? null,
    profile.floorMin ?? null,
    profile.floorMax ?? null,
    profile.houseAreaMin ?? null,
    profile.houseAreaMax ?? null,
    profile.landAreaMin ?? null,
    profile.landAreaMax ?? null,
    profile.floorsCountMin ?? null,
    profile.floorsCountMax ?? null,
    profile.bedroomsMin ?? null,
    profile.bedroomsMax ?? null,
    profile.houseMaterial ?? null,
    profile.communications ?? []
  ];
}

export async function createClientWithProfile(realtorId: string, payload: ClientPayload) {
  return withClient(async (client) => {
    await client.query("BEGIN");
    try {
      const createdClient = await client.query<{ id: string }>(
        `INSERT INTO clients
         (realtor_id, name, phone, email, send_channel, send_contact, status, property_type, comment)
         VALUES ($1, $2, $3, $4, $5, $6, 'new', $7, $8)
         RETURNING id`,
        [realtorId, payload.name, payload.phone, payload.email ?? null, payload.sendChannel, payload.sendContact ?? null, payload.propertyType, payload.comment ?? null]
      );

      const clientId = createdClient.rows[0].id;
      await client.query(
        `INSERT INTO client_search_profiles
         (client_id, ${profileColumns.join(", ")})
         VALUES ($1, ${profileColumns.map((_, index) => `$${index + 2}`).join(", ")})`,
        [clientId, ...profileValues(payload.searchProfile)]
      );

      await client.query("COMMIT");
      return { id: clientId };
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    }
  });
}

export async function updateClientWithProfile(clientId: string, payload: ClientPayload) {
  return withClient(async (client) => {
    await client.query("BEGIN");
    try {
      await client.query(
        `UPDATE clients
         SET name = $2,
             phone = $3,
             email = $4,
             send_channel = $5,
             send_contact = $6,
             property_type = $7,
             comment = $8,
             updated_at = NOW()
         WHERE id = $1`,
        [clientId, payload.name, payload.phone, payload.email ?? null, payload.sendChannel, payload.sendContact ?? null, payload.propertyType, payload.comment ?? null]
      );

      await client.query(
        `INSERT INTO client_search_profiles
         (client_id, ${profileColumns.join(", ")})
         VALUES ($1, ${profileColumns.map((_, index) => `$${index + 2}`).join(", ")})
         ON CONFLICT (client_id) DO UPDATE SET
           ${profileColumns.map((column) => `${column} = EXCLUDED.${column}`).join(", ")},
           updated_at = NOW()`,
        [clientId, ...profileValues(payload.searchProfile)]
      );

      await client.query("COMMIT");
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    }
  });
}

export async function deleteClient(clientId: string) {
  await query("DELETE FROM clients WHERE id = $1", [clientId]);
}

export async function getClientDetails(clientId: string, realtorId: string) {
  const clientResult = await query(
    `SELECT c.*, row_to_json(sp.*) AS search_profile
     FROM clients c
     LEFT JOIN client_search_profiles sp ON sp.client_id = c.id
     WHERE c.id = $1 AND c.realtor_id = $2
     LIMIT 1`,
    [clientId, realtorId]
  );
  const row = clientResult.rows[0];
  if (!row) return null;

  const foundProperties = await query(
    `SELECT cfp.*, row_to_json(p.*) AS property
     FROM client_found_properties cfp
     JOIN properties p ON p.id = cfp.property_id
     WHERE cfp.client_id = $1 AND cfp.is_hidden = FALSE
     ORDER BY cfp.match_score DESC NULLS LAST, cfp.created_at DESC`,
    [clientId]
  );
  const shortlistItems = await query(
    `SELECT si.*, row_to_json(p.*) AS property
     FROM shortlist_items si
     JOIN properties p ON p.id = si.property_id
     WHERE si.client_id = $1
     ORDER BY si.created_at ASC`,
    [clientId]
  );
  const searchRuns = await query(
    `SELECT *
     FROM search_runs
     WHERE client_id = $1
     ORDER BY started_at DESC
     LIMIT 3`,
    [clientId]
  );

  return camelize({
    ...row,
    foundProperties: foundProperties.rows,
    shortlistItems: shortlistItems.rows,
    searchRuns: searchRuns.rows
  });
}

export async function getFoundProperties(clientId: string) {
  const result = await query(
    `SELECT cfp.*, row_to_json(p.*) AS property
     FROM client_found_properties cfp
     JOIN properties p ON p.id = cfp.property_id
     WHERE cfp.client_id = $1 AND cfp.is_hidden = FALSE
     ORDER BY cfp.match_score DESC NULLS LAST, cfp.created_at DESC`,
    [clientId]
  );
  return camelize(result.rows);
}

export async function getFoundProperty(clientId: string, propertyId: string) {
  const result = await query(
    `SELECT cfp.*, row_to_json(p.*) AS property
     FROM client_found_properties cfp
     JOIN properties p ON p.id = cfp.property_id
     WHERE cfp.client_id = $1 AND cfp.property_id = $2 AND cfp.is_hidden = FALSE
     LIMIT 1`,
    [clientId, propertyId]
  );
  return camelize(result.rows[0] ?? null);
}

export async function getShortlist(clientId: string) {
  const result = await query(
    `SELECT si.*, row_to_json(p.*) AS property
     FROM shortlist_items si
     JOIN properties p ON p.id = si.property_id
     WHERE si.client_id = $1
     ORDER BY si.created_at ASC`,
    [clientId]
  );
  return camelize(result.rows);
}

export async function addToShortlist(clientId: string, propertyId: string) {
  await query(
    `INSERT INTO shortlist_items (client_id, property_id)
     VALUES ($1, $2)
     ON CONFLICT (client_id, property_id) DO NOTHING`,
    [clientId, propertyId]
  );
  await query(`UPDATE clients SET status = 'shortlist_ready', updated_at = NOW() WHERE id = $1`, [clientId]);
  const result = await query(
    `SELECT si.*, row_to_json(p.*) AS property
     FROM shortlist_items si
     JOIN properties p ON p.id = si.property_id
     WHERE si.client_id = $1 AND si.property_id = $2
     LIMIT 1`,
    [clientId, propertyId]
  );
  return camelize(result.rows[0] ?? null);
}

export async function removeFromShortlist(clientId: string, propertyId: string) {
  await query(`DELETE FROM shortlist_items WHERE client_id = $1 AND property_id = $2`, [clientId, propertyId]);
  const count = await query<{ count: number }>("SELECT COUNT(*)::int AS count FROM shortlist_items WHERE client_id = $1", [clientId]);
  if (count.rows[0]?.count === 0) {
    const found = await query<{ count: number }>(
      `SELECT COUNT(*)::int AS count FROM client_found_properties WHERE client_id = $1 AND is_hidden = FALSE`,
      [clientId]
    );
    await query(`UPDATE clients SET status = $2, updated_at = NOW() WHERE id = $1`, [clientId, found.rows[0]?.count ? "found" : "no_results"]);
  }
}

export async function createShareMessage(clientId: string, channel: string, contact: string | null, messageText: string) {
  const result = await query(
    `INSERT INTO share_messages (client_id, channel, contact, message_text)
     VALUES ($1, $2, $3, $4)
     RETURNING *`,
    [clientId, channel, contact, messageText]
  );
  return camelize(result.rows[0]);
}

export async function markSent(clientId: string) {
  await withClient(async (client) => {
    await client.query("BEGIN");
    try {
      await client.query(`UPDATE clients SET status = 'sent', updated_at = NOW() WHERE id = $1`, [clientId]);
      await client.query(
        `UPDATE share_messages
         SET copied_at = COALESCE(copied_at, NOW()), sent_marked_at = NOW()
         WHERE client_id = $1 AND sent_marked_at IS NULL`,
        [clientId]
      );
      await client.query("COMMIT");
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    }
  });
  const client = await query(`SELECT * FROM clients WHERE id = $1 LIMIT 1`, [clientId]);
  return camelize(client.rows[0] ?? null);
}

export async function dashboardSummary(realtorId: string) {
  const result = await query(
    `SELECT
       (SELECT COUNT(*)::int FROM clients WHERE realtor_id = $1 AND status <> 'closed') AS clients_in_work,
       (SELECT COUNT(*)::int
        FROM client_found_properties cfp
        JOIN clients c ON c.id = cfp.client_id
        WHERE c.realtor_id = $1 AND cfp.is_hidden = FALSE) AS found_objects,
       (SELECT COUNT(*)::int
        FROM shortlist_items si
        JOIN clients c ON c.id = si.client_id
        WHERE c.realtor_id = $1) AS shortlist_items,
       (SELECT COUNT(*)::int FROM clients WHERE realtor_id = $1 AND status = 'shortlist_ready') AS ready_to_send`,
    [realtorId]
  );
  return camelize(result.rows[0]);
}

export async function dashboardActivity(realtorId: string) {
  const result = await query(
    `WITH days AS (
       SELECT generate_series(
         date_trunc('day', NOW()) - INTERVAL '6 days',
         date_trunc('day', NOW()),
         INTERVAL '1 day'
       ) AS day
     )
     SELECT
       days.day,
       (
         SELECT COUNT(*)::int
         FROM clients c
         WHERE c.realtor_id = $1
           AND c.status <> 'closed'
           AND c.created_at < days.day + INTERVAL '1 day'
       ) AS clients,
       (
         SELECT COUNT(*)::int
         FROM client_found_properties cfp
         JOIN clients c ON c.id = cfp.client_id
         WHERE c.realtor_id = $1
           AND cfp.is_hidden = FALSE
           AND cfp.created_at < days.day + INTERVAL '1 day'
       ) AS found,
       (
         SELECT COUNT(*)::int
         FROM shortlist_items si
         JOIN clients c ON c.id = si.client_id
         WHERE c.realtor_id = $1
           AND si.created_at < days.day + INTERVAL '1 day'
       ) AS shortlisted,
       (
         SELECT COUNT(*)::int
         FROM share_messages sm
         JOIN clients c ON c.id = sm.client_id
         WHERE c.realtor_id = $1
           AND sm.sent_marked_at IS NOT NULL
           AND sm.sent_marked_at < days.day + INTERVAL '1 day'
       ) AS sent,
       (
         SELECT COUNT(*)::int
         FROM clients c
         WHERE c.realtor_id = $1
           AND c.status = 'shortlist_ready'
           AND c.updated_at < days.day + INTERVAL '1 day'
       ) AS ready
     FROM days
     ORDER BY days.day`,
    [realtorId]
  );
  return result.rows;
}

export async function attentionClients(realtorId: string) {
  const result = await query(
    `SELECT
       c.*,
       row_to_json(sp.*) AS search_profile,
       json_build_object(
         'foundProperties', COALESCE(fp.count, 0),
         'shortlistItems', COALESCE(si.count, 0)
       ) AS _count
     FROM clients c
     LEFT JOIN client_search_profiles sp ON sp.client_id = c.id
     LEFT JOIN LATERAL (SELECT COUNT(*)::int AS count FROM client_found_properties WHERE client_id = c.id AND is_hidden = FALSE) fp ON TRUE
     LEFT JOIN LATERAL (SELECT COUNT(*)::int AS count FROM shortlist_items WHERE client_id = c.id) si ON TRUE
     WHERE c.realtor_id = $1 AND c.status = ANY($2::text[])
     ORDER BY c.updated_at DESC
     LIMIT 4`,
    [realtorId, ["found", "shortlist_ready", "no_results", "error"]]
  );
  return camelize(result.rows);
}

export async function getPropertyById(propertyId: string) {
  const result = await query(`SELECT * FROM properties WHERE id = $1 LIMIT 1`, [propertyId]);
  return camelize(result.rows[0] ?? null);
}

export async function getClientForSearch(clientId: string, realtorId: string) {
  const result = await query(
    `SELECT c.*, row_to_json(sp.*) AS search_profile
     FROM clients c
     LEFT JOIN client_search_profiles sp ON sp.client_id = c.id
     WHERE c.id = $1 AND c.realtor_id = $2
     LIMIT 1`,
    [clientId, realtorId]
  );
  return camelize(result.rows[0] ?? null);
}

export async function createSearchRun(clientId: string, propertyType: string) {
  const result = await query(
    `INSERT INTO search_runs (client_id, status, property_type)
     VALUES ($1, 'running', $2)
     RETURNING *`,
    [clientId, propertyType]
  );
  return camelize(result.rows[0]);
}

export async function updateClientStatus(clientId: string, status: string) {
  await query(`UPDATE clients SET status = $2, updated_at = NOW() WHERE id = $1`, [clientId, status]);
}

export async function upsertProperty(item: Record<string, unknown>) {
  const result = await query(
    `INSERT INTO properties (
       external_id, source_name, source_url, property_type, title, complex_name, developer_name,
       description, city, district, address, settlement_name, price, price_per_meter, area, rooms,
       floor, floors_total, house_area, land_area, bedrooms, house_floors, house_material,
       communications, completion_year, finishing, images, raw_data
     )
     VALUES (
       $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28
     )
     ON CONFLICT (source_url) DO UPDATE SET
       external_id = EXCLUDED.external_id,
       source_name = EXCLUDED.source_name,
       property_type = EXCLUDED.property_type,
       title = EXCLUDED.title,
       complex_name = EXCLUDED.complex_name,
       developer_name = EXCLUDED.developer_name,
       description = EXCLUDED.description,
       city = EXCLUDED.city,
       district = EXCLUDED.district,
       address = EXCLUDED.address,
       settlement_name = EXCLUDED.settlement_name,
       price = EXCLUDED.price,
       price_per_meter = EXCLUDED.price_per_meter,
       area = EXCLUDED.area,
       rooms = EXCLUDED.rooms,
       floor = EXCLUDED.floor,
       floors_total = EXCLUDED.floors_total,
       house_area = EXCLUDED.house_area,
       land_area = EXCLUDED.land_area,
       bedrooms = EXCLUDED.bedrooms,
       house_floors = EXCLUDED.house_floors,
       house_material = EXCLUDED.house_material,
       communications = EXCLUDED.communications,
       completion_year = EXCLUDED.completion_year,
       finishing = EXCLUDED.finishing,
       images = EXCLUDED.images,
       raw_data = EXCLUDED.raw_data,
       last_seen_at = NOW()
     RETURNING id`,
    [
      item.externalId ?? null,
      item.sourceName ?? null,
      item.sourceUrl,
      item.propertyType,
      item.title,
      item.complexName ?? null,
      item.developerName ?? null,
      item.description ?? null,
      item.city ?? null,
      item.district ?? null,
      item.address ?? null,
      item.settlementName ?? null,
      item.price ?? null,
      item.pricePerMeter ?? null,
      item.area ?? null,
      item.rooms ?? null,
      item.floor ?? null,
      item.floorsTotal ?? null,
      item.houseArea ?? null,
      item.landArea ?? null,
      item.bedrooms ?? null,
      item.houseFloors ?? null,
      item.houseMaterial ?? null,
      item.communications ?? [],
      item.completionYear ?? null,
      item.finishing ?? null,
      item.images ?? [],
      item.rawData ?? null
    ]
  );
  return result.rows[0];
}

export async function upsertClientFoundProperty(clientId: string, propertyId: string, item: Record<string, unknown>) {
  await query(
    `INSERT INTO client_found_properties
     (client_id, property_id, match_score, match_reasons, mismatch_reasons, is_hidden)
     VALUES ($1, $2, $3, $4, $5, FALSE)
     ON CONFLICT (client_id, property_id) DO UPDATE SET
       match_score = EXCLUDED.match_score,
       match_reasons = EXCLUDED.match_reasons,
       mismatch_reasons = EXCLUDED.mismatch_reasons,
       is_hidden = FALSE`,
    [clientId, propertyId, item.matchScore ?? 0, item.matchReasons ?? [], item.mismatchReasons ?? []]
  );
}

export async function finishSearchRun(searchRunId: string, totalFound: number, totalSaved: number) {
  await query(
    `UPDATE search_runs
     SET status = 'ok', total_found = $2, total_saved = $3, finished_at = NOW()
     WHERE id = $1`,
    [searchRunId, totalFound, totalSaved]
  );
}

export async function failSearchRun(searchRunId: string, errorMessage: string) {
  await query(
    `UPDATE search_runs
     SET status = 'error', error_message = $2, finished_at = NOW()
     WHERE id = $1`,
    [searchRunId, errorMessage]
  );
}
