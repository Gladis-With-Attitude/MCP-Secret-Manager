import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";

import { canUseSecretAction } from "../mappers/secret-mappers";
import type { Secret } from "../types/secret";
import { SecretStatusBadge } from "./secret-status-badge";
import { SecretTypeBadge } from "./secret-type-badge";

type SecretTableProps = {
  isLoading?: boolean;
  onArchive: (secret: Secret) => void;
  secrets: Secret[];
  vaultId: string;
};

const columns = (
  vaultId: string,
  onArchive: (secret: Secret) => void,
): DataTableColumn<Secret>[] => [
  {
    cell: (secret) => (
      <div className="min-w-0">
        <Link
          className="font-medium text-foreground underline-offset-4 hover:underline"
          href={`/vaults/${vaultId}/projects/${secret.projectId}/secrets/${secret.id}`}
        >
          {secret.name}
        </Link>
        {secret.description ? (
          <p className="mt-1 max-w-xl truncate text-muted-foreground">{secret.description}</p>
        ) : null}
      </div>
    ),
    header: "Name",
    key: "name",
  },
  {
    cell: (secret) => secret.projectName ?? secret.projectId,
    header: "Project",
    key: "project",
  },
  {
    cell: (secret) => <SecretTypeBadge type={secret.type} />,
    header: "Type",
    key: "type",
  },
  {
    cell: (secret) => <SecretStatusBadge status={secret.status} />,
    header: "Status",
    key: "status",
  },
  {
    cell: (secret) => secret.currentVersion ?? "Unavailable",
    header: "Current version",
    key: "version",
  },
  {
    cell: (secret) => secret.updatedAt ?? "Unavailable",
    header: "Updated",
    key: "updated",
  },
  {
    cell: (secret) => (
      <div className="flex justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${vaultId}/projects/${secret.projectId}/secrets/${secret.id}`}>
            Open
          </Link>
        </Button>
        {canUseSecretAction(secret.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link
              href={`/vaults/${vaultId}/projects/${secret.projectId}/secrets/${secret.id}/edit`}
            >
              Edit
            </Link>
          </Button>
        ) : null}
        {canUseSecretAction(secret.permissions, "archive") && secret.status !== "archived" ? (
          <Button onClick={() => onArchive(secret)} size="compact" variant="danger">
            Archive
          </Button>
        ) : null}
      </div>
    ),
    className: "text-right",
    header: "Actions",
    headerClassName: "text-right",
    key: "actions",
  },
];

function SecretTable({ isLoading = false, onArchive, secrets, vaultId }: SecretTableProps) {
  return (
    <DataTable
      caption="Secrets metadata"
      columns={columns(vaultId, onArchive)}
      data={secrets}
      getRowKey={(secret) => secret.id}
      isLoading={isLoading}
    />
  );
}

export { SecretTable };
export type { SecretTableProps };
