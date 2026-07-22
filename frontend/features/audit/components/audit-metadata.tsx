import { Card } from "@/components/display/card";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { AuditMetadata as AuditMetadataType } from "../types/audit";

type AuditMetadataProps = {
  metadata: AuditMetadataType;
};

function AuditMetadata({ metadata }: AuditMetadataProps) {
  const entries = Object.entries(metadata);

  if (!entries.length) {
    return (
      <EmptyState
        description="No additional safe metadata was returned for this audit event."
        title="No metadata"
      />
    );
  }

  return (
    <Card>
      <Stack gap="sm">
        {entries.map(([key, value]) => (
          <div className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:items-center" key={key}>
            <Text tone="muted" size="sm">
              {key}
            </Text>
            <Text className="break-words" size="sm">
              {value === null ? "null" : String(value)}
            </Text>
          </div>
        ))}
      </Stack>
    </Card>
  );
}

export { AuditMetadata };
export type { AuditMetadataProps };
