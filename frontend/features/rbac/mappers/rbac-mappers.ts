import type { QueryParams } from "@/lib/api";

import type {
  CreateRoleDto,
  PermissionDto,
  PermissionListResponseDto,
  RbacPermissionDto,
  RoleDto,
  RoleListParamsDto,
  RoleListResponseDto,
  UpdateRoleDto,
  UserRoleDto,
  UserRoleListResponseDto,
} from "../api/rbac-dto";
import type {
  Permission,
  PermissionSensitivity,
  RbacAction,
  RbacActionPermissions,
  Role,
  RoleFilters,
  RoleFormValues,
  RoleKind,
  RoleList,
  RoleStatus,
  UserRole,
  UserRoleList,
} from "../types/rbac";
import { RBAC_DEFAULT_LIMIT, RBAC_MAX_LIMIT } from "../validation/rbac-schema";

const criticalPermissionPattern = /(delete|revoke|admin|role|permission|value|key|rotate|restore)/i;

function normalizeRoleKind(dto: RoleDto): RoleKind {
  if (dto.is_system || dto.kind === "system") {
    return "system";
  }

  return "custom";
}

function normalizeRoleStatus(status?: string | null): RoleStatus {
  return status === "inactive" ? "inactive" : "active";
}

function parsePermissionName(name: string): Pick<Permission, "action" | "group" | "resource"> {
  const [resource = "system", action = "access"] = name.split(".");

  return {
    action,
    group: resource,
    resource,
  };
}

function mapPermissionSensitivity(
  dto: PermissionDto,
  parsed: Pick<Permission, "action" | "resource">,
): PermissionSensitivity {
  if (dto.sensitivity === "critical") {
    return "critical";
  }

  return criticalPermissionPattern.test(`${dto.name} ${parsed.action} ${parsed.resource}`)
    ? "critical"
    : "standard";
}

function mapPermissionDtoToPermission(dto: PermissionDto): Permission {
  const parsed = parsePermissionName(dto.name);

  return {
    action: dto.action ?? parsed.action,
    description: dto.description ?? undefined,
    group: dto.group ?? parsed.group,
    id: dto.id,
    name: dto.name,
    resource: dto.resource ?? parsed.resource,
    sensitivity: mapPermissionSensitivity(dto, parsed),
  };
}

function mapRbacPermissions(dto?: RbacPermissionDto | null): RbacActionPermissions {
  return {
    assign: dto?.assign,
    create: dto?.create,
    read: dto?.read,
    revoke: dto?.revoke,
    update: dto?.update,
  };
}

function mapRoleDtoToRole(dto: RoleDto): Role {
  const permissions = (dto.permissions ?? []).map(mapPermissionDtoToPermission);
  const permissionIds = dto.permission_ids ?? permissions.map((permission) => permission.id);

  return {
    assignmentsCount: dto.assignments_count ?? 0,
    createdAt: dto.created_at ?? undefined,
    description: dto.description ?? undefined,
    id: dto.id,
    kind: normalizeRoleKind(dto),
    name: dto.name,
    permissionIds,
    permissions,
    permissionsCount: dto.permissions_count ?? permissionIds.length,
    status: normalizeRoleStatus(dto.status),
    updatedAt: dto.updated_at ?? undefined,
    uiPermissions: mapRbacPermissions(dto.ui_permissions),
  };
}

function getRoleListItems(dto: RoleListResponseDto): RoleDto[] {
  return Array.isArray(dto) ? dto : dto.data;
}

function normalizeRbacLimit(limit?: number): number {
  if (!limit) {
    return RBAC_DEFAULT_LIMIT;
  }

  return Math.min(RBAC_MAX_LIMIT, Math.max(1, limit));
}

