import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { AuditEvent } from "../types/audit";
import { AuditActor } from "./audit-actor";
import { AuditEventBadge } from "./audit-event-badge";
import { AuditMetadata } from "./audit-metadata";
import { AuditResource } from "./audit-resource";

type AuditDetailsProps = {
  event: AuditEvent;
};

function DetailRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:items-center">
      <Text tone="muted" size="sm">
        {label}
      </Text>
      <Text className="break-words" size="sm">
        {value ?? "Unavailable"}
      </Text>
    </div>
  );
}

function AuditDetails({ event }: AuditDetailsProps) {
  return (
    <Stack>
      <Card>
        <Stack gap="sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Text className="font-medium">{event.action}</Text>
            <AuditEventBadge result={event.result} />
          </div>
          <Divider />
          <DetailRow label="Event ID" value={event.id} />
          <DetailRow label="Timestamp" value={event.timestamp} />
          <DetailRow label="Request ID" value={event.requestId} />
          <DetailRow label="IP address" value={event.ipAddress} />
          <DetailRow label="User agent" value={event.userAgent} />
        </Stack>
      </Card>
      <Grid columns={2}>
        <Section title="Actor">
          <Card>
            <AuditActor event={event} />
          </Card>
        </Section>
        <Section title="Resource">
          <Card>
            <AuditResource event={event} />
          </Card>
        </Section>
      </Grid>
      <Section title="Safe metadata">
        <AuditMetadata metadata={event.metadata} />
      </Section>
    </Stack>
  );
}

export { AuditDetails };
export type { AuditDetailsProps };
