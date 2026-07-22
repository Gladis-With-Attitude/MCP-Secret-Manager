import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { Badge } from "@/components/display/badge";
import { EmptyState } from "@/components/feedback/empty-state";

import type { UserRole } from "../types/rbac";

type UserRoleListProps = {
  canRevoke?: boolean;
  onRevoke?: (role: UserRole) => void;
  userRoles: UserRole[];
};

function UserRoleList({ canRevoke = false, onRevoke, userRoles }: UserRoleListProps) {
  const columns: DataTableColumn<UserRole>[] = [
    {
      cell: (role) => <span className="font-medium">{role.roleName}</span>,
      header: "Role",
      key: "role",
    },
    {
      cell: (role) => <Badge variant="neutral">{role.scopeType}</Badge>,
      header: "Scope",
      key: "scope",
    },
    {
      cell: (role) => role.assignedBy ?? "Backend",
      header: "Assigned by",
      key: "assignedBy",
    },
    {
      cell: (role) => (
        <Badge variant={role.status === "active" ? "success" : "warning"}>{role.status}</Badge>
      ),
      header: "Status",
      key: "status",
    },
    {
      cell: (role) =>
        canRevoke && role.status === "active" ? (
          <Button onClick={() => onRevoke?.(role)} size="compact" variant="danger">
            Revoke
          </Button>
        ) : null,
      className: "text-right",
      header: <span className="sr-only">Actions</span>,
      key: "actions",
    },
  ];

  return (
    <DataTable
      caption="Actor role assignments"
      columns={columns}
      data={userRoles}
      emptyState={
        <EmptyState
          description="No role assignment is visible for this actor."
          title="No assignments"
        />
      }
      getRowKey={(role) => role.id}
    />
  );
}

export { UserRoleList };
export type { UserRoleListProps };
