"use client";

import { useState } from "react";

import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Pagination } from "@/components/navigation/pagination";
import { useProjectDetailQuery } from "@/features/project";
import { useSecretDetailQuery } from "@/features/secret";
import { useVaultDetailQuery } from "@/features/vault";

import { RestoreVersionDialog } from "../components/restore-version-dialog";
import { SecretVersionFilters } from "../components/secret-version-filters";
import { SecretVersionHeader } from "../components/secret-version-header";
import { VersionHistory } from "../components/version-history";
import { useSecretVersionFilters } from "../hooks/use-secret-version-filters";
import { canUseSecretVersionAction } from "../mappers/secret-version-mappers";
import { useRestoreSecretVersionMutation, useSecretVersionListQuery } from "../queries";
import type { SecretVersion } from "../types/secret-version";
import { SecretVersionErrorView } from "./secret-version-error-view";

type SecretVersionListPageProps = {
  projectId: string;
  secretId: string;
  vaultId: string;
};

function SecretVersionListPage({ projectId, secretId, vaultId }: SecretVersionListPageProps) {
  const { currentOnly, filters, page, resetFilters, setCurrentOnly, setPage, setStatus, status } =
    useSecretVersionFilters();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretQuery = useSecretDetailQuery(secretId);
  const versionsQuery = useSecretVersionListQuery(secretId, filters);
  const restoreMutation = useRestoreSecretVersionMutation(secretId);
  const [selectedVersion, setSelectedVersion] = useState<SecretVersion | null>(null);

  if (
    vaultQuery.isLoading ||
    projectQuery.isLoading ||
    secretQuery.isLoading ||
    versionsQuery.isLoading
  ) {
    return <LoadingState title="Loading secret versions" />;
  }

  if (vaultQuery.isError) {
    return (
      <SecretVersionErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />
    );
  }

  if (projectQuery.isError) {
    return (
      <SecretVersionErrorView
        error={projectQuery.error}
        onRetry={() => void projectQuery.refetch()}
      />
    );
  }

  if (secretQuery.isError) {
    return (
      <SecretVersionErrorView
        error={secretQuery.error}
        onRetry={() => void secretQuery.refetch()}
      />
    );
  }

  if (versionsQuery.isError) {
    return (
      <SecretVersionErrorView
        error={versionsQuery.error}
        onRetry={() => void versionsQuery.refetch()}
      />
    );
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const secret = secretQuery.data;
  const versionList = versionsQuery.data;
  const vaultName = vault?.name ?? "Vault";
  const projectName = project?.name ?? "Project";
  const secretName = secret?.name ?? "Secret";
  const labels = {
    [projectId]: projectName,
    [secretId]: secretName,
    [vaultId]: vaultName,
  };
  const basePath = `/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}/versions`;
  const canCreate = canUseSecretVersionAction(versionList?.permissions ?? {}, "create");
  const canRestore = canUseSecretVersionAction(versionList?.permissions ?? {}, "restore");
  const isFiltered = status !== "all" || currentOnly;
  const pagination = versionList?.pagination;
  const currentPage = pagination?.page ?? page;
  const hasPagination =
    Boolean(pagination?.hasNextPage || pagination?.hasPreviousPage) ||
    Boolean(pagination?.total && pagination?.pageSize && pagination.total > pagination.pageSize);

  return (
    <Container size="xl">
      <Stack gap="lg">
        <SecretVersionHeader
          actions={
            canCreate ? (
              <Button asChild>
                <Link href={`${basePath}/rotate`}>Rotate secret</Link>
              </Button>
            ) : undefined
          }
          description={`Consult immutable metadata-only versions for ${secretName}. Values are not displayed in history.`}
          labels={labels}
          parentHref={`/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}`}
          title="Secret versions"
        />
        <Section>
          <SecretVersionFilters
            currentOnly={currentOnly}
            onCurrentOnlyChange={setCurrentOnly}
            onReset={resetFilters}
            onStatusChange={setStatus}
            status={status}
          />
        </Section>
        <Section>
          <VersionHistory
            basePath={basePath}
            canRestore={canRestore}
            isFiltered={isFiltered}
            onCreateAction={
              canCreate ? (
                <Button asChild>
                  <Link href={`${basePath}/rotate`}>Create first version</Link>
                </Button>
              ) : undefined
            }
            onResetFilters={resetFilters}
            onRestore={setSelectedVersion}
            versions={versionList?.items ?? []}
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
      <RestoreVersionDialog
        isOpen={Boolean(selectedVersion)}
        isSubmitting={restoreMutation.isPending}
        onConfirm={() => {
          if (!selectedVersion) {
            return;
          }

          restoreMutation.mutate(
            { versionId: selectedVersion.id },
            {
              onSuccess: () => setSelectedVersion(null),
            },
          );
        }}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedVersion(null);
          }
        }}
        version={selectedVersion}
      />
    </Container>
  );
}

export { SecretVersionListPage };
