"use client";

import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";

import type { Permission } from "../types/rbac";
import { PermissionGroup } from "./permission-group";

type PermissionMatrixProps = {
  disabled?: boolean;
  onPermissionToggle?: (permissionId: string, checked: boolean) => void;
  permissions: Permission[];
  readOnly?: boolean;
  selectedPermissionIds?: string[];
};

function groupPermissions(permissions: Permission[]) {
  return permissions.reduce<Record<string, Permission[]>>((groups, permission) => {
    const group = permission.group || permission.resource || "system";

    groups[group] = [...(groups[group] ?? []), permission];

    return groups;
  }, {});
}

function PermissionMatrix({
  disabled = false,
  onPermissionToggle,
  permissions,
  readOnly = false,
  selectedPermissionIds = [],
}: PermissionMatrixProps) {
  const groups = groupPermissions(permissions);
  const entries = Object.entries(groups).sort(([left], [right]) => left.localeCompare(right));

  if (!permissions.length) {
    return (
      <EmptyState
        description="No backend-defined permission is visible for the current user."
        title="No permissions"
      />
    );
  }

  return (
    <Grid columns={2}>
      {entries.map(([group, items]) => (
        <PermissionGroup
          disabled={disabled}
          group={group}
          key={group}
          onToggle={onPermissionToggle}
          permissions={items}
          readOnly={readOnly}
          selectedPermissionIds={selectedPermissionIds}
        />
      ))}
    </Grid>
  );
}

export { groupPermissions, PermissionMatrix };
export type { PermissionMatrixProps };
