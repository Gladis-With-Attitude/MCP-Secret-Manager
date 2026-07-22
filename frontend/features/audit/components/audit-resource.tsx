import { Text } from "@/components/typography/text";

import type { AuditEvent } from "../types/audit";

type AuditResourceProps = {
  event: AuditEvent;
};

function AuditResource({ event }: AuditResourceProps) {
  return (
    <div>
      <Text className="font-medium">{event.resourceType}</Text>
      <Text className="break-all" tone="muted" size="sm">
        {event.resourceId ?? "No resource id"}
      </Text>
    </div>
  );
}

export { AuditResource };
export type { AuditResourceProps };
