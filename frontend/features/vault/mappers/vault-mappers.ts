import type { QueryParams } from "@/lib/api";

import type {
  CreateVaultRequestDto,
  UpdateVaultRequestDto,
  VaultDto,
  VaultListParamsDto,
  VaultListResponseDto,
  VaultPermissionDto,
} from "../api/vault-dto";
import type {
  Vault,
  VaultFormValues,
  VaultList,
  VaultListFilters,
  VaultPermissions,
  VaultStatus,
} from "../types/vault";

function normalizeVaultStatus(dto: VaultDto): VaultStatus {
  if (dto.locked || dto.status === "locked") {
    return "locked";
  }

  if (dto.archived || dto.status === "archived") {
    return "archived";
  }

  return "active";
}

function mapVaultPermissions(dto?: VaultPermissionDto): VaultPermissions {
  return {
    archive: dto?.archive,
    create: dto?.create,
    delete: dto?.delete,
    lock: dto?.lock,
    read: dto?.read,
    update: dto?.update,
  };
}

function mapVaultDtoToVault(dto: VaultDto): Vault {
  const status = normalizeVaultStatus(dto);

  return {
    archived: status === "archived",
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    description: dto.description,
    id: dto.id,
    locked: status === "locked",
    name: dto.name,
    permissions: mapVaultPermissions(dto.permissions),
    projectCount: dto.project_count,
    secretCount: dto.secret_count,
    status,
    updatedAt: dto.updated_at,
  };
}

function getVaultListItems(dto: VaultListResponseDto): VaultDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapVaultListResponseToVaultList(dto: VaultListResponseDto): VaultList {
  const items = getVaultListItems(dto).map(mapVaultDtoToVault);
  const pagination = !Array.isArray(dto) && "pagination" in dto ? dto.pagination : {};
  const responsePermissions =
    !Array.isArray(dto) && "permissions" in dto ? dto.permissions : undefined;
  const permissions = mapVaultPermissions(responsePermissions);

  return {
    items,
    pagination: {
      hasNextPage: pagination.hasNextPage,
      hasPreviousPage: pagination.hasPreviousPage,
      page: pagination.page,
      pageSize: pagination.pageSize,
      total: pagination.total,
    },
    permissions,
  };
}

function mapVaultFiltersToParams(filters: VaultListFilters = {}): VaultListParamsDto & QueryParams {
  return {
    archived: filters.archived,
    locked: filters.locked,
    page: filters.page,
    page_size: filters.pageSize,
    search: filters.search?.trim() || undefined,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
  };
}

function mapVaultFormToCreateDto(values: VaultFormValues): CreateVaultRequestDto {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
  };
}

function mapVaultFormToUpdateDto(values: VaultFormValues): UpdateVaultRequestDto {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
  };
}

function canUseVaultAction(permissions: VaultPermissions, action: keyof VaultPermissions): boolean {
  return permissions[action] !== false;
}

export {
  canUseVaultAction,
  mapVaultDtoToVault,
  mapVaultFiltersToParams,
  mapVaultFormToCreateDto,
  mapVaultFormToUpdateDto,
  mapVaultListResponseToVaultList,
  mapVaultPermissions,
  normalizeVaultStatus,
};
