import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useArchiveVaultMutation,
  useCreateVaultMutation,
  useUpdateVaultMutation,
} from "@/features/vault/queries";
import { createQueryClient } from "@/lib/api/query-client";

const vaultServiceMocks = vi.hoisted(() => ({
  archiveVault: vi.fn(async () => ({ archived: true, id: "vault_1", name: "Archived" })),
  createVault: vi.fn(async () => ({ id: "vault_created", name: "Created" })),
  updateVault: vi.fn(async () => ({ id: "vault_1", name: "Updated" })),
}));

vi.mock("@/features/vault/api/vault-service", () => ({
  archiveVault: vaultServiceMocks.archiveVault,
  createVault: vaultServiceMocks.createVault,
  updateVault: vaultServiceMocks.updateVault,
}));

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = createQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("vault mutations", () => {
  it("creates vaults through the service layer", async () => {
    const { result } = renderHook(() => useCreateVaultMutation(), { wrapper });

    result.current.mutate({ description: " notes ", name: " Created " });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(vaultServiceMocks.createVault).toHaveBeenCalledWith({
      description: "notes",
      name: "Created",
    });
  });

  it("updates vault metadata through the service layer", async () => {
    const { result } = renderHook(() => useUpdateVaultMutation("vault_1"), { wrapper });

    result.current.mutate({ name: "Updated" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(vaultServiceMocks.updateVault).toHaveBeenCalledWith("vault_1", {
      description: undefined,
      name: "Updated",
    });
  });

  it("archives vaults through the documented lifecycle endpoint", async () => {
    const { result } = renderHook(() => useArchiveVaultMutation(), { wrapper });

    result.current.mutate("vault_1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(vaultServiceMocks.archiveVault).toHaveBeenCalledWith("vault_1");
  });
});
