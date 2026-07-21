import { describe, expect, it } from "vitest";

import {
  VAULT_DESCRIPTION_MAX_LENGTH,
  VAULT_NAME_MAX_LENGTH,
  VAULT_NAME_MIN_LENGTH,
  vaultFormSchema,
} from "@/features/vault/validation/vault-schema";

describe("vault validation", () => {
  it("accepts a valid vault form payload", () => {
    expect(vaultFormSchema.safeParse({ description: "", name: "Production" }).success).toBe(true);
  });

  it("enforces backend vault name length constraints", () => {
    expect(vaultFormSchema.safeParse({ name: "a".repeat(VAULT_NAME_MIN_LENGTH - 1) }).success).toBe(
      false,
    );
    expect(vaultFormSchema.safeParse({ name: "a".repeat(VAULT_NAME_MAX_LENGTH + 1) }).success).toBe(
      false,
    );
  });

  it("keeps descriptions non-sensitive and bounded", () => {
    expect(
      vaultFormSchema.safeParse({
        description: "a".repeat(VAULT_DESCRIPTION_MAX_LENGTH + 1),
        name: "Production",
      }).success,
    ).toBe(false);
  });
});
