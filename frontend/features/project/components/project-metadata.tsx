import type { ReactNode } from "react";

import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { Project } from "../types/project";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectMetadataProps = {
  project: Project;
};

function MetadataRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="grid gap-1 sm:grid-cols-3 sm:gap-4">
      <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
      <dd className="text-sm text-foreground sm:col-span-2">{value}</dd>
    </div>
  );
}

function ProjectMetadata({ project }: ProjectMetadataProps) {
  return (
    <Card>
      <Stack>
        <div>
          <h2 className="text-base font-semibold text-foreground">Metadata</h2>
          <Text tone="muted">Non-sensitive project metadata returned by the backend.</Text>
        </div>
        <Divider />
        <dl className="grid gap-4">
          <MetadataRow
            label="Identifier"
            value={<code className="break-all text-xs">{project.id}</code>}
          />
          <MetadataRow label="Vault" value={project.vaultName ?? project.vaultId} />
          <MetadataRow label="Status" value={<ProjectStatusBadge status={project.status} />} />
          <MetadataRow label="Description" value={project.description ?? "Unavailable"} />
          <MetadataRow label="Secrets" value={project.secretCount ?? "Unavailable"} />
          <MetadataRow label="Versions" value={project.versionCount ?? "Unavailable"} />
          <MetadataRow label="Created" value={project.createdAt ?? "Unavailable"} />
          <MetadataRow label="Updated" value={project.updatedAt ?? "Unavailable"} />
          <MetadataRow label="Created by" value={project.createdBy ?? "Unavailable"} />
        </dl>
      </Stack>
    </Card>
  );
}

export { ProjectMetadata };
export type { ProjectMetadataProps };
