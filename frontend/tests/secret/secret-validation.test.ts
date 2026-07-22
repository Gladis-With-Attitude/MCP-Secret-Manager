import { describe, expect, it } from "vitest";

import {
  parseSecretMetadata,
  parseSecretTags,
  SECRET_NAME_MAX_LENGTH,
  SECRET_NAME_MIN_LENGTH,
  secretCreateFormSchema,
  secretMetadataFormSchema,
} from "@/features/secret/validation/secret-schema";

describe("secret validation", () => {
  it("accepts valid metadata and create payloads", () => {
    expect(
      secretCreateFormSchema.safeParse({
        metadataJson: '{"owner":"platform"}',
        name: "API_TOKEN",
        tagsInput: "production, api",
        type: "api_key",
        value: "sensitive-value",
      }).success,
    ).toBe(true);
    expect(
      secretMetadataFormSchema.safeParse({
        metadataJson: "",
        name: "DATABASE_PASSWORD",
        tagsInput: "",
        type: "password",
      }).success,
    ).toBe(true);
  });

  it("enforces backend secret key constraints", () => {
    expect(
      secretMetadataFormSchema.safeParse({
        metadataJson: "",
        name: "ab",
        tagsInput: "",
        type: "generic",
      }).success,
    ).toBe(false);
    expect(
      secretMetadataFormSchema.safeParse({
        metadataJson: "",
        name: "a".repeat(SECRET_NAME_MAX_LENGTH + 1).toUpperCase(),
        tagsInput: "",
        type: "generic",
      }).success,
    ).toBe(false);
    expect(
      secretMetadataFormSchema.safeParse({
        metadataJson: "",
        name: "invalid-name",
        tagsInput: "",
        type: "generic",
      }).success,
    ).toBe(false);
    expect("A".repeat(SECRET_NAME_MIN_LENGTH)).toHaveLength(SECRET_NAME_MIN_LENGTH);
  });

  it("validates metadata JSON and tags without inspecting encryption", () => {
    expect(() => parseSecretMetadata('{"owner":"platform","count":1,"active":true}')).not.toThrow();
    expect(() => parseSecretMetadata('["not-object"]')).toThrow();
    expect(parseSecretTags("prod, db")).toEqual(["prod", "db"]);
    expect(
      secretCreateFormSchema.safeParse({
        metadataJson: "",
        name: "API_TOKEN",
        tagsInput: "",
        type: "token",
        value: "",
      }).success,
    ).toBe(false);
  });
});
