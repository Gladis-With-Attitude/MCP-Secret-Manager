import type { VaultListFilters } from "../types/vault";

const vaultQueryKeys = {
  all: ["vaults"] as const,
  detail: (vaultId: string) => [...vaultQueryKeys.details(), vaultId] as const,
  details: () => [...vaultQueryKeys.all, "detail"] as const,
  list: (filters: VaultListFilters = {}) => [...vaultQueryKeys.lists(), filters] as const,
  lists: () => [...vaultQueryKeys.all, "list"] as const,
};

export { vaultQueryKeys };
