"use client";

import { useState } from "react";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Stack } from "@/components/layout/stack";

import { DeleteVaultDialog } from "../components/delete-vault-dialog";
import { VaultDetails } from "../components/vault-details";
import { VaultHeader } from "../components/vault-header";
import { useArchiveVaultMutation, useVaultDetailQuery } from "../queries";
import { VaultErrorView } from "./vault-error-view";

type VaultDetailsPageProps = {
  vaultId: string;
};

function VaultDetailsPage({ vaultId }: VaultDetailsPageProps) {
  const vaultQuery = useVaultDetailQuery(vaultId);
  const archiveMutation = useArchiveVaultMutation();
  const [isArchiveOpen, setIsArchiveOpen] = useState(false);

  if (vaultQuery.isLoading) {
    return <LoadingState title="Loading vault" />;
  }

  if (vaultQuery.isError) {
    return <VaultErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  const vault = vaultQuery.data;

  if (!vault) {
    return <LoadingState title="Loading vault" />;
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <VaultHeader onArchive={() => setIsArchiveOpen(true)} title={vault.name} vault={vault} />
        <VaultDetails vault={vault} />
      </Stack>
      <DeleteVaultDialog
        isOpen={isArchiveOpen}
        isSubmitting={archiveMutation.isPending}
        onConfirm={() => {
          archiveMutation.mutate(vault.id, {
            onSuccess: () => setIsArchiveOpen(false),
          });
        }}
        onOpenChange={setIsArchiveOpen}
        vault={vault}
      />
    </Container>
  );
}

export { VaultDetailsPage };
