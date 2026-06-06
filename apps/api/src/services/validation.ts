// Этот файл проверяет входные данные от пользователя.
// Проще говоря: он не дает сохранить в базу сломанный телефон, пустой логин или некорректные параметры поиска.

import { z } from "zod";

const phoneError = "Введите номер в формате +7 (999) 999-99-99 или 8 (999) 999-99-99.";

function normalizePhone(value: string) {
  const trimmed = value.trim();
  const digits = trimmed.replace(/\D/g, "");

  if (trimmed.startsWith("+7")) {
    return digits.length === 11 && digits.startsWith("7") ? `+${digits}` : null;
  }

  if (digits.startsWith("8")) {
    return digits.length === 11 ? digits : null;
  }

  return null;
}

const nullableNumber = z.preprocess(
  (value) => (value === "" || value === null || value === undefined ? undefined : Number(value)),
  z.number().finite().min(0, "Значение не может быть отрицательным").optional()
);

const nullableInt = z.preprocess(
  (value) => (value === "" || value === null || value === undefined ? undefined : Number(value)),
  z.number().int().min(0, "Значение не может быть отрицательным").optional()
);

const list = z.preprocess((value) => {
  if (Array.isArray(value)) {
    return value.map(String).filter(Boolean);
  }
  if (typeof value === "string") {
    return value.split(",").map((item) => item.trim()).filter(Boolean);
  }
  return [];
}, z.array(z.string()));

export const loginSchema = z.object({
  login: z.string().min(1),
  password: z.string().min(1)
});

export const updateUserSchema = z.object({
  name: z.string().trim().min(2, "Укажите имя риелтора"),
  email: z.string().trim().email("Укажите корректный email").optional().or(z.literal("")).nullable(),
  phone: z.string().min(1, phoneError).transform((value, ctx) => {
    const normalized = normalizePhone(value);
    if (!normalized) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: phoneError });
      return z.NEVER;
    }
    return normalized;
  })
});

export const clientSchema = z.object({
  name: z.string().min(2, "Укажите имя клиента"),
  phone: z.string().min(1, phoneError).transform((value, ctx) => {
    const normalized = normalizePhone(value);
    if (!normalized) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: phoneError });
      return z.NEVER;
    }
    return normalized;
  }),
  email: z.string().email().optional().or(z.literal("")).nullable(),
  sendChannel: z.enum(["max", "telegram", "whatsapp", "email", "copy"]),
  sendContact: z.string().optional().nullable(),
  propertyType: z.enum(["apartment", "house"]),
  comment: z.string().optional().nullable(),
  searchProfile: z.object({
    budgetMin: nullableNumber,
    budgetMax: nullableNumber,
    roomsMin: nullableInt,
    roomsMax: nullableInt,
    areaMin: nullableNumber,
    areaMax: nullableNumber,
    districts: list,
    settlementNames: list,
    completionYearMin: nullableInt,
    completionYearMax: nullableInt,
    finishing: z.string().optional().nullable(),
    floorMin: nullableInt,
    floorMax: nullableInt,
    houseAreaMin: nullableNumber,
    houseAreaMax: nullableNumber,
    landAreaMin: nullableNumber,
    landAreaMax: nullableNumber,
    floorsCountMin: nullableInt,
    floorsCountMax: nullableInt,
    bedroomsMin: nullableInt,
    bedroomsMax: nullableInt,
    houseMaterial: z.string().optional().nullable(),
    communications: list
  })
});

export type ClientPayload = z.infer<typeof clientSchema>;
