import { Button } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { Badge } from "@/components/display/badge";
import { EmptyState } from "@/components/feedback/empty-state";

import type { ActiveSession } from "../types/profile";

type SessionListProps = {
  canRevoke?: boolean;
  onRevoke?: (session: ActiveSession) => void;
  sessions: ActiveSession[];
};

function SessionList({ canRevoke = false, onRevoke, sessions }: SessionListProps) {
  const columns: DataTableColumn<ActiveSession>[] = [
    {
      cell: (session) => (
        <div>
          <div className="font-medium text-foreground">{session.device ?? "Unknown device"}</div>
          <div className="text-sm text-muted-foreground">
            {session.userAgent ?? "User agent unavailable"}
          </div>
        </div>
      ),
      header: "Session",
      key: "session",
    },
    {
      cell: (session) => session.ipAddress ?? "Hidden",
      header: "IP",
      key: "ip",
    },
    {
      cell: (session) => session.lastSeenAt ?? "Not available",
      header: "Last seen",
      key: "lastSeen",
    },
    {
      cell: (session) => (session.current ? <Badge variant="success">Current</Badge> : null),
      header: "Status",
      key: "status",
    },
    {
      cell: (session) =>
        canRevoke && !session.current ? (
          <Button onClick={() => onRevoke?.(session)} size="compact" variant="danger">
            Revoke
          </Button>
        ) : null,
      className: "text-right",
      header: <span className="sr-only">Actions</span>,
      key: "actions",
    },
  ];

  return (
    <DataTable
      caption="Active sessions"
      columns={columns}
      data={sessions}
      emptyState={
        <EmptyState
          description="No active session metadata is available from the backend."
          title="No sessions"
        />
      }
      getRowKey={(session) => session.id}
    />
  );
}

export { SessionList };
export type { SessionListProps };
