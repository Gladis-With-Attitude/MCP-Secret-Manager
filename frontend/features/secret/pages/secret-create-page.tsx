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
import { useCreateSecretMutation } from "../queries";
import type { SecretFormValues } from "../types/secret";
import { SecretErrorView } from "./secret-error-view";

type SecretCreatePageProps = {
  projectId: string;
  vaultId: string;
};

function SecretCreatePage({ projectId, vaultId }: SecretCreatePageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const createMutation = useCreateSecretMutation(projectId);
  const error = createMutation.error
    ? isApiError(createMutation.error)
      ? createMutation.error.userMessage
      : "Unable to create secret."
    : null;

  if (vaultQuery.isLoading || projectQuery.isLoading) {
    return <LoadingState title="Loading project" />;
  }

  if (vaultQuery.isError) {
    return <SecretErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  if (projectQuery.isError) {
    return (
      <SecretErrorView error={projectQuery.error} onRetry={() => void projectQuery.refetch()} />
    );
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;
  const vaultName = vault?.name ?? "Vault";
  const projectName = project?.name ?? "Project";

  const handleSubmit = async (values: SecretFormValues) => {
    const secret = await createMutation.mutateAsync(values);
    router.push(`/vaults/${vaultId}/projects/${projectId}/secrets/${secret.id}`);
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <SecretHeader
          description="Create reusable secret metadata inside this project."
          projectId={projectId}
          projectName={projectName}
          title="Create Secret"
          vaultId={vaultId}
          vaultName={vaultName}
        />
        <Section>
          <SecretForm
            error={error}
            isSubmitting={createMutation.isPending}
            onSubmit={handleSubmit}
            projectName={projectName}
            submitLabel="Create secret"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { SecretCreatePage };
