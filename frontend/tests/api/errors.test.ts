import { describe, expect, it } from "vitest";

import {
  ApiConflictError,
  ApiForbiddenError,
  ApiNetworkError,
  ApiNotFoundError,
  ApiRateLimitError,
  ApiServerError,
  ApiTimeoutError,
  ApiUnauthorizedError,
  ApiUnknownError,
  ApiValidationError,
  createHttpError,
  normalizeUnknownError,
} from "@/lib/api/errors";

describe("API error normalization", () => {
  it("maps HTTP status codes to typed API errors", () => {
    expect(createHttpError(401, { message: "Unauthorized" })).toBeInstanceOf(ApiUnauthorizedError);
    expect(createHttpError(403, { message: "Forbidden" })).toBeInstanceOf(ApiForbiddenError);
    expect(createHttpError(404, { message: "Not found" })).toBeInstanceOf(ApiNotFoundError);
    expect(createHttpError(409, { message: "Conflict" })).toBeInstanceOf(ApiConflictError);
    expect(createHttpError(422, { message: "Validation" })).toBeInstanceOf(ApiValidationError);
    expect(createHttpError(429, { message: "Rate limit" })).toBeInstanceOf(ApiRateLimitError);
    expect(createHttpError(500, { message: "Server" })).toBeInstanceOf(ApiServerError);
    expect(createHttpError(418, { message: "Unknown" })).toBeInstanceOf(ApiUnknownError);
  });

  it("normalizes network, timeout and unknown errors", () => {
    expect(normalizeUnknownError(new TypeError("Failed to fetch"))).toBeInstanceOf(ApiNetworkError);
    expect(normalizeUnknownError(new DOMException("Aborted", "AbortError"))).toBeInstanceOf(
      ApiTimeoutError,
    );
    expect(normalizeUnknownError("unexpected")).toBeInstanceOf(ApiUnknownError);
  });
});
