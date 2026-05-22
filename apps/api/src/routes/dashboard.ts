import { Router } from "express";
import { requireAuth } from "../middleware/auth.js";
import { attentionClients, dashboardActivity, dashboardSummary } from "../repositories/sql.js";
import { serialize } from "../services/serializers.js";

export const dashboardRouter = Router();

dashboardRouter.use(requireAuth);

dashboardRouter.get("/summary", async (req, res, next) => {
  try {
    const summary = await dashboardSummary(req.userId!);
    res.json(summary);
  } catch (error) {
    next(error);
  }
});

dashboardRouter.get("/activity", async (req, res, next) => {
  try {
    const runs = await dashboardActivity(req.userId!);
    const days = runs.map((run) => {
      const date = new Date(String((run as { day: string }).day));
      return {
        key: date.toISOString().slice(0, 10),
        label: date.toLocaleDateString("ru-RU", { weekday: "short" }),
        clients: Number((run as { clients: number }).clients ?? 0),
        found: Number((run as { found: number }).found ?? 0),
        shortlisted: Number((run as { shortlisted: number }).shortlisted ?? 0),
        sent: Number((run as { sent: number }).sent ?? 0),
        ready: Number((run as { ready: number }).ready ?? 0)
      };
    });

    res.json(days);
  } catch (error) {
    next(error);
  }
});

dashboardRouter.get("/attention-clients", async (req, res, next) => {
  try {
    const clients = await attentionClients(req.userId!);
    res.json(serialize(clients));
  } catch (error) {
    next(error);
  }
});
