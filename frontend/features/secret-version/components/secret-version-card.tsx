import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { SecretVersion } from "../types/secret-version";
import { CurrentVersionIndicator } from "./current-version-indicator";
import { VersionBadge } from "./version-badge";

type SecretVersionCardProps = {
  basePath: string;
  canRestore?: boolean;
  onRestore?: (version: SecretVersion) => void;
  version: SecretVersion;
};

function SecretVersionCard({
  basePath,
  canRestore = false,
  onRestore,
  version,
}: SecretVersionCardProps) {
  return (
    <Card>
      <Stack gap="sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <CurrentVersionIndicator isCurrent={version.isCurrent} version={version.version} />
          <VersionBadge status={version.status} />
        </div>
        <Text className="text-muted-foreground" size="sm">
          Created {version.createdAt ?? "at an unknown date"}
        </Text>
        <div className="flex flex-wrap gap-2">
          <Button asChild size="compact" variant="outline">
            <Link href={`${basePath}/${version.id}`}>View metadata</Link>
          </Button>
          {canRestore && !version.isCurrent ? (
            <Button onClick={() => onRestore?.(version)} size="compact" variant="secondary">
              Restore
            </Button>
          ) : null}
        </div>
      </Stack>
    </Card>
  );
}

export { SecretVersionCard };
export type { SecretVersionCardProps };
