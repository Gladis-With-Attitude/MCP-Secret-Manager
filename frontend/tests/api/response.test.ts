import { describe, expect, it } from "vitest";

import { ApiValidationError } from "@/lib/api/errors";
import { extractErrorPayload, isEmptyResponse, parseApiResponse } from "@/lib/api/response";

describe("API response parsing", () => {
  it("parses JSON responses", async () => {
    const response = new Response(JSON.stringify({ data: { id: "1" } }), {
      headers: { "content-type": "application/json" },
      status: 200,
    });

    await expect(parseApiResponse(response)).resolves.toEqual({ data: { id: "1" } });
  });

  it("returns undefined for empty responses", async () => {
    const response = new Response(null, { status: 204 });

    expect(isEmptyResponse(response)).toBe(true);
    await expect(parseApiResponse(response)).resolves.toBeUndefined();
  });

  it("throws normalized API errors for failed responses", async () => {
    const response = new Response(
      JSON.stringify({
        error: {
          code: "VALIDATION_ERROR",
          field_errors: { name: ["Required"] },
          message: "Invalid payload",
        },
      }),
      {
        headers: { "content-type": "application/json" },
        status: 422,
      },
    );

    const clonedResponse = response.clone();

    await expect(parseApiResponse(response)).rejects.toMatchObject({
      code: "VALIDATION_ERROR",
      fieldErrors: { name: ["Required"] },
      kind: "validation",
    });
    await expect(parseApiResponse(clonedResponse)).rejects.toBeInstanceOf(ApiValidationError);
  });

  it("extracts safe error payload fields", () => {
    expect(
      extractErrorPayload({
        error: {
          code: "ERROR_CODE",
          details: { safe: true },
          message: "Message",
          request_id: "request-1",
        },
      }),
    ).toEqual({
      code: "ERROR_CODE",
      details: { safe: true },
      fieldErrors: undefined,
      message: "Message",
      requestId: "request-1",
    });
  });
});
