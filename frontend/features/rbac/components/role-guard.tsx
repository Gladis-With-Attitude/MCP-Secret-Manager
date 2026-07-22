"use client";

import type { ReactNode } from "react";

import { useRole } from "../hooks/use-role";
import type { UserRole } from "../types/rbac";

type RoleGuardProps = {
  children: ReactNode;
  fallback?: ReactNode;
  role: string;
  roles?: UserRole[] | string[];
};

function RoleGuard({ children, fallback = null, role, roles }: RoleGuardProps) {
  const isAllowed = useRole(roles, role);

  return isAllowed ? <>{children}</> : <>{fallback}</>;
}

export { RoleGuard };
export type { RoleGuardProps };
