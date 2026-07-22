import type { QueryParams } from "@/lib/api";

import type {
  ApiKeyCreatedResponseDto,
  ApiKeyDto,
  ApiKeyListParamsDto,
  ApiKeyListResponseDto,
  ApiKeyPermissionDto,
  CreateApiKeyRequestDto,
} from "../api/api-key-dto";
import type {
  ApiKey,
  ApiKeyCreated,
  ApiKeyFormValues,
  ApiKeyList,
  ApiKeyListFilters,
  ApiKeyPermissions,
  ApiKeyStatus,
} from "../types/api-key";

const supportedApiKeyStatuses = new Set<ApiKeyStatus>(["active", "expired", "revoked", "unknown"]);

function normalizeApiKeyStatus(dto: ApiKeyDto): ApiKeyStatus {
  if (dto.revoked_at || dto.status === "revoked") {
    return "revoked";
  }

  if (dto.expires_at && Date.parse(dto.expires_at) <= Date.now()) {
    return "expired";
  }

  if (dto.status && supportedApiKeyStatuses.has(dto.status as ApiKeyStatus)) {
    return dto.status as ApiKeyStatus;
  }

  return "active";
}

function mapApiKeyPermissions(dto?: ApiKeyPermissionDto): ApiKeyPermissions {
  return {
    create: dto?.create,
    read: dto?.read,
    revoke: dto?.revoke,
  };
}

function mapApiKeyDtoToApiKey(dto: ApiKeyDto): ApiKey {
  return {
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    description: dto.description,
    expiresAt: dto.expires_at,
    grantedPermissions: dto.granted_permissions ?? dto.permission_names ?? [],
    id: dto.id,
    keyPrefix: dto.key_prefix,
    lastUsedAt: dto.last_used_at,
    name: dto.name ?? dto.key_prefix ?? "API Key",
    ownerId: dto.owner_id,
    ownerName: dto.owner_name,
    ownerType: dto.owner_type,
    permissions: mapApiKeyPermissions(dto.permissions),
    revokedAt: dto.revoked_at,
    roles: dto.roles ?? [],
    scopes: dto.scopes ?? [],
    status: normalizeApiKeyStatus(dto),
  };
}

function getApiKeyListItems(dto: ApiKeyListResponseDto): ApiKeyDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapApiKeyListResponseToApiKeyList(dto: ApiKeyListResponseDto): ApiKeyList {
  const items = getApiKeyListItems(dto).map(mapApiKeyDtoToApiKey);
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
    permissions: mapApiKeyPermissions(responsePermissions),
  };
}

function mapApiKeyCreatedDtoToApiKeyCreated(dto: ApiKeyCreatedResponseDto): ApiKeyCreated {
  const data = "data" in dto ? dto.data : dto;

  return {
    apiKeyValue: data.api_key ?? data.token,
    metadata: mapApiKeyDtoToApiKey(data),
  };
}

function mapApiKeyFiltersToParams(
  filters: ApiKeyListFilters = {},
): ApiKeyListParamsDto & QueryParams {
  return {
    page: filters.page,
    page_size: filters.pageSize,
    q: filters.search?.trim() || undefined,
    search: filters.search?.trim() || undefined,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
  };
}

function mapApiKeyFormToCreateDto(values: ApiKeyFormValues): CreateApiKeyRequestDto {
  return {
    description: values.description?.trim() || undefined,
    expires_at: values.expiresAt || undefined,
    name: values.name.trim(),
    owner_id: values.ownerId.trim(),
    owner_type: values.ownerType,
    permissions: values.permissions,
    scopes: values.scopes,
  };
}

function canUseApiKeyAction(
  permissions: ApiKeyPermissions,
  action: keyof ApiKeyPermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseApiKeyAction,
  mapApiKeyCreatedDtoToApiKeyCreated,
  mapApiKeyDtoToApiKey,
  mapApiKeyFiltersToParams,
  mapApiKeyFormToCreateDto,
  mapApiKeyListResponseToApiKeyList,
  mapApiKeyPermissions,
  normalizeApiKeyStatus,
};
