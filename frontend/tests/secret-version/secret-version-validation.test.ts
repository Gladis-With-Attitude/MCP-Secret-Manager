import { describe, expect, it } from "vitest";

import {
  parseSecretVersionMetadata,
  secretVersionRestoreFormSchema,
  secretVersionRotateFormSchema,
} from "@/features/secret-version/validation/secret-version-schema";

describe("secret version validation", () => {
  it("accepts value transport and non-sensitive metadata", () => {
    const parsed = secretVersionRotateFormSchema.parse({
      makeCurrent: true,
      metadataJson: '{"source":"manual"}',
      note: "scheduled rotation",
      value: "sensitive-value",
    });

    expect(parsed.value).toBe("sensitive-value");
    expect(parseSecretVersionMetadata(parsed.metadataJson)).toEqual({ source: "manual" });
  });

  it("rejects missing values and non-object metadata", () => {
    expect(() =>
      secretVersionRotateFormSchema.parse({
        makeCurrent: true,
        metadataJson: "[]",
        note: "",
        value: "",
      }),
    ).toThrow();
  });

  it("validates restore metadata only", () => {
    expect(
      secretVersionRestoreFormSchema.parse({ reason: "rollback approved", versionId: "version_1" }),
    ).toEqual({ reason: "rollback approved", versionId: "version_1" });
  });
});
