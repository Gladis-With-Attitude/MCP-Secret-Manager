import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  rbacQueryKeys,
  useAssignRoleMutation,
  useCreateRoleMutation,
  useRevokeRoleMutation,
  useUpdateRoleMutation,
} from "@/features/rbac";
import { createQueryClient } from "@/lib/api/query-client";

const rbacServiceMocks = vi.hoisted(() => ({
  assignActorRole: vi.fn(async () => ({
    actor_id: "user_1",
    role_id: "role_1",
    role_name: "reader",
  })),
  createRole: vi.fn(async () => ({
    id: "role_1",
    name: "reader",
    permission_ids: ["perm_1"],
  })),
  revokeActorRole: vi.fn(async () => undefined),
  updateRole: vi.fn(async () => ({
    id: "role_1",
    name: "reader",
    permission_ids: ["perm_1", "perm_2"],
  })),
}));

vi.mock("@/features/rbac/api/rbac-service", () => ({
  assignActorRole: rbacServiceMocks.assignActorRole,
  createRole: rbacServiceMocks.createRole,
  revokeActorRole: rbacServiceMocks.revokeActorRole,
  updateRole: rbacServiceMocks.updateRole,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("RBAC mutations", () => {
  it("creates roles and invalidates role lists", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(rbacQueryKeys.list(), { items: [] });
    const { result } = renderHook(() => useCreateRoleMutation(), { wrapper: Wrapper });

    result.current.mutate({ name: "reader", permissionIds: ["perm_1"] });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(rbacServiceMocks.createRole).toHaveBeenCalledWith({
      description: undefined,
      name: "reader",
      permission_ids: ["perm_1"],
    });
    expect(queryClient.getQueryState(rbacQueryKeys.list())?.isInvalidated).toBe(true);
  });

  it("updates roles without optimistic permission changes", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(rbacQueryKeys.list(), { items: [] });
    const { result } = renderHook(() => useUpdateRoleMutation("role_1"), { wrapper: Wrapper });

    result.current.mutate({ name: "reader", permissionIds: ["perm_1", "perm_2"] });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(rbacServiceMocks.updateRole).toHaveBeenCalledWith("role_1", {
      description: undefined,
      name: "reader",
      permission_ids: ["perm_1", "perm_2"],
    });
    expect(queryClient.getQueryState(rbacQueryKeys.list())?.isInvalidated).toBe(true);
  });

  it("assigns and revokes roles with actor cache invalidation", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(rbacQueryKeys.actorRoles("user_1"), { items: [] });
    const assign = renderHook(() => useAssignRoleMutation(), { wrapper: Wrapper });
    const revoke = renderHook(() => useRevokeRoleMutation("user_1"), { wrapper: Wrapper });

    assign.result.current.mutate({ actorId: "user_1", roleId: "role_1" });
    await waitFor(() => expect(assign.result.current.isSuccess).toBe(true));

    revoke.result.current.mutate("role_1");
    await waitFor(() => expect(revoke.result.current.isSuccess).toBe(true));

    expect(rbacServiceMocks.assignActorRole).toHaveBeenCalledWith("user_1", "role_1");
    expect(rbacServiceMocks.revokeActorRole).toHaveBeenCalledWith("user_1", "role_1");
    expect(queryClient.getQueryState(rbacQueryKeys.actorRoles("user_1"))?.isInvalidated).toBe(true);
  });
});
