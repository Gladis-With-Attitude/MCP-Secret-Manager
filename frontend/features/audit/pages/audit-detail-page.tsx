"use client";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { buttonVariants } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Stack } from "@/components/layout/stack";

import { AuditDetails } from "../components/audit-details";
import { useAuditDetailQuery } from "../queries";
import { AuditErrorView } from "./audit-error-view";

type AuditDetailPageProps = {
  eventId: string;
};

function AuditDetailPage({ eventId }: AuditDetailPageProps) {
  const auditQuery = useAuditDetailQuery(eventId);

  if (auditQuery.isLoading) {
    return <LoadingState title="Loading audit event" />;
  }

  if (auditQuery.isError) {
    return <AuditErrorView error={auditQuery.error} onRetry={() => void auditQuery.refetch()} />;
  }

  const event = auditQuery.data;

  if (!event) {
    return <LoadingState title="Loading audit event" />;
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            <Link className={buttonVariants({ variant: "outline" })} href="/audit">
              Back to audit logs
            </Link>
          }
          breadcrumb={<BreadcrumbBar labels={{ [eventId]: event.action }} />}
          description="Inspect a backend-generated audit event. Values displayed here are safe metadata only."
          title={event.action}
        />
        <AuditDetails event={event} />
      </Stack>
    </Container>
  );
}

export { AuditDetailPage };
