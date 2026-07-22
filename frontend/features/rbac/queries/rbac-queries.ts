import { useQuery } from "@tanstack/react-query";

import { getRole, listActorRoles, listPermissions, listRoles } from "../api/rbac-service";
import {
  mapPermissionListResponseToPermissions,
  mapRoleDtoToRole,
  mapRoleFiltersToParams,
  mapRoleListResponseToRoleList,
  mapUserRoleListResponseToUserRoleList,
} from "../mappers/rbac-mappers";
import type { RoleFilters } from "../types/rbac";
import { rbacQueryKeys } from "./rbac-keys";

function useRoleListQuery(filters: RoleFilters = {}) {
  return useQuery({
    queryFn: async () =>
      mapRoleListResponseToRoleList(await listRoles(mapRoleFiltersToParams(filters)), filters),
    queryKey: rbacQueryKeys.list(filters),
  });
}

function useRoleDetailQuery(roleId: string) {
  return useQuery({
    enabled: Boolean(roleId),
    queryFn: async () => mapRoleDtoToRole(await getRole(roleId)),
    queryKey: rbacQueryKeys.detail(roleId),
    retry: false,
  });
}

function usePermissionListQuery() {
  return useQuery({
    queryFn: async () => mapPermissionListResponseToPermissions(await listPermissions()),
    queryKey: rbacQueryKeys.permissions(),
  });
}

function useActorRolesQuery(actorId: string) {
  return useQuery({
    enabled: Boolean(actorId),
    queryFn: async () =>
      mapUserRoleListResponseToUserRoleList(await listActorRoles(actorId), actorId),
    queryKey: rbacQueryKeys.actorRoles(actorId),
    retry: false,
  });
}

export { useActorRolesQuery, usePermissionListQuery, useRoleDetailQuery, useRoleListQuery };
