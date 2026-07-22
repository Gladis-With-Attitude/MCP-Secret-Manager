"use client";

import { useState } from "react";

import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Stack } from "@/components/layout/stack";
import { useProjectDetailQuery } from "@/features/project";
import { useSecretDetailQuery } from "@/features/secret";
import { useVaultDetailQuery } from "@/features/vault";

import { RestoreVersionDialog } from "../components/restore-version-dialog";
import { SecretVersionDetails } from "../components/secret-version-details";
import { SecretVersionHeader } from "../components/secret-version-header";
import { canUseSecretVersionAction } from "../mappers/secret-version-mappers";
import {
  useCurrentSecretVersionQuery,
  useRestoreSecretVersionMutation,
  useSecretVersionDetailQuery,
} from "../queries";
import { SecretVersionErrorView } from "./secret-version-error-view";

type SecretVersionDetailPageProps = {
  projectId: string;
  secretId: string;
  vaultId: string;
  versionId: string;
};

function SecretVersionDetailPage({
  projectId,
  secretId,
  vaultId,
  versionId,
}: SecretVersionDetailPageProps) {
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretQuery = useSecretDetailQuery(secretId);
  const versionQuery = useSecretVersionDetailQuery(secretId, versionId);
  const currentVersionQuery = useCurrentSecretVersionQuery(secretId);
  const restoreMutation = useRestoreSecretVersionMutation(secretId);
  const [isRestoreOpen, setIsRestoreOpen] = useState(false);

  if (
    vaultQuery.isLoading ||
    projectQuery.isLoading ||
    secretQuery.isLoading ||
    versionQuery.isLoading
  ) {
    return <LoadingState title="Loading secret version" />;
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

  if (versionQuery.isError) {
    return (
      <SecretVersionErrorView
        error={versionQuery.error}
        onRetry={() => void versionQuery.refetch()}
      />
    );
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const secret = secretQuery.data;
  const version = versionQuery.data;

  if (!version) {
    return <LoadingState title="Loading secret version" />;
  }

  const vaultName = vault?.name ?? "Vault";
  const projectName = project?.name ?? "Project";
  const secretName = secret?.name ?? "Secret";
  const labels = {
    [projectId]: projectName,
    [secretId]: secretName,
    [vaultId]: vaultName,
    [versionId]: `Version ${version.version}`,
  };
  const basePath = `/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}/versions`;
  const canRestore = canUseSecretVersionAction(version.permissions, "restore");

  return (
    <Container size="xl">
      <Stack gap="lg">
        <SecretVersionHeader
          actions={
            canRestore && !version.isCurrent ? (
              <Button onClick={() => setIsRestoreOpen(true)} variant="secondary">
                Restore version
              </Button>
            ) : undefined
          }
          description={`Review metadata for version ${version.version}. Secret values are not displayed on this page.`}
          labels={labels}
          parentHref={basePath}
          title={`Version ${version.version}`}
        />
        <SecretVersionDetails currentVersion={currentVersionQuery.data} version={version} />
      </Stack>
      <RestoreVersionDialog
        isOpen={isRestoreOpen}
        isSubmitting={restoreMutation.isPending}
        onConfirm={() => {
          restoreMutation.mutate(
            { versionId: version.id },
            {
              onSuccess: () => setIsRestoreOpen(false),
            },
          );
        }}
        onOpenChange={setIsRestoreOpen}
        version={version}
      />
    </Container>
  );
}

export { SecretVersionDetailPage };
