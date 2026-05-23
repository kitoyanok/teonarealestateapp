// Этот файл отвечает за вход в систему, выход из нее и проверку "кто сейчас вошел".
// Проще говоря: здесь backend проверяет логин и пароль и выдает браузеру безопасную сессию.
import { Router } from "express";
import bcrypt from "bcryptjs";
import { requireAuth, signSession } from "../middleware/auth.js";
import { findUserById, findUserByLogin } from "../repositories/sql.js";
import { serialize } from "../services/serializers.js";
import { loginSchema } from "../services/validation.js";
import { config } from "../config.js";

export const authRouter = Router();

type AuthUser = {
  id: string;
  login: string;
  passwordHash: string;
  name: string;
  email?: string | null;
  phone?: string | null;
};

authRouter.post("/login", async (req, res, next) => {
  try {
    const input = loginSchema.parse(req.body);
    const user = (await findUserByLogin(input.login)) as AuthUser | null;
    if (!user) {
      return res.status(401).json({ message: "Неверный логин или пароль" });
    }

    const ok = await bcrypt.compare(input.password, user.passwordHash);
    if (!ok) {
      return res.status(401).json({ message: "Неверный логин или пароль" });
    }

    const token = signSession(user.id);
    res.cookie("estateflow_token", token, {
      httpOnly: true,
      sameSite: "lax",
      secure: config.isProduction,
      maxAge: 7 * 24 * 60 * 60 * 1000
    });

    return res.json({
      user: serialize({
        id: user.id,
        login: user.login,
        name: user.name,
        email: user.email,
        phone: user.phone
      })
    });
  } catch (error) {
    return next(error);
  }
});

authRouter.post("/logout", (_req, res) => {
  res.clearCookie("estateflow_token");
  res.json({ ok: true });
});

authRouter.get("/me", requireAuth, async (req, res, next) => {
  try {
    const user = (await findUserById(req.userId!)) as AuthUser | null;
    if (!user) {
      return res.status(401).json({ message: "Unauthorized" });
    }
    res.json({
      user: serialize({
        id: user.id,
        login: user.login,
        name: user.name,
        email: user.email,
        phone: user.phone
      })
    });
  } catch (error) {
    next(error);
  }
});
