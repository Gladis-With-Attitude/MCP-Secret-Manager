import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useActorRolesQuery,
  usePermissionListQuery,
  useRoleDetailQuery,
  useRoleListQuery,
} from "@/features/rbac";
import { createQueryClient } from "@/lib/api/query-client";

const rbacServiceMocks = vi.hoisted(() => ({
  getRole: vi.fn(async () => ({
    id: "role_1",
    name: "reader",
    permissions: [{ id: "perm_1", name: "role.read" }],
  })),
  listActorRoles: vi.fn(async () => ({
    actor_id: "user_1",
    data: [{ role_id: "role_1", role_name: "reader" }],
  })),
  listPermissions: vi.fn(async () => ({
    data: [{ id: "perm_1", name: "role.read" }],
  })),
  listRoles: vi.fn(async () => ({
    data: [{ id: "role_1", name: "reader" }],
    permissions: { create: true },
  })),
}));

vi.mock("@/features/rbac/api/rbac-service", () => ({
  getRole: rbacServiceMocks.getRole,
  listActorRoles: rbacServiceMocks.listActorRoles,
  listPermissions: rbacServiceMocks.listPermissions,
  listRoles: rbacServiceMocks.listRoles,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("RBAC queries", () => {
  it("loads role lists through the RBAC service", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useRoleListQuery({ query: "reader" }), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(rbacServiceMocks.listRoles).toHaveBeenCalledWith(
      expect.objectContaining({ q: "reader" }),
    );
    expect(result.current.data?.items[0]?.name).toBe("reader");
  });

  it("loads role details, permissions and actor roles", async () => {
    const { Wrapper } = createWrapper();
    const detail = renderHook(() => useRoleDetailQuery("role_1"), { wrapper: Wrapper });
    const permissions = renderHook(() => usePermissionListQuery(), { wrapper: Wrapper });
    const actorRoles = renderHook(() => useActorRolesQuery("user_1"), { wrapper: Wrapper });

    await waitFor(() => expect(detail.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(permissions.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(actorRoles.result.current.isSuccess).toBe(true));

    expect(detail.result.current.data?.permissions[0]?.name).toBe("role.read");
    expect(permissions.result.current.data?.[0]?.id).toBe("perm_1");
    expect(actorRoles.result.current.data?.items[0]?.roleName).toBe("reader");
  });
});
