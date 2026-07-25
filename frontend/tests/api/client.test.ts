import { afterEach, describe, expect, it, vi } from "vitest";

import { createApiClient } from "@/lib/api/client";
import { ApiNetworkError } from "@/lib/api/errors";

const config = {
  baseUrl: "https://api.example.test",
  credentials: "include" as const,
  defaultHeaders: { "X-Client": "frontend" },
  environment: "test" as const,
  timeoutMs: 1000,
};

describe("API client", () => {
  afterEach(() => {
    document.cookie = "mcp_sm_csrf=; Max-Age=0; path=/";
    vi.unstubAllGlobals();
  });

  it("builds GET requests with query params and parses JSON", async () => {
    const fetchMock = vi.fn(async (request: Request) => {
      expect(request.method).toBe("GET");
      expect(request.url).toBe("https://api.example.test/items?limit=10&status=ready");
      expect(request.headers.get("Accept")).toBe("application/json");
      expect(request.headers.get("X-Client")).toBe("frontend");

      return new Response(JSON.stringify({ data: ["alpha"] }), {
        headers: { "content-type": "application/json" },
        status: 200,
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient(config);

    await expect(client.get("/items", { params: { limit: 10, status: "ready" } })).resolves.toEqual(
      {
        data: ["alpha"],
      },
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("builds JSON mutation requests without retrying by default", async () => {
    const fetchMock = vi.fn(async (request: Request) => {
      expect(request.method).toBe("POST");
      expect(request.headers.get("Content-Type")).toBe("application/json");
      expect(await request.text()).toBe(JSON.stringify({ name: "Alpha" }));

      return new Response(null, { status: 204 });
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient(config);

    await expect(client.post("/items", { name: "Alpha" })).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("echoes the CSRF cookie on unsafe browser requests", async () => {
    document.cookie = "mcp_sm_csrf=csrf-token; path=/";
    const fetchMock = vi.fn(async (request: Request) => {
      expect(request.method).toBe("PATCH");
      expect(request.headers.get("X-CSRF-Token")).toBe("csrf-token");

      return new Response(null, { status: 204 });
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient(config);

    await expect(client.patch("/items/alpha", { name: "Alpha" })).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("preserves an explicit CSRF header override", async () => {
    document.cookie = "mcp_sm_csrf=csrf-token; path=/";
    const fetchMock = vi.fn(async (request: Request) => {
      expect(request.headers.get("X-CSRF-Token")).toBe("explicit-token");

      return new Response(null, { status: 204 });
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient(config);

    await expect(
      client.delete("/items/alpha", { headers: { "X-CSRF-Token": "explicit-token" } }),
    ).resolves.toBeUndefined();
  });

  it("normalizes fetch failures and calls error hooks", async () => {
    const onError = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );

    const client = createApiClient(config, { onError });

    await expect(client.get("/items")).rejects.toBeInstanceOf(ApiNetworkError);
    expect(onError).toHaveBeenCalledTimes(1);
  });
});
