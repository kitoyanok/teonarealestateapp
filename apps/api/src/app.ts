import path from "node:path";
import { fileURLToPath } from "node:url";
import cookieParser from "cookie-parser";
import cors from "cors";
import express from "express";
import { authRouter } from "./routes/auth.js";
import { clientsRouter } from "./routes/clients.js";
import { dashboardRouter } from "./routes/dashboard.js";
import { propertiesRouter } from "./routes/properties.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../../..");

export async function createApp() {
  const app = express();

  app.use(cors({ origin: true, credentials: true }));
  app.use(express.json({ limit: "1mb" }));
  app.use(cookieParser());

  app.get("/api/health", (_req, res) => {
    res.json({ ok: true, service: "estateflow-api" });
  });

  app.use("/api/auth", authRouter);
  app.use("/api/dashboard", dashboardRouter);
  app.use("/api/clients", clientsRouter);
  app.use("/api/properties", propertiesRouter);

  app.use("/api", (_req, res) => {
    res.status(404).json({ message: "API endpoint not found" });
  });

  app.use((error: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    const typed = error as Error & { status?: number; issues?: unknown };
    const status = typed.status ?? (typed.name === "ZodError" ? 400 : 500);
    res.status(status).json({
      message: status === 500 ? "Сервис временно недоступен" : typed.message,
      issues: typed.issues
    });
  });

  if (process.env.NODE_ENV === "production") {
    const staticRoot = path.join(repoRoot, "apps/web/dist");
    app.use(express.static(staticRoot));
    app.get("*", (_req, res) => {
      res.sendFile(path.join(staticRoot, "index.html"));
    });
  }

  return app;
}
