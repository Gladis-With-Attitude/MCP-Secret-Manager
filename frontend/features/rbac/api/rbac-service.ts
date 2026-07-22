import { get, patch, post, remove } from "@/lib/api";

import type {
  CreateRoleDto,
  PermissionListResponseDto,
  RoleDto,
  RoleListParamsDto,
  RoleListResponseDto,
  UpdateRoleDto,
  UserRoleDto,
  UserRoleListResponseDto,
} from "./rbac-dto";

function listRoles(params?: RoleListParamsDto): Promise<RoleListResponseDto> {
  return get<RoleListResponseDto>("/v1/roles", { params });
}

function createRole(body: CreateRoleDto): Promise<RoleDto> {
  return post<RoleDto, CreateRoleDto>("/v1/roles", body);
}

function getRole(roleId: string): Promise<RoleDto> {
  return get<RoleDto>(`/v1/roles/${roleId}`);
}

function updateRole(roleId: string, body: UpdateRoleDto): Promise<RoleDto> {
  return patch<RoleDto, UpdateRoleDto>(`/v1/roles/${roleId}`, body);
}

function listPermissions(): Promise<PermissionListResponseDto> {
  return get<PermissionListResponseDto>("/v1/permissions");
}

function listActorRoles(actorId: string): Promise<UserRoleListResponseDto> {
  return get<UserRoleListResponseDto>(`/v1/actors/${actorId}/roles`);
}

function assignActorRole(actorId: string, roleId: string): Promise<UserRoleDto> {
  return post<UserRoleDto>(`/v1/actors/${actorId}/roles/${roleId}`);
}

function revokeActorRole(actorId: string, roleId: string): Promise<UserRoleDto | undefined> {
  return remove<UserRoleDto | undefined>(`/v1/actors/${actorId}/roles/${roleId}`);
}

const rbacService = {
  assignActorRole,
  createRole,
  getRole,
  listActorRoles,
  listPermissions,
  listRoles,
  revokeActorRole,
  updateRole,
};

export {
  assignActorRole,
  createRole,
  getRole,
  listActorRoles,
  listPermissions,
  listRoles,
  rbacService,
  revokeActorRole,
  updateRole,
};
