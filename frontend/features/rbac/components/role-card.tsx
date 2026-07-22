import Link from "next/link";

import { buttonVariants } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";
import { cn } from "@/lib/utils";

import type { Role } from "../types/rbac";
import { PermissionBadge } from "./permission-badge";

type RoleCardProps = {
  role: Role;
};

function RoleCard({ role }: RoleCardProps) {
  const criticalPermissions = role.permissions.filter(
    (permission) => permission.sensitivity === "critical",
  );

  return (
    <Card>
      <Stack gap="sm">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="truncate text-base font-semibold text-foreground">{role.name}</h3>
            <Text size="sm" tone="muted">
              {role.description ?? "No description provided."}
            </Text>
          </div>
          <span className="rounded-md border border-border px-2 py-1 text-xs capitalize text-muted-foreground">
            {role.kind}
          </span>
        </div>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <span>{role.permissionsCount} permissions</span>
          <span>{role.assignmentsCount} assignments</span>
        </div>
        {criticalPermissions.length ? (
          <div className="flex flex-wrap gap-2" aria-label="Critical permissions">
            {criticalPermissions.slice(0, 3).map((permission) => (
              <PermissionBadge key={permission.id} permission={permission} />
            ))}
          </div>
        ) : null}
        <Link
          className={cn(buttonVariants({ variant: "outline" }), "w-fit")}
          href={`/rbac/roles/${role.id}`}
        >
          Open role
        </Link>
      </Stack>
    </Card>
  );
}

export { RoleCard };
export type { RoleCardProps };
