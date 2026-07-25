import { describe, expect, it, vi } from "vitest";

import { getAuditEvent, listAuditEvents } from "@/features/audit/api/audit-service";

const httpMocks = vi.hoisted(() => ({
  get: vi.fn(async () => ({
    action: "vault.create",
    actor_type: "user",
    id: "event_1",
    metadata: { name: "Production" },
    resource_type: "vault",
    result: "SUCCESS",
    timestamp: "2026-07-25T12:00:00Z",
  })),
}));

vi.mock("@/lib/api", () => ({
  get: httpMocks.get,
}));

describe("audit service", () => {
  it("uses backend audit list and detail endpoints", async () => {
    await listAuditEvents({ action: "vault.create", q: "Production" });
    const event = await getAuditEvent("event_1");

    expect(httpMocks.get).toHaveBeenNthCalledWith(1, "/v1/audit/events", {
      params: { action: "vault.create", q: "Production" },
    });
    expect(httpMocks.get).toHaveBeenNthCalledWith(2, "/v1/audit/events/event_1");
    expect(event).toMatchObject({
      action: "vault.create",
      id: "event_1",
      result: "success",
    });
  });
});
