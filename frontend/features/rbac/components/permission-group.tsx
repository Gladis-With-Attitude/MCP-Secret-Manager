"use client";

import { Checkbox } from "@/components/forms/checkbox";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { Permission } from "../types/rbac";
import { PermissionBadge } from "./permission-badge";

type PermissionGroupProps = {
  disabled?: boolean;
  group: string;
  onToggle?: (permissionId: string, checked: boolean) => void;
  permissions: Permission[];
  readOnly?: boolean;
  selectedPermissionIds?: string[];
};

function PermissionGroup({
  disabled = false,
  group,
  onToggle,
  permissions,
  readOnly = false,
  selectedPermissionIds = [],
}: PermissionGroupProps) {
  return (
    <section
      aria-label={`${group} permissions`}
      className="rounded-md border border-border bg-background p-4"
    >
      <Stack gap="sm">
        <div>
          <h3 className="text-sm font-semibold capitalize text-foreground">{group}</h3>
          <Text size="sm" tone="muted">
            {permissions.length} permission{permissions.length === 1 ? "" : "s"}
          </Text>
        </div>
        <div className="grid gap-3">
          {permissions.map((permission) => {
            const checked = selectedPermissionIds.includes(permission.id);
            const description =
              permission.description ?? `${permission.action} on ${permission.resource}`;

            return (
              <div className="flex items-start justify-between gap-3" key={permission.id}>
                <div className="min-w-0 space-y-1">
                  <PermissionBadge permission={permission} />
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
                {readOnly ? null : (
                  <Checkbox
                    aria-label={`Select ${permission.name}`}
                    checked={checked}
                    disabled={disabled}
                    onCheckedChange={(value) => onToggle?.(permission.id, value === true)}
                  />
                )}
              </div>
            );
          })}
        </div>
      </Stack>
    </section>
  );
}

export { PermissionGroup };
export type { PermissionGroupProps };
