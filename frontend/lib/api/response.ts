import { createHttpError } from "./errors";
import type { APIError, EmptyResponse } from "./types";

type ParsedErrorPayload = {
  code?: string;
  details?: unknown;
  fieldErrors?: Record<string, string[]>;
  message?: string;
  requestId?: string;
};

function isEmptyResponse(response: Response, method?: string): boolean {
  return (
    method === "HEAD" ||
    response.status === 204 ||
    response.status === 205 ||
    response.headers.get("content-length") === "0"
  );
}

function isJsonResponse(response: Response): boolean {
  return response.headers.get("content-type")?.toLowerCase().includes("application/json") ?? false;
}

function isStringRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeFieldErrors(value: unknown): Record<string, string[]> | undefined {
  if (!isStringRecord(value)) {
    return undefined;
  }

  const fieldErrors: Record<string, string[]> = {};

  Object.entries(value).forEach(([field, messages]) => {
    if (Array.isArray(messages)) {
      fieldErrors[field] = messages.map(String);
      return;
    }

    if (typeof messages === "string") {
      fieldErrors[field] = [messages];
    }
  });

  return Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined;
}

function extractErrorPayload(payload: unknown): ParsedErrorPayload {
  if (!isStringRecord(payload)) {
    return {};
  }

  const nestedError = isStringRecord(payload.error) ? payload.error : payload;
  const message = typeof nestedError.message === "string" ? nestedError.message : undefined;
  const code = typeof nestedError.code === "string" ? nestedError.code : undefined;
  const requestId =
    typeof nestedError.requestId === "string"
      ? nestedError.requestId
      : typeof nestedError.request_id === "string"
        ? nestedError.request_id
        : undefined;
  const fieldErrors = normalizeFieldErrors(
    nestedError.fieldErrors ?? nestedError.field_errors ?? nestedError.errors,
  );

  return {
    code,
    details: nestedError.details,
    fieldErrors,
    message,
    requestId,
  };
}

async function parseJsonSafely(response: Response): Promise<unknown> {
  if (!isJsonResponse(response)) {
    return undefined;
  }

  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

async function parseApiResponse<TData>(
  response: Response,
  method?: string,
): Promise<TData | EmptyResponse> {
  if (!response.ok) {
    const payload = await parseJsonSafely(response);
    const errorPayload = extractErrorPayload(payload);
    const apiError: APIError = {
      code: errorPayload.code,
      details: errorPayload.details,
      fieldErrors: errorPayload.fieldErrors,
      message: errorPayload.message ?? `HTTP request failed with status ${response.status}.`,
      requestId: errorPayload.requestId,
      status: response.status,
    };

    throw createHttpError(response.status, apiError);
  }

  if (isEmptyResponse(response, method)) {
    return undefined;
  }

  if (isJsonResponse(response)) {
    return (await response.json()) as TData;
  }

  return (await response.text()) as TData;
}

export { extractErrorPayload, isEmptyResponse, isJsonResponse, parseApiResponse };
export type { ParsedErrorPayload };
