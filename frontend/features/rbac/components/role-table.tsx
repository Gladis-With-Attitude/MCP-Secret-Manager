import Link from "next/link";

import { buttonVariants } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { Badge } from "@/components/display/badge";
import { cn } from "@/lib/utils";

import type { Role } from "../types/rbac";

type RoleTableProps = {
  roles: Role[];
};

const columns: DataTableColumn<Role>[] = [
  {
    cell: (role) => (
      <div>
        <div className="font-medium text-foreground">{role.name}</div>
        <div className="text-sm text-muted-foreground">{role.description ?? "No description"}</div>
      </div>
    ),
    header: "Role",
    key: "role",
  },
  {
    cell: (role) => (
      <Badge variant={role.kind === "system" ? "info" : "neutral"}>{role.kind}</Badge>
    ),
    header: "Kind",
    key: "kind",
  },
  {
    cell: (role) => role.permissionsCount,
    header: "Permissions",
    key: "permissions",
  },
  {
    cell: (role) => role.assignmentsCount,
    header: "Assignments",
    key: "assignments",
  },
  {
    cell: (role) => (
      <Badge variant={role.status === "active" ? "success" : "warning"}>{role.status}</Badge>
    ),
    header: "Status",
    key: "status",
  },
  {
    cell: (role) => (
      <Link
        className={cn(buttonVariants({ size: "compact", variant: "outline" }))}
        href={`/rbac/roles/${role.id}`}
      >
        Open
      </Link>
    ),
    className: "text-right",
    header: <span className="sr-only">Actions</span>,
    key: "actions",
  },
];

function RoleTable({ roles }: RoleTableProps) {
  return (
    <DataTable caption="RBAC roles" columns={columns} data={roles} getRowKey={(role) => role.id} />
  );
}

export { RoleTable };
export type { RoleTableProps };
