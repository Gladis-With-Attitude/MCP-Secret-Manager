import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import type { SecretVersion } from "../types/secret-version";
import { SecretVersionMetadata } from "./secret-version-metadata";
import { VersionCompare } from "./version-compare";

type SecretVersionDetailsProps = {
  currentVersion?: SecretVersion | null;
  version: SecretVersion;
};

function SecretVersionDetails({ currentVersion, version }: SecretVersionDetailsProps) {
  return (
    <Stack>
      <SecretVersionMetadata version={version} />
      <Grid columns={2}>
        <Section title="Metadata comparison">
          {currentVersion ? (
            <VersionCompare currentVersion={currentVersion} selectedVersion={version} />
          ) : (
            <EmptyState
              description="The current version metadata could not be loaded."
              title="No comparison available"
            />
          )}
        </Section>
        <Section title="Value access">
          <EmptyState
            description="Version values are never displayed in metadata views. Authorized value access belongs to explicit reveal workflows."
            title="Metadata only"
          />
        </Section>
      </Grid>
    </Stack>
  );
}

export { SecretVersionDetails };
export type { SecretVersionDetailsProps };
