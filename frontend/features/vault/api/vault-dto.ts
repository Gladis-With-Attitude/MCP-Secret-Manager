import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

type VaultPermissionDto = {
  archive?: boolean;
  create?: boolean;
  delete?: boolean;
  lock?: boolean;
  read?: boolean;
  update?: boolean;
};

type VaultDto = {
  archived?: boolean;
  created_at?: string | null;
  created_by?: string | null;
  description?: string | null;
  id: string;
  locked?: boolean;
  name: string;
  permissions?: VaultPermissionDto;
  project_count?: number | null;
  secret_count?: number | null;
  status?: string | null;
  updated_at?: string | null;
};

type VaultListEnvelopeDto = PaginatedResponse<VaultDto> & {
  permissions?: VaultPermissionDto;
};

type VaultListResponseDto = VaultListEnvelopeDto | SuccessResponse<VaultDto[]> | VaultDto[];

type CreateVaultRequestDto = {
  description?: string;
  name: string;
};

type UpdateVaultRequestDto = {
  description?: string;
  name: string;
};

type VaultListParamsDto = {
  archived?: boolean;
  locked?: boolean;
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
};

type VaultActionResponseDto = SuccessResponse<VaultDto> | VaultDto;

export type {
  CreateVaultRequestDto,
  UpdateVaultRequestDto,
  VaultActionResponseDto,
  VaultDto,
  VaultListParamsDto,
  VaultListResponseDto,
  VaultPermissionDto,
};
