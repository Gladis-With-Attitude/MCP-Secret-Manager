import type { QueryParams } from "@/lib/api";

import type {
  CreateSecretRequestDto,
  SecretDto,
  SecretListParamsDto,
  SecretListResponseDto,
  SecretPermissionDto,
  SecretValueResponseDto,
  UpdateSecretRequestDto,
} from "../api/secret-dto";
import type {
  Secret,
  SecretFormValues,
  SecretList,
  SecretListFilters,
  SecretPermissions,
  SecretStatus,
  SecretType,
  SecretValueResult,
} from "../types/secret";
import { parseSecretMetadata, parseSecretTags } from "../validation/secret-schema";

const supportedSecretTypes = new Set<SecretType>([
  "api_key",
  "certificate",
  "generic",
  "password",
  "token",
  "other",
]);

function normalizeSecretStatus(dto: SecretDto): SecretStatus {
  if (dto.status === "deleted") {
    return "deleted";
  }

  if (dto.archived || dto.status === "archived") {
    return "archived";
  }

  if (dto.status === "missing_version") {
    return "missing_version";
  }

  return "active";
}

function normalizeSecretType(type?: string | null): SecretType {
  return type && supportedSecretTypes.has(type as SecretType) ? (type as SecretType) : "generic";
}

function mapSecretPermissions(dto?: SecretPermissionDto): SecretPermissions {
  return {
    archive: dto?.archive,
    create: dto?.create,
    delete: dto?.delete,
    read: dto?.read,
    readValue: dto?.read_value,
    update: dto?.update,
  };
}

function mapSecretDtoToSecret(dto: SecretDto): Secret {
  const status = normalizeSecretStatus(dto);

  return {
    archived: status === "archived",
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    currentVersion: dto.current_version,
    description: dto.description,
    id: dto.id,
    lastVersionAt: dto.last_version_at,
    metadata: dto.metadata ?? {},
    name: dto.name ?? dto.key ?? "UNKNOWN_SECRET",
    permissions: mapSecretPermissions(dto.permissions),
    projectId: dto.project_id,
    projectName: dto.project_name,
    provider: dto.provider,
    status,
    tags: dto.tags ?? [],
    type: normalizeSecretType(dto.type),
    updatedAt: dto.updated_at,
    vaultId: dto.vault_id,
    vaultName: dto.vault_name,
    versionCount: dto.version_count,
  };
}

function getSecretListItems(dto: SecretListResponseDto): SecretDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapSecretListResponseToSecretList(
  dto: SecretListResponseDto,
  projectId: string,
): SecretList {
  const items = getSecretListItems(dto).map(mapSecretDtoToSecret);
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
    permissions: mapSecretPermissions(responsePermissions),
    projectId,
  };
}

function mapSecretFiltersToParams(
  filters: SecretListFilters = {},
): SecretListParamsDto & QueryParams {
  return {
    archived: filters.archived,
    page: filters.page,
    page_size: filters.pageSize,
    provider: filters.provider?.trim() || undefined,
    q: filters.search?.trim() || undefined,
    search: filters.search?.trim() || undefined,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
    type: filters.type && filters.type !== "all" ? filters.type : undefined,
  };
}

function mapSecretFormToCreateDto(values: SecretFormValues): CreateSecretRequestDto {
  return {
    description: values.description?.trim() || undefined,
    key: values.name.trim(),
    metadata: values.metadata,
    tags: values.tags,
    type: values.type,
  };
}

function mapSecretFormToUpdateDto(values: SecretFormValues): UpdateSecretRequestDto {
  return {
    description: values.description?.trim() || undefined,
    key: values.name.trim(),
    metadata: values.metadata,
    tags: values.tags,
    type: values.type,
  };
}

function mapSecretSchemaValuesToFormValues(values: {
  description?: string;
  metadataJson: string;
  name: string;
  tagsInput: string;
  type: SecretType;
  value?: string;
}): SecretFormValues {
  return {
    description: values.description?.trim() || undefined,
    metadata: parseSecretMetadata(values.metadataJson),
    name: values.name.trim(),
    tags: parseSecretTags(values.tagsInput),
    type: values.type,
    value: values.value,
  };
}

function mapSecretToFormDefaults(secret?: Secret) {
  return {
    description: secret?.description ?? "",
    metadataJson: secret ? JSON.stringify(secret.metadata, null, 2) : "",
    name: secret?.name ?? "",
    tagsInput: secret?.tags.join(", ") ?? "",
    type: secret?.type ?? "generic",
    value: "",
  };
}

function mapSecretValueResponseToResult(dto: SecretValueResponseDto): SecretValueResult {
  const data = "data" in dto ? dto.data : dto;

  return {
    expiresAt: data.expires_at,
    value: data.value,
  };
}

function canUseSecretAction(
  permissions: SecretPermissions,
  action: keyof SecretPermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseSecretAction,
  mapSecretDtoToSecret,
  mapSecretFiltersToParams,
  mapSecretFormToCreateDto,
  mapSecretFormToUpdateDto,
  mapSecretListResponseToSecretList,
  mapSecretPermissions,
  mapSecretSchemaValuesToFormValues,
  mapSecretToFormDefaults,
  mapSecretValueResponseToResult,
  normalizeSecretStatus,
  normalizeSecretType,
};
