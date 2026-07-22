import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Text } from "@/components/typography/text";

import type { ActiveSession } from "../types/profile";

type ActiveSessionCardProps = {
  session: ActiveSession;
};

function ActiveSessionCard({ session }: ActiveSessionCardProps) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-foreground">
            {session.device ?? "Unknown device"}
          </h3>
          <Text size="sm" tone="muted">
            {session.location ?? session.ipAddress ?? "Location unavailable"}
          </Text>
          <Text size="sm" tone="muted">
            Last seen: {session.lastSeenAt ?? "Not available"}
          </Text>
        </div>
        {session.current ? <Badge variant="success">Current</Badge> : null}
      </div>
    </Card>
  );
}

export { ActiveSessionCard };
export type { ActiveSessionCardProps };
