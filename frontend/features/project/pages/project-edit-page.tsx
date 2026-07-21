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
import { useProjectDetailQuery, useUpdateProjectMutation } from "../queries";
import type { ProjectFormValues } from "../types/project";
import { ProjectErrorView } from "./project-error-view";

type ProjectEditPageProps = {
  projectId: string;
  vaultId: string;
};

function ProjectEditPage({ projectId, vaultId }: ProjectEditPageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const updateMutation = useUpdateProjectMutation(projectId);
  const error = updateMutation.error
    ? isApiError(updateMutation.error)
      ? updateMutation.error.userMessage
      : "Unable to update project."
    : null;

  if (vaultQuery.isLoading || projectQuery.isLoading) {
    return <LoadingState title="Loading project" />;
  }

  if (vaultQuery.isError) {
    return <ProjectErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  if (projectQuery.isError) {
    return (
      <ProjectErrorView error={projectQuery.error} onRetry={() => void projectQuery.refetch()} />
    );
  }

  const vault = vaultQuery.data;
  const project = projectQuery.data;

  if (!project) {
    return <LoadingState title="Loading project" />;
  }

  const handleSubmit = async (values: ProjectFormValues) => {
    updateMutation.mutate(values, {
      onSuccess: () => router.push(`/vaults/${vaultId}/projects/${project.id}`),
    });
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <ProjectHeader
          description="Update non-sensitive project metadata."
          project={project}
          title="Edit Project"
          vaultId={vaultId}
          vaultName={vault?.name ?? project.vaultName}
        />
        <Section>
          <ProjectForm
            error={error}
            isSubmitting={updateMutation.isPending}
            onCancel={() => router.push(`/vaults/${vaultId}/projects/${project.id}`)}
            onSubmit={handleSubmit}
            project={project}
            submitLabel="Save changes"
            vaultName={vault?.name ?? project.vaultName}
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { ProjectEditPage };
