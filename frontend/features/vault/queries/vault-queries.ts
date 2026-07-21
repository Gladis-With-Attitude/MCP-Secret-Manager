import { useQuery } from "@tanstack/react-query";

import { getVault, listVaults } from "../api/vault-service";
import {
  mapVaultDtoToVault,
  mapVaultFiltersToParams,
  mapVaultListResponseToVaultList,
} from "../mappers/vault-mappers";
import type { VaultListFilters } from "../types/vault";
import { vaultQueryKeys } from "./vault-keys";

function useVaultListQuery(filters: VaultListFilters = {}) {
  return useQuery({
    queryFn: async () =>
      mapVaultListResponseToVaultList(await listVaults(mapVaultFiltersToParams(filters))),
    queryKey: vaultQueryKeys.list(filters),
  });
}

function useVaultDetailQuery(vaultId: string) {
  return useQuery({
    enabled: Boolean(vaultId),
    queryFn: async () => mapVaultDtoToVault(await getVault(vaultId)),
    queryKey: vaultQueryKeys.detail(vaultId),
  });
}

export { useVaultDetailQuery, useVaultListQuery };
