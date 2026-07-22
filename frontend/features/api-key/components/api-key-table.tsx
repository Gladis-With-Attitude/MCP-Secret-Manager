import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/feedback/empty-state";

import type { ApiKey } from "../types/api-key";
import { ApiKeyBadge } from "./api-key-badge";
import { ApiKeyExpiration } from "./api-key-expiration";
import { ApiKeyLastUsed } from "./api-key-last-used";

type ApiKeyTableProps = {
  apiKeys: ApiKey[];
  canCreate?: boolean;
  canRevoke?: boolean;
  isFiltered?: boolean;
  isLoading?: boolean;
  onCreateAction?: React.ReactNode;
  onResetFilters?: () => void;
  onRevoke?: (apiKey: ApiKey) => void;
};

function ApiKeyTable({
  apiKeys,
  canCreate = false,
  canRevoke = false,
  isFiltered = false,
  isLoading = false,
  onCreateAction,
  onResetFilters,
  onRevoke,
}: ApiKeyTableProps) {
  const columns: DataTableColumn<ApiKey>[] = [
    {
      cell: (apiKey) => (
        <div>
          <p className="font-medium">{apiKey.name}</p>
          <p className="text-xs text-muted-foreground">
            Prefix {apiKey.keyPrefix ?? "unavailable"}
          </p>
        </div>
      ),
      header: "Name",
      key: "name",
    },
    {
      cell: (apiKey) => <ApiKeyBadge status={apiKey.status} />,
      header: "Status",
      key: "status",
    },
    {
      cell: (apiKey) => apiKey.ownerName ?? apiKey.ownerId ?? "Unavailable",
      header: "Owner",
      key: "owner",
    },
    {
      cell: (apiKey) => <ApiKeyExpiration expiresAt={apiKey.expiresAt} />,
      header: "Expiration",
      key: "expiresAt",
    },
    {
      cell: (apiKey) => <ApiKeyLastUsed lastUsedAt={apiKey.lastUsedAt} />,
      header: "Last used",
      key: "lastUsed",
    },
    {
      cell: (apiKey) => (
        <div className="flex justify-end gap-2">
          <Button asChild size="compact" variant="outline">
            <Link href={`/api-keys/${apiKey.id}`}>View</Link>
          </Button>
          {canRevoke && apiKey.status !== "revoked" ? (
            <Button onClick={() => onRevoke?.(apiKey)} size="compact" variant="danger">
              Revoke
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
      caption="API keys"
      columns={columns}
      data={apiKeys}
      emptyState={
        <EmptyState
          action={
            isFiltered ? (
              <Button onClick={onResetFilters} variant="outline">
                Reset filters
              </Button>
            ) : canCreate ? (
              onCreateAction
            ) : undefined
          }
          description={
            isFiltered
              ? "No API key matches the selected filters."
              : "Create API keys for agents, services and external integrations."
          }
          title={isFiltered ? "No matching API keys" : "No API keys"}
        />
      }
      getRowKey={(apiKey) => apiKey.id}
      isLoading={isLoading}
    />
  );
}

export { ApiKeyTable };
export type { ApiKeyTableProps };
