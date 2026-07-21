"use client";

import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { useVaultDetailQuery } from "@/features/vault";
import { isApiError } from "@/lib/api";

import { ProjectForm } from "../components/project-form";
import { ProjectHeader } from "../components/project-header";
import { useCreateProjectMutation } from "../queries";
import type { ProjectFormValues } from "../types/project";
import { ProjectErrorView } from "./project-error-view";

type ProjectCreatePageProps = {
  vaultId: string;
};

function ProjectCreatePage({ vaultId }: ProjectCreatePageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const createMutation = useCreateProjectMutation(vaultId);
  const error = createMutation.error
    ? isApiError(createMutation.error)
      ? createMutation.error.userMessage
      : "Unable to create project."
    : null;

  if (vaultQuery.isLoading) {
    return <LoadingState title="Loading vault" />;
  }

  if (vaultQuery.isError) {
    return <ProjectErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  const vault = vaultQuery.data;
  const vaultName = vault?.name ?? "Vault";

  const handleSubmit = async (values: ProjectFormValues) => {
    createMutation.mutate(values, {
      onSuccess: (project) => router.push(`/vaults/${vaultId}/projects/${project.id}`),
    });
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <ProjectHeader
          description="Create a new project inside this vault."
          title="Create Project"
          vaultId={vaultId}
          vaultName={vaultName}
        />
        <Section>
          <ProjectForm
            error={error}
            isSubmitting={createMutation.isPending}
            onSubmit={handleSubmit}
            submitLabel="Create project"
            vaultName={vaultName}
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { ProjectCreatePage };
