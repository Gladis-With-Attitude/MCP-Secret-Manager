import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useVaultDetailQuery, useVaultListQuery } from "@/features/vault/queries";
import { createQueryClient } from "@/lib/api/query-client";

vi.mock("@/features/vault/api/vault-service", () => ({
  getVault: vi.fn(async () => ({ id: "vault_1", name: "Production" })),
  listVaults: vi.fn(async () => ({
    data: [{ id: "vault_1", name: "Production" }],
    pagination: { page: 1, pageSize: 20, total: 1 },
    success: true,
  })),
}));

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = createQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("vault queries", () => {
  it("loads and maps the vault list", async () => {
    const { result } = renderHook(() => useVaultListQuery(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items[0]?.name).toBe("Production");
  });

  it("loads and maps a vault detail", async () => {
    const { result } = renderHook(() => useVaultDetailQuery("vault_1"), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.id).toBe("vault_1");
  });
});
