import { pool } from "../db/pool.js";
import { config } from "../config.js";
import { ensureSeedUser as ensurePgSeedUser } from "./sql.js";

export async function ensureSeedUser() {
  return ensurePgSeedUser(config.demoLogin, config.demoPassword);
}

export { pool };
