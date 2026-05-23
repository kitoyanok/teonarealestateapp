// Этот файл защищает закрытые разделы API.
// Проще говоря: он проверяет, вошел ли пользователь в систему, и только после этого пускает его к данным.

import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { config } from "../config.js";
import { findUserById } from "../repositories/sql.js";

type TokenPayload = {
  sub: string;
};

type AuthUser = {
  id: string;
};

declare global {
  namespace Express {
    interface Request {
      userId?: string;
    }
  }
}

export function signSession(userId: string) {
  return jwt.sign({ sub: userId }, config.jwtSecret, { expiresIn: "7d" });
}

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  try {
    const bearer = req.headers.authorization?.replace(/^Bearer\s+/i, "");
    const token = req.cookies?.estateflow_token ?? bearer;
    if (!token) {
      return res.status(401).json({ message: "Unauthorized" });
    }

    const payload = jwt.verify(token, config.jwtSecret) as TokenPayload;
    const user = (await findUserById(payload.sub)) as AuthUser | null;
    if (!user) {
      return res.status(401).json({ message: "Unauthorized" });
    }

    req.userId = user.id;
    return next();
  } catch {
    return res.status(401).json({ message: "Unauthorized" });
  }
}
