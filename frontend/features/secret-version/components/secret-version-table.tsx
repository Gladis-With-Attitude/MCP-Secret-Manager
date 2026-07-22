import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/feedback/empty-state";

import type { SecretVersion } from "../types/secret-version";
import { CurrentVersionIndicator } from "./current-version-indicator";
import { VersionBadge } from "./version-badge";

type SecretVersionTableProps = {
  basePath: string;
  canRestore?: boolean;
  isFiltered?: boolean;
  isLoading?: boolean;
  onCreateAction?: React.ReactNode;
  onResetFilters?: () => void;
  onRestore?: (version: SecretVersion) => void;
  versions: SecretVersion[];
};

function SecretVersionTable({
  basePath,
  canRestore = false,
  isFiltered = false,
  isLoading = false,
  onCreateAction,
  onResetFilters,
  onRestore,
  versions,
}: SecretVersionTableProps) {
  const columns: DataTableColumn<SecretVersion>[] = [
    {
      cell: (version) => (
        <CurrentVersionIndicator isCurrent={version.isCurrent} version={version.version} />
      ),
      header: "Version",
      key: "version",
    },
    {
      cell: (version) => <VersionBadge status={version.status} />,
      header: "Status",
      key: "status",
    },
    {
      cell: (version) => version.createdAt ?? "Unavailable",
      header: "Created",
      key: "createdAt",
    },
    {
      cell: (version) => version.createdBy ?? "Unavailable",
      header: "Actor",
      key: "createdBy",
    },
    {
      cell: (version) => (
        <div className="flex justify-end gap-2">
          <Button asChild size="compact" variant="outline">
            <Link href={`${basePath}/${version.id}`}>View</Link>
          </Button>
          {canRestore && !version.isCurrent ? (
            <Button onClick={() => onRestore?.(version)} size="compact" variant="secondary">
              Restore
            </Button>
          ) : null}
        </div>
      ),
      className: "text-right",
      header: <span className="sr-only">Actions</span>,
      key: "actions",
    },
  ];

  return (
    <DataTable
      caption="Secret versions"
      columns={columns}
      data={versions}
      emptyState={
        <EmptyState
          action={
            isFiltered ? (
              <Button onClick={onResetFilters} variant="outline">
                Reset filters
              </Button>
            ) : (
              onCreateAction
            )
          }
          description={
            isFiltered
              ? "No version matches the selected filters."
              : "This secret has no version metadata available. A secret cannot provide a value until a version exists."
          }
          title={isFiltered ? "No matching versions" : "No versions"}
        />
      }
      getRowKey={(version) => version.id}
      isLoading={isLoading}
    />
  );
}

export { SecretVersionTable };
export type { SecretVersionTableProps };
