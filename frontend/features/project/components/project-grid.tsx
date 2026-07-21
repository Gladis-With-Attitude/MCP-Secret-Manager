import { Grid } from "@/components/layout/grid";

import type { Project } from "../types/project";
import { ProjectCard } from "./project-card";

type ProjectGridProps = {
  projects: Project[];
};

function ProjectGrid({ projects }: ProjectGridProps) {
  return (
    <Grid columns={3}>
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </Grid>
  );
}

export { ProjectGrid };
export type { ProjectGridProps };
