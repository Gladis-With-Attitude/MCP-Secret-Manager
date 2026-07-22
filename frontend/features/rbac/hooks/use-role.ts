import { hasRole } from "../mappers/rbac-mappers";
import type { UserRole } from "../types/rbac";

function useRole(roles: UserRole[] | string[] | undefined, roleName: string) {
  return hasRole(roles, roleName);
}

export { useRole };
