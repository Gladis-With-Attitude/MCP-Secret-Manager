import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useArchiveSecretMutation,
  useCreateSecretMutation,
  useUpdateSecretMutation,
} from "@/features/secret/queries";
import { createQueryClient } from "@/lib/api/query-client";

const secretServiceMocks = vi.hoisted(() => ({
  archiveSecret: vi.fn(async () => ({
    archived: true,
    id: "secret_1",
    key: "ARCHIVED_SECRET",
    project_id: "project_1",
  })),
  createSecret: vi.fn(async () => ({
    id: "secret_created",
    key: "API_TOKEN",
    project_id: "project_1",
  })),
  updateSecret: vi.fn(async () => ({ id: "secret_1", key: "API_TOKEN", project_id: "project_1" })),
}));

vi.mock("@/features/secret/api/secret-service", () => ({
  archiveSecret: secretServiceMocks.archiveSecret,
  createSecret: secretServiceMocks.createSecret,
  updateSecret: secretServiceMocks.updateSecret,
}));

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = createQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("secret mutations", () => {
  it("creates secrets through the project-scoped service layer", async () => {
    const { result } = renderHook(() => useCreateSecretMutation("project_1"), { wrapper });

    result.current.mutate({
      metadata: { owner: "platform" },
      name: "API_TOKEN",
      tags: ["production"],
      type: "token",
      value: "sensitive-value",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretServiceMocks.createSecret).toHaveBeenCalledWith("project_1", {
      description: undefined,
      key: "API_TOKEN",
      metadata: { owner: "platform" },
      tags: ["production"],
      type: "token",
    });
  });

  it("updates secret metadata without sending a value", async () => {
    const { result } = renderHook(() => useUpdateSecretMutation("secret_1"), { wrapper });

    result.current.mutate({
      metadata: {},
      name: "API_TOKEN",
      tags: [],
      type: "token",
      value: "must-not-be-sent",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretServiceMocks.updateSecret).toHaveBeenCalledWith("secret_1", {
      description: undefined,
      key: "API_TOKEN",
      metadata: {},
      tags: [],
      type: "token",
    });
  });

  it("archives secrets through the documented lifecycle endpoint", async () => {
    const { result } = renderHook(() => useArchiveSecretMutation(), { wrapper });

    result.current.mutate("secret_1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretServiceMocks.archiveSecret).toHaveBeenCalledWith("secret_1");
  });
});
