// Этот файл запускает backend-сервер.
// Проще говоря: сначала он убеждается, что стартовые риелторы есть в базе, потом поднимает API и корректно завершает его при остановке.
import { config } from "./config.js";
import { createApp } from "./app.js";
import { pool } from "./db/pool.js";
import { ensureSeedRealtors } from "./repositories/db.js";

async function bootstrap() {
  await ensureSeedRealtors();
  const app = await createApp();

  const server = app.listen(config.port, () => {
    console.log(`EstateFlow is running on http://localhost:${config.port}`);
  });

  const shutdown = async () => {
    server.close();
    await pool.end();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

bootstrap().catch(async (error) => {
  console.error(error);
  await pool.end();
  process.exit(1);
});
