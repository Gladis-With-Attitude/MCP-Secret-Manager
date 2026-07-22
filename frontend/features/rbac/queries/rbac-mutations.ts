import { useMutation, useQueryClient } from "@tanstack/react-query";

import { assignActorRole, createRole, revokeActorRole, updateRole } from "../api/rbac-service";
import {
  mapRoleDtoToRole,
  mapRoleFormToCreateDto,
  mapRoleFormToUpdateDto,
  mapUserRoleDtoToUserRole,
} from "../mappers/rbac-mappers";
import type { RoleAssignmentValues, RoleFormValues } from "../types/rbac";
import { rbacQueryKeys } from "./rbac-keys";

function useCreateRoleMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: RoleFormValues) =>
      mapRoleDtoToRole(await createRole(mapRoleFormToCreateDto(values))),
    onSuccess: async (role) => {
      queryClient.setQueryData(rbacQueryKeys.detail(role.id), role);
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.lists() });
    },
    retry: false,
  });
}

function useUpdateRoleMutation(roleId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: RoleFormValues) =>
      mapRoleDtoToRole(await updateRole(roleId, mapRoleFormToUpdateDto(values))),
    onSuccess: async (role) => {
      queryClient.setQueryData(rbacQueryKeys.detail(role.id), role);
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.lists() });
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.permissions() });
    },
    retry: false,
  });
}

function useAssignRoleMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ actorId, roleId }: RoleAssignmentValues) =>
      mapUserRoleDtoToUserRole(await assignActorRole(actorId, roleId), actorId),
    onSuccess: async (assignment) => {
      await queryClient.invalidateQueries({
        queryKey: rbacQueryKeys.actorRoles(assignment.actorId),
      });
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.lists() });
    },
    retry: false,
  });
}

function useRevokeRoleMutation(actorId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (roleId: string) => {
      const response = await revokeActorRole(actorId, roleId);

      return response ? mapUserRoleDtoToUserRole(response, actorId) : { actorId, roleId };
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.actorRoles(actorId) });
      await queryClient.invalidateQueries({ queryKey: rbacQueryKeys.lists() });
    },
    retry: false,
  });
}

export {
  useAssignRoleMutation,
  useCreateRoleMutation,
  useRevokeRoleMutation,
  useUpdateRoleMutation,
};
