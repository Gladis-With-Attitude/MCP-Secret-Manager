import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  apiKeyQueryKeys,
  useCreateApiKeyMutation,
  useRevokeApiKeyMutation,
} from "@/features/api-key";
import { createQueryClient } from "@/lib/api/query-client";

const apiKeyServiceMocks = vi.hoisted(() => ({
  createApiKey: vi.fn(async () => ({
    api_key: "mcp_full_api_key",
    id: "key_1",
    key_prefix: "mcp",
    name: "agent",
  })),
  revokeApiKey: vi.fn(async () => ({
    id: "key_1",
    key_prefix: "mcp",
    name: "agent",
    revoked_at: "2026-01-01T00:00:00Z",
  })),
}));

vi.mock("@/features/api-key/api/api-key-service", () => ({
  createApiKey: apiKeyServiceMocks.createApiKey,
  revokeApiKey: apiKeyServiceMocks.revokeApiKey,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("api key mutations", () => {
  it("creates API keys and invalidates list cache while keeping value separate", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(apiKeyQueryKeys.list(), { items: [] });
    const { result } = renderHook(() => useCreateApiKeyMutation(), { wrapper: Wrapper });

    result.current.mutate({
      name: "agent",
      ownerId: "owner_1",
      ownerType: "service_account",
      permissions: ["secret.read"],
      scopes: ["global"],
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(apiKeyServiceMocks.createApiKey).toHaveBeenCalledWith({
      description: undefined,
      expires_at: undefined,
      name: "agent",
      owner_id: "owner_1",
      owner_type: "service_account",
      permissions: ["secret.read"],
      scopes: ["global"],
    });
    expect(result.current.data?.apiKeyValue).toBe("mcp_full_api_key");
    expect(JSON.stringify(result.current.data?.metadata)).not.toContain("mcp_full_api_key");
    expect(queryClient.getQueryState(apiKeyQueryKeys.list())?.isInvalidated).toBe(true);
  });

  it("revokes API keys without optimistic updates", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(apiKeyQueryKeys.list(), { items: [] });
    const { result } = renderHook(() => useRevokeApiKeyMutation(), { wrapper: Wrapper });

    result.current.mutate("key_1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(apiKeyServiceMocks.revokeApiKey).toHaveBeenCalledWith("key_1");
    expect(result.current.data?.status).toBe("revoked");
    expect(queryClient.getQueryState(apiKeyQueryKeys.list())?.isInvalidated).toBe(true);
  });
});
