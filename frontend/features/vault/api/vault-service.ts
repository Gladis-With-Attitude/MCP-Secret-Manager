import { get, patch, post } from "@/lib/api";

import type {
  CreateVaultRequestDto,
  UpdateVaultRequestDto,
  VaultActionResponseDto,
  VaultDto,
  VaultListParamsDto,
  VaultListResponseDto,
} from "./vault-dto";

function unwrapVaultResponse(response: VaultActionResponseDto): VaultDto {
  return "data" in response ? response.data : response;
}

async function listVaults(params?: VaultListParamsDto): Promise<VaultListResponseDto> {
  return get<VaultListResponseDto>("/v1/vaults", { params });
}

async function getVault(vaultId: string): Promise<VaultDto> {
  const response = await get<VaultActionResponseDto>(`/v1/vaults/${vaultId}`);

  return unwrapVaultResponse(response);
}

async function createVault(payload: CreateVaultRequestDto): Promise<VaultDto> {
  const response = await post<VaultActionResponseDto, CreateVaultRequestDto>("/v1/vaults", payload);

  return unwrapVaultResponse(response);
}

async function updateVault(vaultId: string, payload: UpdateVaultRequestDto): Promise<VaultDto> {
  const response = await patch<VaultActionResponseDto, UpdateVaultRequestDto>(
    `/v1/vaults/${vaultId}`,
    payload,
  );

  return unwrapVaultResponse(response);
}

async function archiveVault(vaultId: string): Promise<VaultDto> {
  const response = await post<VaultActionResponseDto>(`/v1/vaults/${vaultId}/archive`);

  return unwrapVaultResponse(response);
}

const vaultService = {
  archiveVault,
  createVault,
  getVault,
  listVaults,
  updateVault,
};

export { archiveVault, createVault, getVault, listVaults, updateVault, vaultService };
