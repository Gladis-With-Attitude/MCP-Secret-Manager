import { describe, expect, it } from "vitest";

import {
  mapAuditEventDtoToAuditEvent,
  mapAuditFiltersToParams,
  mapAuditListResponseToAuditList,
  sanitizeAuditMetadata,
} from "@/features/audit";

describe("audit mappers", () => {
  it("maps audit events and removes sensitive-looking metadata fields", () => {
    const event = mapAuditEventDtoToAuditEvent({
      action: "secret.read",
      actor_id: "actor_1",
      actor_type: "user",
      id: "event_1",
      metadata: {
        reason: "allowed",
        secret_value: "must-not-render",
        token: "must-not-render",
      },
      resource_id: "secret_1",
      resource_type: "secret",
      result: "SUCCESS",
      timestamp: "2026-01-01T00:00:00Z",
    });

    expect(event).toMatchObject({
      action: "secret.read",
      actorId: "actor_1",
      id: "event_1",
      result: "success",
    });
    expect(event.metadata).toEqual({ reason: "allowed" });
    expect(JSON.stringify(event)).not.toContain("must-not-render");
  });

  it("maps paginated array responses and stable limit offset pagination", () => {
    const list = mapAuditListResponseToAuditList(
      [
        {
          action: "vault.create",
          actor_type: "user",
          id: "event_1",
          resource_type: "vault",
          result: "FAILURE",
          timestamp: "2026-01-01T00:00:00Z",
        },
      ],
      { limit: 100, offset: 100 },
    );

    expect(list.events[0]?.result).toBe("failure");
    expect(list.pagination).toEqual({
      hasNextPage: false,
      hasPreviousPage: true,
      limit: 100,
      offset: 100,
    });
  });

  it("maps filters to backend query params", () => {
    expect(
      mapAuditFiltersToParams({
        action: "secret.read",
        actorId: "actor_1",
        limit: 50,
        offset: 25,
        query: "secret_1",
        resourceType: "secret",
        result: "failure",
      }),
    ).toEqual({
      action: "secret.read",
      actor_id: "actor_1",
      end_date: undefined,
      limit: 50,
      offset: 25,
      q: "secret_1",
      resource_id: undefined,
      resource_type: "secret",
      result: "FAILURE",
      start_date: undefined,
    });
  });

  it("sanitizes metadata defensively", () => {
    expect(
      sanitizeAuditMetadata({
        api_key: "hidden",
        safe: "visible",
      }),
    ).toEqual({ safe: "visible" });
  });
});
