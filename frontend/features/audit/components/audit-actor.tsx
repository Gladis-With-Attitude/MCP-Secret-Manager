import { Text } from "@/components/typography/text";

import type { AuditEvent } from "../types/audit";

type AuditActorProps = {
  event: AuditEvent;
};

function AuditActor({ event }: AuditActorProps) {
  return (
    <div>
      <Text className="font-medium">{event.actorId ?? "Anonymous"}</Text>
      <Text tone="muted" size="sm">
        {event.actorType}
      </Text>
    </div>
  );
}

export { AuditActor };
export type { AuditActorProps };
