"use client";

import { useState } from "react";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Stack } from "@/components/layout/stack";
import { useProjectDetailQuery } from "@/features/project";
import { useVaultDetailQuery } from "@/features/vault";

import { readSecretValue } from "../api/secret-service";
import { DeleteSecretDialog } from "../components/delete-secret-dialog";
import { SecretDetails } from "../components/secret-details";
import { SecretHeader } from "../components/secret-header";
import { mapSecretValueResponseToResult } from "../mappers/secret-mappers";
import { useArchiveSecretMutation, useSecretDetailQuery } from "../queries";
import { SecretErrorView } from "./secret-error-view";

type SecretDetailsPageProps = {
  projectId: string;
  secretId: string;
  vaultId: string;
};

function SecretDetailsPage({ projectId, secretId, vaultId }: SecretDetailsPageProps) {
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretQuery = useSecretDetailQuery(secretId);
  const archiveMutation = useArchiveSecretMutation();
  const [isArchiveOpen, setIsArchiveOpen] = useState(false);

  if (vaultQuery.isLoading || projectQuery.isLoading || secretQuery.isLoading) {
    return <LoadingState title="Loading secret" />;
  }

  if (vaultQuery.isError) {
    return <SecretErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  if (projectQuery.isError) {
    return (
      <SecretErrorView error={projectQuery.error} onRetry={() => void projectQuery.refetch()} />
    );
  }

  if (secretQuery.isError) {
    return <SecretErrorView error={secretQuery.error} onRetry={() => void secretQuery.refetch()} />;
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const secret = secretQuery.data;

  if (!secret) {
    return <LoadingState title="Loading secret" />;
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <SecretHeader
          onArchive={() => setIsArchiveOpen(true)}
          projectId={projectId}
          projectName={project?.name ?? secret.projectName}
          secret={secret}
          title={secret.name}
          vaultId={vaultId}
          vaultName={vault?.name ?? secret.vaultName}
        />
        <SecretDetails
          onRevealValue={async () =>
            mapSecretValueResponseToResult(await readSecretValue(secret.id))
          }
          secret={secret}
        />
      </Stack>
      <DeleteSecretDialog
        isOpen={isArchiveOpen}
        isSubmitting={archiveMutation.isPending}
        onConfirm={() => {
          archiveMutation.mutate(secret.id, {
            onSuccess: () => setIsArchiveOpen(false),
          });
        }}
        onOpenChange={setIsArchiveOpen}
        secret={secret}
      />
    </Container>
  );
}

export { SecretDetailsPage };
