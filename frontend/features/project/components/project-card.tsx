import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Text } from "@/components/typography/text";

import { canUseProjectAction } from "../mappers/project-mappers";
import type { Project } from "../types/project";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectCardProps = {
  project: Project;
};

function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Card className="grid gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold text-foreground">{project.name}</h3>
          <Text tone="muted">
            Vault: {project.vaultName ?? project.vaultId}
            {project.description ? ` - ${project.description}` : ""}
          </Text>
        </div>
        <ProjectStatusBadge status={project.status} />
      </div>
      <div className="grid grid-cols-2 gap-3 text-sm text-muted-foreground">
        <span>Secrets: {project.secretCount ?? "Unavailable"}</span>
        <span>Versions: {project.versionCount ?? "Unavailable"}</span>
      </div>
      <div className="flex flex-wrap justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${project.vaultId}/projects/${project.id}`}>Open</Link>
        </Button>
        {canUseProjectAction(project.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link href={`/vaults/${project.vaultId}/projects/${project.id}/edit`}>Edit</Link>
          </Button>
        ) : null}
      </div>
    </Card>
  );
}

export { ProjectCard };
export type { ProjectCardProps };
