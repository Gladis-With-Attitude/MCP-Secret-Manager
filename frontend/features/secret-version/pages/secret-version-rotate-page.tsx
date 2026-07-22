"use client";

import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { useProjectDetailQuery } from "@/features/project";
import { useSecretDetailQuery } from "@/features/secret";
import { useVaultDetailQuery } from "@/features/vault";

import { SecretVersionForm } from "../components/secret-version-form";
import { SecretVersionHeader } from "../components/secret-version-header";
import { useCreateSecretVersionMutation } from "../queries";
import type { SecretVersionFormValues } from "../types/secret-version";
import { SecretVersionErrorView } from "./secret-version-error-view";

type SecretVersionRotatePageProps = {
  projectId: string;
  secretId: string;
  vaultId: string;
};

function SecretVersionRotatePage({ projectId, secretId, vaultId }: SecretVersionRotatePageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretQuery = useSecretDetailQuery(secretId);
  const createMutation = useCreateSecretVersionMutation(secretId);

  if (vaultQuery.isLoading || projectQuery.isLoading || secretQuery.isLoading) {
    return <LoadingState title="Loading rotation context" />;
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

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const secret = secretQuery.data;
  const vaultName = vault?.name ?? "Vault";
  const projectName = project?.name ?? "Project";
  const secretName = secret?.name ?? "Secret";
  const labels = {
    [projectId]: projectName,
    [secretId]: secretName,
    [vaultId]: vaultName,
  };
  const versionsPath = `/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}/versions`;

  async function handleSubmit(values: SecretVersionFormValues) {
    createMutation.mutate(values, {
      onSuccess: (version) => {
        router.push(`${versionsPath}/${version.id}`);
      },
    });
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <SecretVersionHeader
          description={`Create a new immutable version for ${secretName}. Encryption and key handling are backend-owned.`}
          labels={labels}
          parentHref={versionsPath}
          title="Rotate secret"
        />
        <Section>
          <SecretVersionForm
            error={createMutation.error instanceof Error ? createMutation.error.message : null}
            isSubmitting={createMutation.isPending}
            onCancel={() => router.push(versionsPath)}
            onSubmit={handleSubmit}
            secretName={secretName}
            submitLabel="Create version"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { SecretVersionRotatePage };
