import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  secretVersionQueryKeys,
  useCreateSecretVersionMutation,
  useRestoreSecretVersionMutation,
} from "@/features/secret-version";
import { createQueryClient } from "@/lib/api/query-client";

const secretVersionServiceMocks = vi.hoisted(() => ({
  createSecretVersion: vi.fn(async () => ({
    active: true,
    id: "version_2",
    secret_id: "secret_1",
    version: 2,
  })),
  restoreSecretVersion: vi.fn(async () => ({
    active: true,
    id: "version_1",
    secret_id: "secret_1",
    version: 1,
  })),
}));

vi.mock("@/features/secret-version/api/secret-version-service", () => ({
  createSecretVersion: secretVersionServiceMocks.createSecretVersion,
  restoreSecretVersion: secretVersionServiceMocks.restoreSecretVersion,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("secret version mutations", () => {
  it("creates versions through the service layer and invalidates secret-scoped cache", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(secretVersionQueryKeys.list("secret_1"), { items: [] });
    const { result } = renderHook(() => useCreateSecretVersionMutation("secret_1"), {
      wrapper: Wrapper,
    });

    result.current.mutate({
      makeCurrent: true,
      metadata: { source: "manual" },
      note: "rotation",
      value: "sensitive-value",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretVersionServiceMocks.createSecretVersion).toHaveBeenCalledWith("secret_1", {
      make_current: true,
      metadata: { source: "manual" },
      note: "rotation",
      value: "sensitive-value",
    });
    expect(queryClient.getQueryState(secretVersionQueryKeys.list("secret_1"))?.isInvalidated).toBe(
      true,
    );
  });

  it("restores versions through the documented extension endpoint", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(secretVersionQueryKeys.current("secret_1"), { id: "version_2" });
    const { result } = renderHook(() => useRestoreSecretVersionMutation("secret_1"), {
      wrapper: Wrapper,
    });

    result.current.mutate({ reason: "rollback approved", versionId: "version_1" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(secretVersionServiceMocks.restoreSecretVersion).toHaveBeenCalledWith(
      "secret_1",
      "version_1",
      {
        reason: "rollback approved",
      },
    );
    expect(
      queryClient.getQueryState(secretVersionQueryKeys.current("secret_1"))?.isInvalidated,
    ).toBe(true);
  });
});
