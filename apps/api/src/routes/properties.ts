// Этот файл отдает подробные данные по одному объекту недвижимости.
// Проще говоря: он нужен, когда фронтенду надо открыть карточку конкретного объявления.

import { Router } from "express";
import { requireAuth } from "../middleware/auth.js";
import { getPropertyById } from "../repositories/sql.js";
import { serialize } from "../services/serializers.js";

export const propertiesRouter = Router();

propertiesRouter.use(requireAuth);

propertiesRouter.get("/:id", async (req, res, next) => {
  try {
    const property = await getPropertyById(req.params.id);
    res.json(serialize(property));
  } catch (error) {
    next(error);
  }
});
