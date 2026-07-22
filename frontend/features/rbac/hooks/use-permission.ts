import { hasPermission } from "../mappers/rbac-mappers";
import type { Permission } from "../types/rbac";

function usePermission(permissions: Permission[] | string[] | undefined, permissionName: string) {
  return hasPermission(permissions, permissionName);
}

export { usePermission };
