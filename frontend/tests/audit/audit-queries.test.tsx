import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useAuditDetailQuery, useAuditListQuery } from "@/features/audit";
import { createQueryClient } from "@/lib/api/query-client";

const auditServiceMocks = vi.hoisted(() => ({
  getAuditEvent: vi.fn(async () => ({
    action: "secret.read",
    actorId: "actor_1",
    actorType: "user",
    id: "event_1",
    metadata: {},
    resourceType: "secret",
    result: "success",
    timestamp: "2026-01-01T00:00:00Z",
  })),
  listAuditEvents: vi.fn(async () => [
    {
      action: "secret.read",
      actor_id: "actor_1",
      actor_type: "user",
      id: "event_1",
      metadata: { token: "must-not-be-cached", safe: "yes" },
      resource_type: "secret",
      result: "SUCCESS",
      timestamp: "2026-01-01T00:00:00Z",
    },
  ]),
}));

vi.mock("@/features/audit/api/audit-service", () => ({
  getAuditEvent: auditServiceMocks.getAuditEvent,
  listAuditEvents: auditServiceMocks.listAuditEvents,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("audit queries", () => {
  it("loads paginated audit metadata without caching sensitive-looking metadata", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useAuditListQuery({ limit: 100, offset: 0 }), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(auditServiceMocks.listAuditEvents).toHaveBeenCalledWith({
      action: undefined,
      actor_id: undefined,
      end_date: undefined,
      limit: 100,
      offset: 0,
      q: undefined,
      resource_id: undefined,
      resource_type: undefined,
      result: undefined,
      start_date: undefined,
    });
    expect(
      JSON.stringify(
        queryClient
          .getQueryCache()
          .getAll()
          .map((query) => query.state.data),
      ),
    ).not.toContain("must-not-be-cached");
  });

  it("loads audit event detail", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAuditDetailQuery("event_1"), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.id).toBe("event_1");
    expect(auditServiceMocks.getAuditEvent).toHaveBeenCalledWith("event_1");
  });
});
