import type { ReactNode } from "react";

import { Button } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";

import type { Vault } from "../types/vault";
import { VaultGrid } from "./vault-grid";
import { VaultTable } from "./vault-table";

type VaultListProps = {
  canCreate?: boolean;
  isFiltered?: boolean;
  isLoading?: boolean;
  onArchive: (vault: Vault) => void;
  onCreateAction?: ReactNode;
  onResetFilters?: () => void;
  vaults: Vault[];
};

function VaultList({
  canCreate = true,
  isFiltered = false,
  isLoading = false,
  onArchive,
  onCreateAction,
  onResetFilters,
  vaults,
}: VaultListProps) {
  if (!isLoading && vaults.length === 0) {
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
            ? "No vault matches the current search or filters."
            : canCreate
              ? "A vault is the first security boundary for organizing projects and secrets."
              : "No vault is currently accessible. Contact an administrator if this looks unexpected."
        }
        title={isFiltered ? "No matching vaults" : "No vaults available"}
      />
    );
  }

  return (
    <Stack>
      <div className="hidden lg:block">
        <VaultTable isLoading={isLoading} onArchive={onArchive} vaults={vaults} />
      </div>
      <div className="lg:hidden">
        <VaultGrid vaults={vaults} />
      </div>
    </Stack>
  );
}

export { VaultList };
export type { VaultListProps };