function mapRoleListResponseToRoleList(
  dto: RoleListResponseDto,
  filters: RoleFilters = {},
): RoleList {
  const items = getRoleListItems(dto).map(mapRoleDtoToRole);
  const limit = normalizeRbacLimit(filters.limit);
  const offset = Math.max(0, filters.offset ?? 0);
  const responsePermissions = !Array.isArray(dto) ? dto.permissions : undefined;
  const total = !Array.isArray(dto) ? dto.total : undefined;

  return {
    items,
    pagination: {
      hasNextPage: total ? offset + limit < total : items.length >= limit,
      hasPreviousPage: offset > 0,
      limit,
      offset,
      total,
    },
    permissions: mapRbacPermissions(responsePermissions),
  };
}

function mapPermissionListResponseToPermissions(dto: PermissionListResponseDto): Permission[] {
  const items = Array.isArray(dto) ? dto : dto.data;

  return items.map(mapPermissionDtoToPermission);
}

function mapRoleFiltersToParams(filters: RoleFilters = {}): RoleListParamsDto & QueryParams {
  return {
    kind: filters.kind && filters.kind !== "all" ? filters.kind : undefined,
    limit: normalizeRbacLimit(filters.limit),
    offset: Math.max(0, filters.offset ?? 0),
    q: filters.query?.trim() || undefined,
    search: filters.query?.trim() || undefined,
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
  };
}

function mapRoleFormToCreateDto(values: RoleFormValues): CreateRoleDto {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
    permission_ids: values.permissionIds,
  };
}

function mapRoleFormToUpdateDto(values: RoleFormValues): UpdateRoleDto {
  return mapRoleFormToCreateDto(values);
}

function mapUserRoleDtoToUserRole(dto: UserRoleDto, fallbackActorId: string): UserRole {
  const roleName = dto.role_name ?? dto.role?.name ?? dto.role_id;

  return {
    actorId: dto.actor_id ?? fallbackActorId,
    assignedAt: dto.assigned_at ?? undefined,
    assignedBy: dto.assigned_by ?? undefined,
    id: dto.id ?? `${dto.actor_id ?? fallbackActorId}:${dto.role_id}`,
    roleId: dto.role_id,
    roleName,
    scopeId: dto.scope_id ?? undefined,
    scopeType:
      dto.scope_type === "vault" || dto.scope_type === "project" || dto.scope_type === "secret"
        ? dto.scope_type
        : "global",
    status: dto.status === "revoked" ? "revoked" : "active",
  };
}

function mapUserRoleListResponseToUserRoleList(
  dto: UserRoleListResponseDto,
  actorId: string,
): UserRoleList {
  const items = Array.isArray(dto) ? dto : dto.data;
  const permissions = Array.isArray(dto) ? undefined : dto.permissions;

  return {
    actorId: Array.isArray(dto) ? actorId : (dto.actor_id ?? actorId),
    items: items.map((item) => mapUserRoleDtoToUserRole(item, actorId)),
    permissions: mapRbacPermissions(permissions),
  };
}

function canUseRbacAction(permissions: RbacActionPermissions, action: RbacAction): boolean {
  return permissions[action] !== false;
}

function hasPermission(
  permissions: Permission[] | string[] | undefined,
  permissionName: string,
): boolean {
  if (!permissions?.length) {
    return false;
  }

  return permissions.some((permission) =>
    typeof permission === "string"
      ? permission === permissionName
      : permission.name === permissionName,
  );
}

function hasRole(roles: UserRole[] | string[] | undefined, roleName: string): boolean {
  if (!roles?.length) {
    return false;
  }

  return roles.some((role) =>
    typeof role === "string"
      ? role === roleName
      : role.roleName === roleName || role.roleId === roleName,
  );
}

export {
  canUseRbacAction,
  hasPermission,
  hasRole,
  mapPermissionDtoToPermission,
  mapPermissionListResponseToPermissions,
  mapRbacPermissions,
  mapRoleDtoToRole,
  mapRoleFiltersToParams,
  mapRoleFormToCreateDto,
  mapRoleFormToUpdateDto,
  mapRoleListResponseToRoleList,
  mapUserRoleDtoToUserRole,
  mapUserRoleListResponseToUserRoleList,
  normalizeRbacLimit,
};
