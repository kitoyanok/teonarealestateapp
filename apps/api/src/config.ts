// Этот файл собирает настройки приложения из переменных окружения.
// Проще говоря: здесь backend узнает, на каком порту запускаться,
// как подключаться к базе и где искать сервис поиска.
import dotenv from "dotenv";

dotenv.config({ path: ".env" });
dotenv.config({ path: "../../.env" });

export const config = {
  port: Number(process.env.API_PORT ?? process.env.NODE_API_PORT ?? process.env.WEB_PORT ?? 5003),
  jwtSecret: process.env.JWT_SECRET ?? "estateflow-dev-secret",
  searchServiceUrl: process.env.SEARCH_SERVICE_URL ?? "http://localhost:8002",
  isProduction: process.env.NODE_ENV === "production",
  databaseUrl: process.env.DATABASE_URL ?? "postgres://estateflow:estateflow_password@localhost:5432/estateflow"
};
