import type { ReactNode } from "react";

import { Button } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";

import type { Secret } from "../types/secret";
import { SecretGrid } from "./secret-grid";
import { SecretTable } from "./secret-table";

type SecretListProps = {
  canCreate?: boolean;
  isFiltered?: boolean;
  isLoading?: boolean;
  onArchive: (secret: Secret) => void;
  onCreateAction?: ReactNode;
  onResetFilters?: () => void;
  secrets: Secret[];
  vaultId: string;
};

function SecretList({
  canCreate = true,
  isFiltered = false,
  isLoading = false,
  onArchive,
  onCreateAction,
  onResetFilters,
  secrets,
  vaultId,
}: SecretListProps) {
  if (!isLoading && secrets.length === 0) {
    return (
      <EmptyState
        action={
          isFiltered && onResetFilters ? (
            <Button onClick={onResetFilters} variant="outline">
              Reset filters
            </Button>
          ) : canCreate ? (
            onCreateAction
          ) : undefined
        }
        description={
          isFiltered
            ? "No secret metadata matches the current search or filters."
            : canCreate
              ? "A secret stores a sensitive value as versioned backend-managed data. Values are masked by default."
              : "No secret metadata is currently accessible in this project."
        }
        title={isFiltered ? "No matching secrets" : "No secrets available"}
      />
    );
  }

  return (
    <Stack>
      <div className="hidden lg:block">
        <SecretTable
          isLoading={isLoading}
          onArchive={onArchive}
          secrets={secrets}
          vaultId={vaultId}
        />
      </div>
      <div className="lg:hidden">
        <SecretGrid secrets={secrets} vaultId={vaultId} />
      </div>
    </Stack>
  );
}

export { SecretList };
export type { SecretListProps };
