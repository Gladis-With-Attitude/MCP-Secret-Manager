import { Card } from "@/components/display/card";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { SecretVersion } from "../types/secret-version";
import { CurrentVersionIndicator } from "./current-version-indicator";
import { VersionBadge } from "./version-badge";

type SecretVersionTimelineProps = {
  versions: SecretVersion[];
};

function SecretVersionTimeline({ versions }: SecretVersionTimelineProps) {
  if (!versions.length) {
    return (
      <EmptyState
        description="Version history will appear here after the first secret value is created."
        title="No version history"
      />
    );
  }

  return (
    <ol aria-label="Secret version timeline" className="grid gap-3">
      {versions.map((version) => (
        <li key={version.id}>
          <Card className="relative">
            <Stack gap="xs">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <CurrentVersionIndicator isCurrent={version.isCurrent} version={version.version} />
                <VersionBadge status={version.status} />
              </div>
              <Text className="text-muted-foreground" size="sm">
                Created {version.createdAt ?? "at an unknown date"}
                {version.createdBy ? ` by ${version.createdBy}` : ""}
              </Text>
            </Stack>
          </Card>
        </li>
      ))}
    </ol>
  );
}

export { SecretVersionTimeline };
export type { SecretVersionTimelineProps };
