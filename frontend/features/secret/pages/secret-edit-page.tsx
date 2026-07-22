"use client";

import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { useProjectDetailQuery } from "@/features/project";
import { useVaultDetailQuery } from "@/features/vault";
import { isApiError } from "@/lib/api";

import { SecretForm } from "../components/secret-form";
import { SecretHeader } from "../components/secret-header";
import { useSecretDetailQuery, useUpdateSecretMutation } from "../queries";
import type { SecretFormValues } from "../types/secret";
import { SecretErrorView } from "./secret-error-view";

type SecretEditPageProps = {
  projectId: string;
  secretId: string;
  vaultId: string;
};

function SecretEditPage({ projectId, secretId, vaultId }: SecretEditPageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const secretQuery = useSecretDetailQuery(secretId);
  const updateMutation = useUpdateSecretMutation(secretId);
  const error = updateMutation.error
    ? isApiError(updateMutation.error)
      ? updateMutation.error.userMessage
      : "Unable to update secret."
    : null;

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

  const handleSubmit = async (values: SecretFormValues) => {
    await updateMutation.mutateAsync(values);
    router.push(`/vaults/${vaultId}/projects/${projectId}/secrets/${secret.id}`);
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <SecretHeader
          description="Update non-sensitive secret metadata. Secret values are not edited here."
          projectId={projectId}
          projectName={project?.name ?? secret.projectName}
          secret={secret}
          title="Edit Secret"
          vaultId={vaultId}
          vaultName={vault?.name ?? secret.vaultName}
        />
        <Section>
          <SecretForm
            error={error}
            isSubmitting={updateMutation.isPending}
            onCancel={() =>
              router.push(`/vaults/${vaultId}/projects/${projectId}/secrets/${secret.id}`)
            }
            onSubmit={handleSubmit}
            projectName={project?.name ?? secret.projectName}
            secret={secret}
            submitLabel="Save changes"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { SecretEditPage };
