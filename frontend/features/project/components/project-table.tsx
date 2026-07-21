import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";

import { canUseProjectAction } from "../mappers/project-mappers";
import type { Project } from "../types/project";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectTableProps = {
  isLoading?: boolean;
  onArchive: (project: Project) => void;
  projects: Project[];
};

const columns = (onArchive: (project: Project) => void): DataTableColumn<Project>[] => [
  {
    cell: (project) => (
      <div className="min-w-0">
        <Link
          className="font-medium text-foreground underline-offset-4 hover:underline"
          href={`/vaults/${project.vaultId}/projects/${project.id}`}
        >
          {project.name}
        </Link>
        {project.description ? (
          <p className="mt-1 max-w-xl truncate text-muted-foreground">{project.description}</p>
        ) : null}
      </div>
    ),
    header: "Name",
    key: "name",
  },
  {
    cell: (project) => project.vaultName ?? project.vaultId,
    header: "Vault",
    key: "vault",
  },
  {
    cell: (project) => <ProjectStatusBadge status={project.status} />,
    header: "Status",
    key: "status",
  },
  {
    cell: (project) => project.secretCount ?? "Unavailable",
    header: "Secrets",
    key: "secrets",
  },
  {
    cell: (project) => project.updatedAt ?? "Unavailable",
    header: "Updated",
    key: "updated",
  },
  {
    cell: (project) => (
      <div className="flex justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${project.vaultId}/projects/${project.id}`}>Open</Link>
        </Button>
        {canUseProjectAction(project.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link href={`/vaults/${project.vaultId}/projects/${project.id}/edit`}>Edit</Link>
          </Button>
        ) : null}
        {canUseProjectAction(project.permissions, "archive") && project.status !== "archived" ? (
          <Button onClick={() => onArchive(project)} size="compact" variant="danger">
            Archive
          </Button>
        ) : null}
      </div>
    ),
    className: "text-right",
    header: "Actions",
    headerClassName: "text-right",
    key: "actions",
  },
];

function ProjectTable({ isLoading = false, onArchive, projects }: ProjectTableProps) {
  return (
    <DataTable
      caption="Projects"
      columns={columns(onArchive)}
      data={projects}
      getRowKey={(project) => project.id}
      isLoading={isLoading}
    />
  );
}

export { ProjectTable };
export type { ProjectTableProps };
