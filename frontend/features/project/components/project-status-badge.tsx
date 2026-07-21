import { Badge } from "@/components/display/badge";

import type { ProjectStatus } from "../types/project";

type ProjectStatusBadgeProps = {
  status: ProjectStatus;
};

const statusLabel = {
  active: "Active",
  archived: "Archived",
} satisfies Record<ProjectStatus, string>;

function ProjectStatusBadge({ status }: ProjectStatusBadgeProps) {
  return (
    <Badge variant={status === "archived" ? "warning" : "success"}>{statusLabel[status]}</Badge>
  );
}

export { ProjectStatusBadge };
export type { ProjectStatusBadgeProps };
