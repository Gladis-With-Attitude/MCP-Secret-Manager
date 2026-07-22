import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useCurrentSecretVersionQuery,
  useSecretVersionDetailQuery,
  useSecretVersionListQuery,
} from "@/features/secret-version";
import { createQueryClient } from "@/lib/api/query-client";

const secretVersionServiceMocks = vi.hoisted(() => ({
  getCurrentSecretVersion: vi.fn(async () => ({
    active: true,
    id: "version_2",
    secret_id: "secret_1",
    value: "must-not-be-cached",
    version: 2,
  })),
  getSecretVersion: vi.fn(async () => ({
    id: "version_1",
    secret_id: "secret_1",
    value: "must-not-be-cached",
    version: 1,
  })),
  listSecretVersions: vi.fn(async () => ({
    data: [{ id: "version_1", secret_id: "secret_1", value: "must-not-be-cached", version: 1 }],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
}));

vi.mock("@/features/secret-version/api/secret-version-service", () => ({
  getCurrentSecretVersion: secretVersionServiceMocks.getCurrentSecretVersion,
  getSecretVersion: secretVersionServiceMocks.getSecretVersion,
  listSecretVersions: secretVersionServiceMocks.listSecretVersions,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("secret version queries", () => {
  it("loads version lists without caching returned values", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const { result } = renderHook(() => useSecretVersionListQuery("secret_1"), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretVersionServiceMocks.listSecretVersions).toHaveBeenCalledWith("secret_1", {
      current_only: undefined,
      page: undefined,
      page_size: undefined,
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

  it("loads detail and current metadata only", async () => {
    const { queryClient, Wrapper } = createWrapper();
    const detail = renderHook(() => useSecretVersionDetailQuery("secret_1", "version_1"), {
      wrapper: Wrapper,
    });
    const current = renderHook(() => useCurrentSecretVersionQuery("secret_1"), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(detail.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(current.result.current.isSuccess).toBe(true));

    expect(detail.result.current.data?.version).toBe(1);
    expect(current.result.current.data?.isCurrent).toBe(true);
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
