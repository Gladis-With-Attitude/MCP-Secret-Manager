import { AuditDetailPage } from "@/features/audit";

type AuditEventRoutePageProps = {
  params: Promise<{
    eventId: string;
  }>;
};

export default async function AuditEventRoutePage({ params }: AuditEventRoutePageProps) {
  const { eventId } = await params;

  return <AuditDetailPage eventId={eventId} />;
}
