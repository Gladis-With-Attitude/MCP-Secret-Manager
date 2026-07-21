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
import { useVaultDetailQuery } from "@/features/vault";

import { DeleteProjectDialog } from "../components/delete-project-dialog";
import { ProjectFilters } from "../components/project-filters";
import { ProjectList } from "../components/project-list";
import { useProjectFilters } from "../hooks/use-project-filters";
import { canUseProjectAction } from "../mappers/project-mappers";
import { useArchiveProjectMutation, useProjectListQuery } from "../queries";
import type { Project } from "../types/project";
import { ProjectErrorView } from "./project-error-view";

type ProjectListPageProps = {
  vaultId: string;
};

function ProjectListPage({ vaultId }: ProjectListPageProps) {
  const { filters, page, resetFilters, search, setPage, setSearch, setStatus, status } =
    useProjectFilters();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const projectsQuery = useProjectListQuery(vaultId, filters);
  const archiveMutation = useArchiveProjectMutation();
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  if (vaultQuery.isLoading || projectsQuery.isLoading) {
    return <LoadingState title="Loading projects" />;
  }

  if (vaultQuery.isError) {
    return <ProjectErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  if (projectsQuery.isError) {
    return (
      <ProjectErrorView error={projectsQuery.error} onRetry={() => void projectsQuery.refetch()} />
    );
  }

  const vault = vaultQuery.data;
  const projectList = projectsQuery.data;
  const vaultName = vault?.name ?? "Vault";
  const canCreate = canUseProjectAction(projectList?.permissions ?? {}, "create");
  const isFiltered = Boolean(search || status !== "all");
  const pagination = projectList?.pagination;
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
                <Link href={`/vaults/${vaultId}/projects/new`}>Create project</Link>
              </Button>
            ) : undefined
          }
          breadcrumb={<BreadcrumbBar labels={{ [vaultId]: vaultName }} />}
          description={`Consult, search and administer projects inside ${vaultName}.`}
          title="Projects"
        />
        <Section>
          <ProjectFilters
            onReset={resetFilters}
            onSearchChange={setSearch}
            onStatusChange={setStatus}
            search={search}
            status={status}
          />
        </Section>
        <Section>
          <ProjectList
            canCreate={canCreate}
            isFiltered={isFiltered}
            onArchive={setSelectedProject}
            onCreateAction={
              <Button asChild>
                <Link href={`/vaults/${vaultId}/projects/new`}>Create first project</Link>
              </Button>
            }
            onResetFilters={resetFilters}
            projects={projectList?.items ?? []}
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
      {selectedProject ? (
        <DeleteProjectDialog
          isOpen={Boolean(selectedProject)}
          isSubmitting={archiveMutation.isPending}
          onConfirm={() => {
            archiveMutation.mutate(selectedProject.id, {
              onSuccess: () => setSelectedProject(null),
            });
          }}
          onOpenChange={(open) => {
            if (!open) {
              setSelectedProject(null);
            }
          }}
          project={selectedProject}
        />
      ) : null}
    </Container>
  );
}

export { ProjectListPage };
