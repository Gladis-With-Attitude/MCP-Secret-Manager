import Link from "next/link";

import { buttonVariants } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { AuditEvent } from "../types/audit";
import { AuditEventBadge } from "./audit-event-badge";

type AuditTimelineProps = {
  events: AuditEvent[];
};

function AuditTimeline({ events }: AuditTimelineProps) {
  if (!events.length) {
    return (
      <EmptyState
        description="Audit events will appear here after backend activity is recorded."
        title="No audit timeline"
      />
    );
  }

  return (
    <ol aria-label="Audit timeline" className="grid gap-3">
      {events.map((event) => (
        <li key={event.id}>
          <Card>
            <Stack gap="xs">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <Text className="font-medium">{event.action}</Text>
                <AuditEventBadge result={event.result} />
              </div>
              <Text tone="muted" size="sm">
                {event.timestamp} · {event.actorId ?? "Anonymous"} · {event.resourceType}
              </Text>
              <Link
                className={buttonVariants({ size: "compact", variant: "outline" })}
                href={`/audit/${event.id}`}
              >
                View event
              </Link>
            </Stack>
          </Card>
        </li>
      ))}
    </ol>
  );
}

export { AuditTimeline };
export type { AuditTimelineProps };
