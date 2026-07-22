import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useApiKeyDetailQuery, useApiKeyListQuery } from "@/features/api-key";
import { createQueryClient } from "@/lib/api/query-client";

const apiKeyServiceMocks = vi.hoisted(() => ({
  getApiKey: vi.fn(async () => ({
    id: "key_1",
    key_prefix: "mcp",
    name: "agent",
    token: "must-not-be-cached",
  })),
  listApiKeys: vi.fn(async () => ({
    data: [{ id: "key_1", key_prefix: "mcp", name: "agent", token: "must-not-be-cached" }],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
}));

vi.mock("@/features/api-key/api/api-key-service", () => ({
  getApiKey: apiKeyServiceMocks.getApiKey,
  listApiKeys: apiKeyServiceMocks.listApiKeys,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("api key queries", () => {
  it("loads list metadata without caching full token values", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useApiKeyListQuery(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(apiKeyServiceMocks.listApiKeys).toHaveBeenCalledWith({
      page: undefined,
      page_size: undefined,
      q: undefined,
      search: undefined,
      status: undefined,
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

  it("loads detail metadata without caching full token values", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useApiKeyDetailQuery("key_1"), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.name).toBe("agent");
    expect(
      JSON.stringify(
        queryClient
          .getQueryCache()
          .getAll()
          .map((query) => query.state.data),
      ),
    ).not.toContain("must-not-be-cached");
  });
});
