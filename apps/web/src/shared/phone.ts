// Этот файл работает с телефонными номерами.
// Проще говоря: он очищает номер, форматирует его и помогает не сохранять мусор вместо телефона.

const PHONE_ERROR = "Введите номер в формате +7 (999) 999-99-99 или 8 (999) 999-99-99.";

function digitsOnly(value: string) {
  return value.replace(/\D/g, "");
}

export function normalizePhone(value: string) {
  const trimmed = value.trim();
  if (trimmed.startsWith("+7")) {
    const digits = `7${digitsOnly(trimmed.slice(2))}`;
    return digits.length === 11 ? `+${digits}` : null;
  }

  const digits = digitsOnly(trimmed);
  if (digits.startsWith("8") && digits.length === 11) {
    return digits;
  }

  return null;
}

export function isValidPhone(value: string) {
  return normalizePhone(value) !== null;
}

export function formatPhoneInput(value: string) {
  const hasPlusSeven = value.trim().startsWith("+7");
  const digits = digitsOnly(value);

  if (hasPlusSeven) {
    const local = digits.replace(/^7/, "").slice(0, 10);
    return `+7${local ? ` (${local.slice(0, 3)}` : ""}${local.length >= 3 ? ")" : ""}${local.length > 3 ? ` ${local.slice(3, 6)}` : ""}${local.length > 6 ? `-${local.slice(6, 8)}` : ""}${local.length > 8 ? `-${local.slice(8, 10)}` : ""}`;
  }

  if (digits.startsWith("8")) {
    const local = digits.slice(1, 11);
    return `8${local ? ` (${local.slice(0, 3)}` : ""}${local.length >= 3 ? ")" : ""}${local.length > 3 ? ` ${local.slice(3, 6)}` : ""}${local.length > 6 ? `-${local.slice(6, 8)}` : ""}${local.length > 8 ? `-${local.slice(8, 10)}` : ""}`;
  }

  if (digits.startsWith("7")) {
    const local = digits.slice(1, 11);
    return `+7${local ? ` (${local.slice(0, 3)}` : ""}${local.length >= 3 ? ")" : ""}${local.length > 3 ? ` ${local.slice(3, 6)}` : ""}${local.length > 6 ? `-${local.slice(6, 8)}` : ""}${local.length > 8 ? `-${local.slice(8, 10)}` : ""}`;
  }

  return value.replace(/[^\d+()\-\s]/g, "").slice(0, 18);
}

export function phoneErrorText() {
  return PHONE_ERROR;
}
