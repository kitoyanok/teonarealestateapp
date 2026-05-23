// Этот файл делает все запросы frontend к backend единообразными.
// Проще говоря: он отправляет HTTP-запросы, читает ответы и превращает ошибки сервера в понятный вид.

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {})
    }
  });

  const contentType = response.headers.get("content-type") ?? "";
  // Payload - это содержимое ответа сервера: то, что backend отправил в браузер.
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    throw new ApiError(response.status, payload?.message ?? "Сервис временно недоступен");
  }

  return payload as T;
}

export const api = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }),
  put: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: "PUT", body: JSON.stringify(body ?? {}) }),
  delete: <T>(path: string) => apiRequest<T>(path, { method: "DELETE" })
};
