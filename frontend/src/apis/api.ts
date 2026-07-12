import { z } from "zod";
import { useAuthStore } from "../store/authStore";
export * from "../schemas/index";

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

export const API_URL = import.meta.env.VITE_API_URL || "/api";

export async function fetchJSON(url: string, options?: RequestInit) {
  const token = useAuthStore.getState().token;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options?.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const errData = await res.json();
      if (errData.detail)
        msg =
          typeof errData.detail === "string"
            ? errData.detail
            : JSON.stringify(errData.detail);
    } catch (e) {}
    throw new APIError(res.status, msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

export function parse<T>(schema: z.ZodType<T>, data: unknown): T {
  return schema.parse(data);
}
