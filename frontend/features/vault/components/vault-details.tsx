import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import type { Vault } from "../types/vault";
import { VaultMetadata } from "./vault-metadata";

type VaultDetailsProps = {
  vault: Vault;
};

function VaultDetails({ vault }: VaultDetailsProps) {
  return (
    <Stack>
      <VaultMetadata vault={vault} />
      <Grid columns={3}>
        <Section title="Projects">
          <EmptyState
            action={
              <div className="flex flex-wrap justify-center gap-2">
                <Button asChild variant="outline">
                  <Link href={`/vaults/${vault.id}/projects`}>View projects</Link>
                </Button>
                <Button asChild>
                  <Link href={`/vaults/${vault.id}/projects/new`}>Create project</Link>
                </Button>
              </div>
            }
            description="Projects are managed from the Project feature while preserving this vault context."
            title={
              vault.projectCount
                ? `${vault.projectCount} projects available`
                : "No project data loaded"
            }
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

export { VaultDetails };
export type { VaultDetailsProps };
