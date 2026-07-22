"use client";

import type { ReactNode } from "react";

import { usePermission } from "../hooks/use-permission";
import type { Permission } from "../types/rbac";

type PermissionGuardProps = {
  children: ReactNode;
  fallback?: ReactNode;
  permission: string;
  permissions?: Permission[] | string[];
};

function PermissionGuard({
  children,
  fallback = null,
  permission,
  permissions,
}: PermissionGuardProps) {
  const isAllowed = usePermission(permissions, permission);

  return isAllowed ? <>{children}</> : <>{fallback}</>;
}

export { PermissionGuard };
export type { PermissionGuardProps };
