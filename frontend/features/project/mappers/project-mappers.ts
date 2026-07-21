import type { QueryParams } from "@/lib/api";

import type {
  CreateProjectRequestDto,
  ProjectDto,
  ProjectListParamsDto,
  ProjectListResponseDto,
  ProjectPermissionDto,
  UpdateProjectRequestDto,
} from "../api/project-dto";
import type {
  Project,
  ProjectFormValues,
  ProjectList,
  ProjectListFilters,
  ProjectPermissions,
  ProjectStatus,
} from "../types/project";

function normalizeProjectStatus(dto: ProjectDto): ProjectStatus {
  if (dto.archived || dto.status === "archived") {
    return "archived";
  }

  return "active";
}

function mapProjectPermissions(dto?: ProjectPermissionDto): ProjectPermissions {
  return {
    archive: dto?.archive,
    create: dto?.create,
    delete: dto?.delete,
    read: dto?.read,
    update: dto?.update,
  };
}

function mapProjectDtoToProject(dto: ProjectDto): Project {
  const status = normalizeProjectStatus(dto);

  return {
    archived: status === "archived",
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    description: dto.description,
    id: dto.id,
    name: dto.name,
    permissions: mapProjectPermissions(dto.permissions),
    secretCount: dto.secret_count,
    status,
    updatedAt: dto.updated_at,
    vaultId: dto.vault_id,
    vaultName: dto.vault_name,
    versionCount: dto.version_count,
  };
}

function getProjectListItems(dto: ProjectListResponseDto): ProjectDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapProjectListResponseToProjectList(
  dto: ProjectListResponseDto,
  vaultId: string,
): ProjectList {
  const items = getProjectListItems(dto).map(mapProjectDtoToProject);
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
    permissions: mapProjectPermissions(responsePermissions),
    vaultId,
  };
}

function mapProjectFiltersToParams(
  filters: ProjectListFilters = {},
): ProjectListParamsDto & QueryParams {
  return {
    archived: filters.archived,
    page: filters.page,
    page_size: filters.pageSize,
    search: filters.search?.trim() || undefined,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
  };
}

function mapProjectFormToCreateDto(values: ProjectFormValues): CreateProjectRequestDto {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
  };
}

function mapProjectFormToUpdateDto(values: ProjectFormValues): UpdateProjectRequestDto {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
  };
}

function canUseProjectAction(
  permissions: ProjectPermissions,
  action: keyof ProjectPermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseProjectAction,
  mapProjectDtoToProject,
  mapProjectFiltersToParams,
  mapProjectFormToCreateDto,
  mapProjectFormToUpdateDto,
  mapProjectListResponseToProjectList,
  mapProjectPermissions,
  normalizeProjectStatus,
};
