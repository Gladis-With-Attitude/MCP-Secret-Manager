import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import type { SecretVersion } from "../types/secret-version";
import { SecretVersionCard } from "./secret-version-card";
import { SecretVersionTable } from "./secret-version-table";
import { SecretVersionTimeline } from "./secret-version-timeline";

type VersionHistoryProps = {
  basePath: string;
  canRestore?: boolean;
  isFiltered?: boolean;
  onCreateAction?: React.ReactNode;
  onResetFilters?: () => void;
  onRestore?: (version: SecretVersion) => void;
  versions: SecretVersion[];
};

function VersionHistory({
  basePath,
  canRestore = false,
  isFiltered = false,
  onCreateAction,
  onResetFilters,
  onRestore,
  versions,
}: VersionHistoryProps) {
  return (
    <Stack>
      <div className="hidden md:block">
        <SecretVersionTable
          basePath={basePath}
          canRestore={canRestore}
          isFiltered={isFiltered}
          onCreateAction={onCreateAction}
          onResetFilters={onResetFilters}
          onRestore={onRestore}
          versions={versions}
        />
      </div>
      <div className="md:hidden">
        {versions.length ? (
          <Grid>
            {versions.map((version) => (
              <SecretVersionCard
                basePath={basePath}
                canRestore={canRestore}
                key={version.id}
                onRestore={onRestore}
                version={version}
              />
            ))}
          </Grid>
        ) : (
          <SecretVersionTable
            basePath={basePath}
            isFiltered={isFiltered}
            onCreateAction={onCreateAction}
            onResetFilters={onResetFilters}
            versions={versions}
          />
        )}
      </div>
      <Section title="Timeline">
        <SecretVersionTimeline versions={versions} />
      </Section>
    </Stack>
  );
}

export { VersionHistory };
export type { VersionHistoryProps };
