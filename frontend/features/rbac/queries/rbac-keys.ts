import type { RoleFilters } from "../types/rbac";

const rbacQueryKeys = {
  actorRoles: (actorId: string) => ["rbac", "actors", actorId, "roles"] as const,
  detail: (roleId: string) => ["rbac", "roles", "detail", roleId] as const,
  list: (filters: RoleFilters = {}) => ["rbac", "roles", "list", filters] as const,
  lists: () => ["rbac", "roles", "list"] as const,
  permissions: () => ["rbac", "permissions"] as const,
  root: () => ["rbac"] as const,
};

export { rbacQueryKeys };
