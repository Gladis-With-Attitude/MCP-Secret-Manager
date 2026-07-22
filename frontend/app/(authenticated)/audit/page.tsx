import { Suspense } from "react";

import { LoadingState } from "@/components/feedback/loading-state";
import { AuditListPage } from "@/features/audit";

export default function AuditPage() {
  return (
    <Suspense fallback={<LoadingState title="Loading audit logs" />}>
      <AuditListPage />
    </Suspense>
  );
}
