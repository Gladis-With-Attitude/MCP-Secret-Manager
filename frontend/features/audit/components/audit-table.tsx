import Link from "next/link";

import { Button, buttonVariants } from "@/components/buttons/button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/feedback/empty-state";

import type { AuditEvent } from "../types/audit";
import { AuditActor } from "./audit-actor";
import { AuditEventBadge } from "./audit-event-badge";
import { AuditResource } from "./audit-resource";

type AuditTableProps = {
  events: AuditEvent[];
  isFiltered?: boolean;
  isLoading?: boolean;
  onResetFilters?: () => void;
};

function AuditTable({
  events,
  isFiltered = false,
  isLoading = false,
  onResetFilters,
}: AuditTableProps) {
  const columns: DataTableColumn<AuditEvent>[] = [
    {
      cell: (event) => event.timestamp,
      header: "Timestamp",
      key: "timestamp",
    },
    {
      cell: (event) => <AuditActor event={event} />,
      header: "Actor",
      key: "actor",
    },
    {
      cell: (event) => event.action,
      header: "Action",
      key: "action",
    },
    {
      cell: (event) => <AuditResource event={event} />,
      header: "Resource",
      key: "resource",
    },
    {
      cell: (event) => <AuditEventBadge result={event.result} />,
      header: "Result",
      key: "result",
    },
    {
      cell: (event) => (
        <div className="flex justify-end">
          <Link
            className={buttonVariants({ size: "compact", variant: "outline" })}
            href={`/audit/${event.id}`}
          >
            View
          </Link>
        </div>
      ),
      className: "text-right",
      header: <span className="sr-only">Actions</span>,
      key: "actions",
    },
  ];

  return (
    <DataTable
      caption="Audit logs"
      columns={columns}
      data={events}
      emptyState={
        <EmptyState
          action={
            isFiltered ? (
              <Button onClick={onResetFilters} variant="outline">
                Reset filters
              </Button>
            ) : undefined
          }
          description={
            isFiltered
              ? "No audit event matches the selected filters."
              : "No audit event is available for this instance yet."
          }
          title={isFiltered ? "No matching audit logs" : "No audit logs"}
        />
      }
      getRowKey={(event) => event.id}
      isLoading={isLoading}
    />
  );
}

export { AuditTable };
export type { AuditTableProps };
