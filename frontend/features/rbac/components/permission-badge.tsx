import { Badge } from "@/components/display/badge";

import type { Permission } from "../types/rbac";

type PermissionBadgeProps = {
  permission: Permission;
};

function PermissionBadge({ permission }: PermissionBadgeProps) {
  return (
    <Badge
      aria-label={`${permission.name}${permission.sensitivity === "critical" ? ", critical permission" : ""}`}
      variant={permission.sensitivity === "critical" ? "danger" : "neutral"}
    >
      {permission.name}
    </Badge>
  );
}

export { PermissionBadge };
export type { PermissionBadgeProps };
