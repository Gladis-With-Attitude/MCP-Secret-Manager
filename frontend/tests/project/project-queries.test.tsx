import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useProjectDetailQuery, useProjectListQuery } from "@/features/project/queries";
import { createQueryClient } from "@/lib/api/query-client";

const projectServiceMocks = vi.hoisted(() => ({
  getProject: vi.fn(async () => ({ id: "project_1", name: "API", vault_id: "vault_1" })),
  listProjects: vi.fn(async () => ({
    data: [{ id: "project_1", name: "API", vault_id: "vault_1" }],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
}));

vi.mock("@/features/project/api/project-service", () => ({
  getProject: projectServiceMocks.getProject,
  listProjects: projectServiceMocks.listProjects,
}));

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = createQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("project queries", () => {
  it("loads and maps the vault-scoped project list", async () => {
    const { result } = renderHook(() => useProjectListQuery("vault_1"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(projectServiceMocks.listProjects).toHaveBeenCalledWith("vault_1", {
      archived: undefined,
      page: undefined,
      page_size: undefined,
      search: undefined,
      status: undefined,
    });
    expect(result.current.data?.items[0]?.name).toBe("API");
  });

  it("loads and maps a project detail", async () => {
    const { result } = renderHook(() => useProjectDetailQuery("project_1"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.vaultId).toBe("vault_1");
  });
});
