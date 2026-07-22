"use client";

import { useState } from "react";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Pagination } from "@/components/navigation/pagination";
import { useProjectDetailQuery } from "@/features/project";
import { useVaultDetailQuery } from "@/features/vault";

import { DeleteSecretDialog } from "../components/delete-secret-dialog";
import { SecretFilters } from "../components/secret-filters";
import { SecretList } from "../components/secret-list";
import { useSecretFilters } from "../hooks/use-secret-filters";
import { canUseSecretAction } from "../mappers/secret-mappers";
import { useArchiveSecretMutation, useSecretListQuery } from "../queries";
import type { Secret } from "../types/secret";
import { SecretErrorView } from "./secret-error-view";

type SecretListPageProps = {
  projectId: string;
  vaultId: string;
};

function SecretListPage({ projectId, vaultId }: SecretListPageProps) {
  const {
    filters,
    page,
    resetFilters,
    search,
    setPage,
    setSearch,
    setStatus,
    setType,
    status,
    type,
  } = useSecretFilters();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretsQuery = useSecretListQuery(projectId, filters);
  const archiveMutation = useArchiveSecretMutation();
  const [selectedSecret, setSelectedSecret] = useState<Secret | null>(null);

  if (vaultQuery.isLoading || projectQuery.isLoading || secretsQuery.isLoading) {
    return <LoadingState title="Loading secrets" />;
  }

  if (vaultQuery.isError) {
    return <SecretErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  if (projectQuery.isError) {
    return (
      <SecretErrorView error={projectQuery.error} onRetry={() => void projectQuery.refetch()} />
    );
  }

  if (secretsQuery.isError) {
    return (
      <SecretErrorView error={secretsQuery.error} onRetry={() => void secretsQuery.refetch()} />
    );
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const secretList = secretsQuery.data;
  const vaultName = vault?.name ?? "Vault";
  const projectName = project?.name ?? "Project";
  const canCreate = canUseSecretAction(secretList?.permissions ?? {}, "create");
  const isFiltered = Boolean(search || status !== "all" || type !== "all");
  const pagination = secretList?.pagination;
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
                <Link href={`/vaults/${vaultId}/projects/${projectId}/secrets/new`}>
                  Create secret
                </Link>
              </Button>
            ) : undefined
          }
          breadcrumb={<BreadcrumbBar labels={{ [projectId]: projectName, [vaultId]: vaultName }} />}
          description={`Consult and search secret metadata inside ${projectName}. Values are never shown in the list.`}
          title="Secrets"
        />
        <Section>
          <SecretFilters
            onReset={resetFilters}
            onSearchChange={setSearch}
            onStatusChange={setStatus}
            onTypeChange={setType}
            search={search}
            status={status}
            type={type}
          />
        </Section>
        <Section>
          <SecretList
            canCreate={canCreate}
            isFiltered={isFiltered}
            onArchive={setSelectedSecret}
            onCreateAction={
              <Button asChild>
                <Link href={`/vaults/${vaultId}/projects/${projectId}/secrets/new`}>
                  Create first secret
                </Link>
              </Button>
            }
            onResetFilters={resetFilters}
            secrets={secretList?.items ?? []}
            vaultId={vaultId}
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
      {selectedSecret ? (
        <DeleteSecretDialog
          isOpen={Boolean(selectedSecret)}
          isSubmitting={archiveMutation.isPending}
          onConfirm={() => {
            archiveMutation.mutate(selectedSecret.id, {
              onSuccess: () => setSelectedSecret(null),
            });
          }}
          onOpenChange={(open) => {
            if (!open) {
              setSelectedSecret(null);
            }
          }}
          secret={selectedSecret}
        />
      ) : null}
    </Container>
  );
}

export { SecretListPage };
