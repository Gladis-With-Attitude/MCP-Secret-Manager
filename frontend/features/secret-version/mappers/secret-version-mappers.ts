import type { QueryParams } from "@/lib/api";

import type {
  CreateSecretVersionRequestDto,
  SecretVersionDto,
  SecretVersionListParamsDto,
  SecretVersionListResponseDto,
  SecretVersionPermissionDto,
} from "../api/secret-version-dto";
import type {
  SecretVersion,
  SecretVersionFormValues,
  SecretVersionList,
  SecretVersionListFilters,
  SecretVersionPermissions,
  SecretVersionStatus,
} from "../types/secret-version";

const supportedSecretVersionStatuses = new Set<SecretVersionStatus>([
  "current",
  "active",
  "revoked",
  "deprecated",
  "destroyed",
  "unknown",
]);

function normalizeSecretVersionStatus(dto: SecretVersionDto): SecretVersionStatus {
  if (dto.is_current || dto.status === "current") {
    return "current";
  }

  if (dto.status && supportedSecretVersionStatuses.has(dto.status as SecretVersionStatus)) {
    return dto.status as SecretVersionStatus;
  }

  if (dto.active === true) {
    return "active";
  }

  return "unknown";
}

function mapSecretVersionPermissions(dto?: SecretVersionPermissionDto): SecretVersionPermissions {
  return {
    create: dto?.create,
    read: dto?.read,
    readValue: dto?.read_value,
    restore: dto?.restore,
    rotate: dto?.rotate,
    revoke: dto?.revoke,
  };
}

function mapSecretVersionDtoToSecretVersion(dto: SecretVersionDto): SecretVersion {
  const status = normalizeSecretVersionStatus(dto);

  return {
    algorithm: dto.algorithm,
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    cryptoSchemeVersion: dto.crypto_scheme_version,
    id: dto.id,
    isCurrent: dto.is_current === true || status === "current" || dto.active === true,
    keyReference: dto.key_reference,
    metadata: dto.metadata ?? {},
    note: dto.note,
    permissions: mapSecretVersionPermissions(dto.permissions),
    secretId: dto.secret_id,
    status,
    version: dto.version,
  };
}

function getSecretVersionListItems(dto: SecretVersionListResponseDto): SecretVersionDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapSecretVersionListResponseToSecretVersionList(
  dto: SecretVersionListResponseDto,
  secretId: string,
): SecretVersionList {
  const items = getSecretVersionListItems(dto)
    .map(mapSecretVersionDtoToSecretVersion)
    .sort((first, second) => second.version - first.version);
  const pagination = !Array.isArray(dto) && "pagination" in dto ? dto.pagination : {};
  const responsePermissions =
    !Array.isArray(dto) && "permissions" in dto ? dto.permissions : undefined;

  return {
    items,
    pagination: {
      hasNextPage: pagination.hasNextPage,
      hasPreviousPage: pagination.hasPreviousPage,
      page: pagination.page,
      pageSize: pagination.pageSize,
      total: pagination.total,
    },
    permissions: mapSecretVersionPermissions(responsePermissions),
    secretId,
  };
}

function mapSecretVersionFiltersToParams(
  filters: SecretVersionListFilters = {},
): SecretVersionListParamsDto & QueryParams {
  return {
    current_only: filters.currentOnly || undefined,
    page: filters.page,
    page_size: filters.pageSize,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
  };
}

function mapSecretVersionFormToCreateDto(
  values: SecretVersionFormValues,
): CreateSecretVersionRequestDto {
  return {
    make_current: values.makeCurrent,
    metadata: values.metadata,
    note: values.note?.trim() || undefined,
    value: values.value,
  };
}

function canUseSecretVersionAction(
  permissions: SecretVersionPermissions,
  action: keyof SecretVersionPermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseSecretVersionAction,
  mapSecretVersionDtoToSecretVersion,
  mapSecretVersionFiltersToParams,
  mapSecretVersionFormToCreateDto,
  mapSecretVersionListResponseToSecretVersionList,
  mapSecretVersionPermissions,
  normalizeSecretVersionStatus,
};
