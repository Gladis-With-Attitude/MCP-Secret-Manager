import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useArchiveProjectMutation,
  useCreateProjectMutation,
  useUpdateProjectMutation,
} from "@/features/project/queries";
import { createQueryClient } from "@/lib/api/query-client";

const projectServiceMocks = vi.hoisted(() => ({
  archiveProject: vi.fn(async () => ({
    archived: true,
    id: "project_1",
    name: "Archived",
    vault_id: "vault_1",
  })),
  createProject: vi.fn(async () => ({
    id: "project_created",
    name: "Created",
    vault_id: "vault_1",
  })),
  updateProject: vi.fn(async () => ({ id: "project_1", name: "Updated", vault_id: "vault_1" })),
}));

vi.mock("@/features/project/api/project-service", () => ({
  archiveProject: projectServiceMocks.archiveProject,
  createProject: projectServiceMocks.createProject,
  updateProject: projectServiceMocks.updateProject,
}));

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = createQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("project mutations", () => {
  it("creates projects through the vault-scoped service layer", async () => {
    const { result } = renderHook(() => useCreateProjectMutation("vault_1"), { wrapper });

    result.current.mutate({ description: " notes ", name: " Created " });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(projectServiceMocks.createProject).toHaveBeenCalledWith("vault_1", {
      description: "notes",
      name: "Created",
    });
  });

  it("updates project metadata through the service layer", async () => {
    const { result } = renderHook(() => useUpdateProjectMutation("project_1"), { wrapper });

    result.current.mutate({ name: "Updated" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(projectServiceMocks.updateProject).toHaveBeenCalledWith("project_1", {
      description: undefined,
      name: "Updated",
    });
  });

  it("archives projects through the documented lifecycle endpoint", async () => {
    const { result } = renderHook(() => useArchiveProjectMutation(), { wrapper });

    result.current.mutate("project_1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(projectServiceMocks.archiveProject).toHaveBeenCalledWith("project_1");
  });
});
