import { describe, expect, it } from "vitest";

import { apiKeyFormSchema, parseApiKeyItems } from "@/features/api-key/validation/api-key-schema";

describe("api key validation", () => {
  it("accepts names, permissions, scopes and expiration", () => {
    const parsed = apiKeyFormSchema.parse({
      description: "Used by agent",
      expiresAt: "2026-02-01",
      name: "openclaw-agent",
      ownerId: "service-account-id",
      ownerType: "service_account",
      permissionsInput: "secret.read, secret.version.read",
      scopesInput: "global, vault:prod",
    });

    expect(parsed.name).toBe("openclaw-agent");
    expect(parseApiKeyItems(parsed.permissionsInput)).toEqual([
      "secret.read",
      "secret.version.read",
    ]);
  });

  it("rejects unsafe names and missing permissions", () => {
    expect(() =>
      apiKeyFormSchema.parse({
        description: "",
        expiresAt: "",
        name: "bad name",
        ownerId: "owner",
        ownerType: "service_account",
        permissionsInput: "",
        scopesInput: "global",
      }),
    ).toThrow();
  });
});
