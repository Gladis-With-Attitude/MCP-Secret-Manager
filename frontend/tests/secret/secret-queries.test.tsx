import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useSecretDetailQuery, useSecretListQuery } from "@/features/secret/queries";
import { createQueryClient } from "@/lib/api/query-client";

const secretServiceMocks = vi.hoisted(() => ({
  getSecret: vi.fn(async () => ({
    id: "secret_1",
    key: "API_TOKEN",
    project_id: "project_1",
    value: "must-not-be-cached",
  })),
  listSecrets: vi.fn(async () => ({
    data: [
      { id: "secret_1", key: "API_TOKEN", project_id: "project_1", value: "must-not-be-cached" },
    ],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
  searchSecrets: vi.fn(async () => ({
    data: [{ id: "secret_1", key: "API_TOKEN", project_id: "project_1" }],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
}));

vi.mock("@/features/secret/api/secret-service", () => ({
  getSecret: secretServiceMocks.getSecret,
  listSecrets: secretServiceMocks.listSecrets,
  searchSecrets: secretServiceMocks.searchSecrets,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("secret queries", () => {
  it("loads project-scoped secret metadata without caching values", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useSecretListQuery("project_1"), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretServiceMocks.listSecrets).toHaveBeenCalledWith("project_1", {
      archived: undefined,
      page: undefined,
      page_size: undefined,
      provider: undefined,
      q: undefined,
      search: undefined,
      status: undefined,
      type: undefined,
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

  it("uses search service when search metadata is provided", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useSecretListQuery("project_1", { search: "api" }), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretServiceMocks.searchSecrets).toHaveBeenCalled();
  });

  it("loads a secret detail as metadata only", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useSecretDetailQuery("secret_1"), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.name).toBe("API_TOKEN");
    expect(
      JSON.stringify(queryClient.getQueryData(["secrets", "detail", "secret_1"])),
    ).not.toContain("must-not-be-cached");
  });
});
