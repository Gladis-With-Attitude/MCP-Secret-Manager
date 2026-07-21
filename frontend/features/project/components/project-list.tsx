import type { ReactNode } from "react";

import { Button } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";

import type { Project } from "../types/project";
import { ProjectGrid } from "./project-grid";
import { ProjectTable } from "./project-table";

type ProjectListProps = {
  canCreate?: boolean;
  isFiltered?: boolean;
  isLoading?: boolean;
  onArchive: (project: Project) => void;
  onCreateAction?: ReactNode;
  onResetFilters?: () => void;
  projects: Project[];
};

function ProjectList({
  canCreate = true,
  isFiltered = false,
  isLoading = false,
  onArchive,
  onCreateAction,
  onResetFilters,
  projects,
}: ProjectListProps) {
  if (!isLoading && projects.length === 0) {
    return (
      <EmptyState
        action={
          isFiltered && onResetFilters ? (
            <Button onClick={onResetFilters} variant="outline">
              Reset filters
            </Button>
          ) : canCreate ? (
            onCreateAction
          ) : undefined
        }
        description={
          isFiltered
            ? "No project matches the current search or filters."
            : canCreate
              ? "A project organizes secrets inside a vault."
              : "No project is currently accessible in this vault."
        }
        title={isFiltered ? "No matching projects" : "No projects available"}
      />
    );
  }

  return (
    <Stack>
      <div className="hidden lg:block">
        <ProjectTable isLoading={isLoading} onArchive={onArchive} projects={projects} />
      </div>
      <div className="lg:hidden">
        <ProjectGrid projects={projects} />
      </div>
    </Stack>
  );
}

export { ProjectList };
export type { ProjectListProps };
