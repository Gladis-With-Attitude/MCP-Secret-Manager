import { useMutation, useQueryClient } from "@tanstack/react-query";

import { archiveVault, createVault, updateVault } from "../api/vault-service";
import {
  mapVaultDtoToVault,
  mapVaultFormToCreateDto,
  mapVaultFormToUpdateDto,
} from "../mappers/vault-mappers";
import type { VaultFormValues } from "../types/vault";
import { vaultQueryKeys } from "./vault-keys";

function useCreateVaultMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: VaultFormValues) =>
      mapVaultDtoToVault(await createVault(mapVaultFormToCreateDto(values))),
    onSuccess: async (vault) => {
      queryClient.setQueryData(vaultQueryKeys.detail(vault.id), vault);
      await queryClient.invalidateQueries({ queryKey: vaultQueryKeys.lists() });
    },
    retry: false,
  });
}

function useUpdateVaultMutation(vaultId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: VaultFormValues) =>
      mapVaultDtoToVault(await updateVault(vaultId, mapVaultFormToUpdateDto(values))),
    onSuccess: async (vault) => {
      queryClient.setQueryData(vaultQueryKeys.detail(vault.id), vault);
      await queryClient.invalidateQueries({ queryKey: vaultQueryKeys.lists() });
    },
    retry: false,
  });
}

function useArchiveVaultMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (vaultId: string) => mapVaultDtoToVault(await archiveVault(vaultId)),
    onSuccess: async (vault) => {
      queryClient.setQueryData(vaultQueryKeys.detail(vault.id), vault);
      await queryClient.invalidateQueries({ queryKey: vaultQueryKeys.lists() });
    },
    retry: false,
  });
}

export { useArchiveVaultMutation, useCreateVaultMutation, useUpdateVaultMutation };
