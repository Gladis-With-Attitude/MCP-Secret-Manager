"use client";

import { useState } from "react";

import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Pagination } from "@/components/navigation/pagination";

import { DeleteVaultDialog } from "../components/delete-vault-dialog";
import { VaultFilters } from "../components/vault-filters";
import { VaultList } from "../components/vault-list";
import { useVaultFilters } from "../hooks/use-vault-filters";
import { canUseVaultAction } from "../mappers/vault-mappers";
import { useArchiveVaultMutation, useVaultListQuery } from "../queries";
import type { Vault } from "../types/vault";
import { VaultErrorView } from "./vault-error-view";

function VaultListPage() {
  const { filters, page, resetFilters, search, setPage, setSearch, setStatus, status } =
    useVaultFilters();
  const vaultsQuery = useVaultListQuery(filters);
  const archiveMutation = useArchiveVaultMutation();
  const [selectedVault, setSelectedVault] = useState<Vault | null>(null);

  if (vaultsQuery.isLoading) {
    return <LoadingState title="Loading vaults" />;
  }

  if (vaultsQuery.isError) {
    return <VaultErrorView error={vaultsQuery.error} onRetry={() => void vaultsQuery.refetch()} />;
  }

  const vaultList = vaultsQuery.data;
  const canCreate = canUseVaultAction(vaultList?.permissions ?? {}, "create");
  const isFiltered = Boolean(search || status !== "all");
  const pagination = vaultList?.pagination;
  const currentPage = pagination?.page ?? page;
  const hasPagination =
    Boolean(pagination?.hasNextPage || pagination?.hasPreviousPage) ||
    Boolean(pagination?.total && pagination?.pageSize && pagination.total > pagination.pageSize);

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            canCreate ? (
              <Button asChild>
                <Link href="/vaults/new">Create vault</Link>
              </Button>
            ) : undefined
          }
          description="Consult, search and administer vault metadata."
          title="Vaults"
        />
        <Section>
          <VaultFilters
            onReset={resetFilters}
            onSearchChange={setSearch}
            onStatusChange={setStatus}
            search={search}
            status={status}
          />
        </Section>
        <Section>
          <VaultList
            canCreate={canCreate}
            isFiltered={isFiltered}
            onArchive={setSelectedVault}
            onCreateAction={
              <Button asChild>
                <Link href="/vaults/new">Create first vault</Link>
              </Button>
            }
            onResetFilters={resetFilters}
            vaults={vaultList?.items ?? []}
          />
          {hasPagination ? (
            <Pagination
              className="mt-6"
              isNextDisabled={!pagination?.hasNextPage}
              isPreviousDisabled={!pagination?.hasPreviousPage}
              onNext={() => setPage(currentPage + 1)}
              onPrevious={() => setPage(Math.max(1, currentPage - 1))}
              pageLabel={
                pagination?.total
                  ? `Page ${currentPage} of ${Math.max(1, Math.ceil(pagination.total / (pagination.pageSize ?? 20)))}`
                  : `Page ${currentPage}`
              }
            />
          ) : null}
        </Section>
      </Stack>
      {selectedVault ? (
        <DeleteVaultDialog
          isOpen={Boolean(selectedVault)}
          isSubmitting={archiveMutation.isPending}
          onConfirm={() => {
            archiveMutation.mutate(selectedVault.id, {
              onSuccess: () => setSelectedVault(null),
            });
          }}
          onOpenChange={(open) => {
            if (!open) {
              setSelectedVault(null);
            }
          }}
          vault={selectedVault}
        />
      ) : null}
    </Container>
  );
}

export { VaultListPage };
