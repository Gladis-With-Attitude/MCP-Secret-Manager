import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";

import { canUseVaultAction } from "../mappers/vault-mappers";
import type { Vault } from "../types/vault";
import { VaultStatusBadge } from "./vault-status-badge";

type VaultTableProps = {
  isLoading?: boolean;
  onArchive: (vault: Vault) => void;
  vaults: Vault[];
};

const columns = (onArchive: (vault: Vault) => void): DataTableColumn<Vault>[] => [
  {
    cell: (vault) => (
      <div className="min-w-0">
        <Link
          className="font-medium text-foreground underline-offset-4 hover:underline"
          href={`/vaults/${vault.id}`}
        >
          {vault.name}
        </Link>
        {vault.description ? (
          <p className="mt-1 max-w-xl truncate text-muted-foreground">{vault.description}</p>
        ) : null}
      </div>
    ),
    header: "Name",
    key: "name",
  },
  {
    cell: (vault) => <VaultStatusBadge status={vault.status} />,
    header: "Status",
    key: "status",
  },
  {
    cell: (vault) => vault.projectCount ?? "Unavailable",
    header: "Projects",
    key: "projects",
  },
  {
    cell: (vault) => vault.secretCount ?? "Unavailable",
    header: "Secrets",
    key: "secrets",
  },
  {
    cell: (vault) => (
      <div className="flex justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${vault.id}`}>Open</Link>
        </Button>
        {canUseVaultAction(vault.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link href={`/vaults/${vault.id}/edit`}>Edit</Link>
          </Button>
        ) : null}
        {canUseVaultAction(vault.permissions, "archive") && vault.status !== "archived" ? (
          <Button onClick={() => onArchive(vault)} size="compact" variant="danger">
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

function VaultTable({ isLoading = false, onArchive, vaults }: VaultTableProps) {
  return (
    <DataTable
      caption="Vaults"
      columns={columns(onArchive)}
      data={vaults}
      getRowKey={(vault) => vault.id}
      isLoading={isLoading}
    />
  );
}

export { VaultTable };
export type { VaultTableProps };
