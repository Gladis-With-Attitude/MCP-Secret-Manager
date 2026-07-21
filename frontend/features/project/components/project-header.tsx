import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { PageHeader } from "@/components/layout/page-header";

import { canUseProjectAction } from "../mappers/project-mappers";
import type { Project } from "../types/project";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectHeaderProps = {
  description?: string;
  onArchive?: () => void;
  project?: Project;
  title: string;
  vaultId: string;
  vaultName?: string | null;
};

function ProjectHeader({
  description,
  onArchive,
  project,
  title,
  vaultId,
  vaultName,
}: ProjectHeaderProps) {
  const labels = {
    [vaultId]: vaultName ?? "Vault",
    ...(project ? { [project.id]: project.name } : {}),
  };

  return (
    <PageHeader
      actions={
        project ? (
          <>
            <Button asChild variant="outline">
              <Link href={`/vaults/${vaultId}/projects`}>Back to projects</Link>
            </Button>
            {canUseProjectAction(project.permissions, "update") ? (
              <Button asChild variant="outline">
                <Link href={`/vaults/${vaultId}/projects/${project.id}/edit`}>Edit</Link>
              </Button>
            ) : null}
            {onArchive &&
            canUseProjectAction(project.permissions, "archive") &&
            project.status !== "archived" ? (
              <Button onClick={onArchive} variant="danger">
                Archive
              </Button>
            ) : null}
          </>
        ) : undefined
      }
      badges={project ? <ProjectStatusBadge status={project.status} /> : undefined}
      breadcrumb={<BreadcrumbBar labels={labels} />}
      description={description ?? project?.description}
      title={title}
    />
  );
}

export { ProjectHeader };
export type { ProjectHeaderProps };
