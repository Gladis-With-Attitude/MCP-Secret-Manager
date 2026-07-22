import { describe, expect, it, vi } from "vitest";

import {
  mapApiKeyCreatedDtoToApiKeyCreated,
  mapApiKeyDtoToApiKey,
  mapApiKeyFiltersToParams,
  mapApiKeyFormToCreateDto,
  mapApiKeyListResponseToApiKeyList,
} from "@/features/api-key/mappers/api-key-mappers";

describe("api key mappers", () => {
  it("maps metadata without leaking full token values into ApiKey models", () => {
    const apiKey = mapApiKeyDtoToApiKey({
      id: "key_1",
      key_prefix: "mcp_123",
      name: "agent",
      token: "must-not-be-mapped",
    });

    expect(apiKey).toMatchObject({
      id: "key_1",
      keyPrefix: "mcp_123",
      name: "agent",
      status: "active",
    });
    expect(JSON.stringify(apiKey)).not.toContain("must-not-be-mapped");
  });

  it("maps the one-time created value separately from metadata", () => {
    const created = mapApiKeyCreatedDtoToApiKeyCreated({
      api_key: "mcp_full_value",
      id: "key_1",
      key_prefix: "mcp",
      name: "agent",
    });

    expect(created.apiKeyValue).toBe("mcp_full_value");
    expect(JSON.stringify(created.metadata)).not.toContain("mcp_full_value");
  });

  it("normalizes expired and revoked states", () => {
    vi.setSystemTime(new Date("2026-01-02T00:00:00Z"));

    expect(
      mapApiKeyDtoToApiKey({
        expires_at: "2026-01-01T00:00:00Z",
        id: "expired",
      }).status,
    ).toBe("expired");
    expect(
      mapApiKeyDtoToApiKey({
        id: "revoked",
        revoked_at: "2026-01-01T00:00:00Z",
      }).status,
    ).toBe("revoked");

    vi.useRealTimers();
  });

  it("maps lists, filters and create payloads", () => {
    expect(
      mapApiKeyListResponseToApiKeyList({
        data: [{ id: "key_1", key_prefix: "mcp" }],
        pagination: { page: 1, pageSize: 20, total: 1 },
        permissions: { create: true },
        success: true,
      }),
    ).toMatchObject({
      items: [{ id: "key_1" }],
      permissions: { create: true },
    });
    expect(mapApiKeyFiltersToParams({ search: " agent ", status: "active" })).toEqual({
      page: undefined,
      page_size: undefined,
      q: "agent",
      search: "agent",
      status: "active",
    });
    expect(
      mapApiKeyFormToCreateDto({
        description: " prod ",
        expiresAt: "2026-02-01",
        name: "agent",
        ownerId: "owner_1",
        ownerType: "service_account",
        permissions: ["secret.read"],
        scopes: ["global"],
      }),
    ).toEqual({
      description: "prod",
      expires_at: "2026-02-01",
      name: "agent",
      owner_id: "owner_1",
      owner_type: "service_account",
      permissions: ["secret.read"],
      scopes: ["global"],
    });
  });
});
