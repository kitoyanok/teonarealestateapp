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
    const start = new Date();
    start.setDate(start.getDate() - 6);
    start.setHours(0, 0, 0, 0);

    const runs = await dashboardActivity(req.userId!);

    const days = Array.from({ length: 7 }, (_, index) => {
      const day = new Date(start);
      day.setDate(start.getDate() + index);
      return {
        key: day.toISOString().slice(0, 10),
        label: day.toLocaleDateString("ru-RU", { weekday: "short" }),
        found: 0,
        shortlisted: 0,
        sent: 0
      };
    });

    for (const run of runs) {
      const date = new Date(String((run as { started_at: string }).started_at));
      const key = date.toISOString().slice(0, 10);
      const item = days.find((day) => day.key === key);
      if (item) {
        item.found += Number((run as { total_found: number }).total_found ?? 0);
      }
    }

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
