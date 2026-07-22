import { describe, expect, it } from "vitest";

import { notificationPreferencesSchema, preferencesSchema } from "@/features/settings";

describe("settings validation", () => {
  it("accepts valid preferences and notifications", () => {
    expect(
      preferencesSchema.safeParse({
        dateTimeFormat: "absolute",
        displayDensity: "comfortable",
        language: "en",
        theme: "system",
        timezone: "UTC",
      }).success,
    ).toBe(true);
    expect(
      notificationPreferencesSchema.safeParse({
        auditAlerts: true,
        emailEnabled: true,
        inAppEnabled: true,
        productUpdates: false,
        securityAlerts: true,
      }).success,
    ).toBe(true);
  });

  it("rejects unsupported preference values", () => {
    expect(
      preferencesSchema.safeParse({
        dateTimeFormat: "full",
        displayDensity: "dense",
        language: "de",
        theme: "neon",
        timezone: "",
      }).success,
    ).toBe(false);
  });
});
