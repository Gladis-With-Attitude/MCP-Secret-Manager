import { describe, expect, it } from "vitest";

import { auditFiltersSchema } from "@/features/audit";

describe("audit validation", () => {
  it("accepts advanced audit filters", () => {
    expect(
      auditFiltersSchema.parse({
        action: "secret.read",
        actorId: "actor_1",
        endDate: "2026-01-02T00:00",
        query: "secret",
        resourceId: "secret_1",
        resourceType: "secret",
        result: "success",
        startDate: "2026-01-01T00:00",
      }),
    ).toMatchObject({ action: "secret.read", result: "success" });
  });

  it("rejects invalid action formats and inverted dates", () => {
    expect(() =>
      auditFiltersSchema.parse({
        action: "Secret Read",
        actorId: "",
        endDate: "2026-01-01T00:00",
        query: "",
        resourceId: "",
        resourceType: "",
        result: "all",
        startDate: "2026-01-02T00:00",
      }),
    ).toThrow();
  });
});
