// Этот файл нужен как тонкая прослойка между запуском сервера и SQL-слоем.
// Он не хранит бизнес-логику сам, а просто дает понятные функции вроде "создай стартовых риелторов".
import { pool } from "../db/pool.js";
import { seedRealtors } from "../data/realtors.js";
import { ensureSeedRealtors as ensurePgSeedRealtors } from "./sql.js";

export async function ensureSeedRealtors() {
  return ensurePgSeedRealtors(seedRealtors);
}

export { pool };
