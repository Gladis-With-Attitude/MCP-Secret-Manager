"use client";

import { useState } from "react";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Stack } from "@/components/layout/stack";
import { useVaultDetailQuery } from "@/features/vault";

import { DeleteProjectDialog } from "../components/delete-project-dialog";
import { ProjectDetails } from "../components/project-details";
import { ProjectHeader } from "../components/project-header";
import { useArchiveProjectMutation, useProjectDetailQuery } from "../queries";
import { ProjectErrorView } from "./project-error-view";

type ProjectDetailsPageProps = {
  projectId: string;
  vaultId: string;
};

function ProjectDetailsPage({ projectId, vaultId }: ProjectDetailsPageProps) {
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectQuery = useProjectDetailQuery(projectId);
  const archiveMutation = useArchiveProjectMutation();
  const [isArchiveOpen, setIsArchiveOpen] = useState(false);

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

  return (
    <Container size="xl">
      <Stack gap="lg">
        <ProjectHeader
          onArchive={() => setIsArchiveOpen(true)}
          project={project}
          title={project.name}
          vaultId={vaultId}
          vaultName={vault?.name ?? project.vaultName}
        />
        <ProjectDetails project={project} />
      </Stack>
      <DeleteProjectDialog
        isOpen={isArchiveOpen}
        isSubmitting={archiveMutation.isPending}
        onConfirm={() => {
          archiveMutation.mutate(project.id, {
            onSuccess: () => setIsArchiveOpen(false),
          });
        }}
        onOpenChange={setIsArchiveOpen}
        project={project}
      />
    </Container>
  );
}

export { ProjectDetailsPage };
