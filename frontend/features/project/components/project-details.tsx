import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import type { Project } from "../types/project";
import { ProjectMetadata } from "./project-metadata";

type ProjectDetailsProps = {
  project: Project;
};

function ProjectDetails({ project }: ProjectDetailsProps) {
  return (
    <Stack>
      <ProjectMetadata project={project} />
      <Grid columns={3}>
        <Section title="Secrets">
          <EmptyState
            description="Secret workflows belong to the Secret feature and are intentionally not implemented here."
            title="No secret data loaded"
          />
        </Section>
        <Section title="Permissions">
          <EmptyState
            description="Permission details will be displayed when the backend exposes the authorized summary."
            title="No permission summary"
          />
        </Section>
        <Section title="Recent Activity">
          <EmptyState
            description="Audit data belongs to the Audit feature and is intentionally not implemented here."
            title="No activity loaded"
          />
        </Section>
      </Grid>
    </Stack>
  );
}

export { ProjectDetails };
export type { ProjectDetailsProps };
