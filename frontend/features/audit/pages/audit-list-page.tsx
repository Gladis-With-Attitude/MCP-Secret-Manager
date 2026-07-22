"use client";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { AuditFilters } from "../components/audit-filters";
import { AuditPagination } from "../components/audit-pagination";
import { AuditTable } from "../components/audit-table";
import { AuditTimeline } from "../components/audit-timeline";
import { useAuditFilters } from "../hooks/use-audit-filters";
import { useAuditListQuery } from "../queries";
import { AuditErrorView } from "./audit-error-view";

function AuditListPage() {
  const { applyFilters, filters, formValues, resetFilters, setOffset } = useAuditFilters();
  const auditQuery = useAuditListQuery(filters);

  if (auditQuery.isLoading) {
    return <LoadingState title="Loading audit logs" />;
  }

  if (auditQuery.isError) {
    return <AuditErrorView error={auditQuery.error} onRetry={() => void auditQuery.refetch()} />;
  }

  const auditList = auditQuery.data;
  const isFiltered = Boolean(
    filters.action ||
    filters.actorId ||
    filters.endDate ||
    filters.query ||
    filters.resourceId ||
    filters.resourceType ||
    (filters.result && filters.result !== "all") ||
    filters.startDate,
  );

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Consult backend-generated audit events. The frontend never creates, modifies or deletes audit records."
          title="Audit Logs"
        />
        <Section title="Filters">
          <AuditFilters
            defaultValues={formValues}
            filters={filters}
            onApply={applyFilters}
            onReset={resetFilters}
          />
        </Section>
        <Section>
          <div className="hidden md:block">
            <AuditTable
              events={auditList?.events ?? []}
              isFiltered={isFiltered}
              onResetFilters={resetFilters}
            />
          </div>
          <div className="md:hidden">
            <AuditTimeline events={auditList?.events ?? []} />
          </div>
          {auditList ? (
            <AuditPagination
              hasNextPage={auditList.pagination.hasNextPage}
              hasPreviousPage={auditList.pagination.hasPreviousPage}
              limit={auditList.pagination.limit}
              offset={auditList.pagination.offset}
              onOffsetChange={setOffset}
            />
          ) : null}
        </Section>
      </Stack>
    </Container>
  );
}

export { AuditListPage };
