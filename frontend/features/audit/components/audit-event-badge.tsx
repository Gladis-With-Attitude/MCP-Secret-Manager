import { Badge } from "@/components/display/badge";

import type { AuditResult } from "../types/audit";

type AuditEventBadgeProps = {
  result: AuditResult;
};

const auditResultLabels: Record<AuditResult, string> = {
  failure: "Failure",
  success: "Success",
  unknown: "Unknown",
};

const auditResultVariants: Record<AuditResult, "danger" | "neutral" | "success"> = {
  failure: "danger",
  success: "success",
  unknown: "neutral",
};

function AuditEventBadge({ result }: AuditEventBadgeProps) {
  return <Badge variant={auditResultVariants[result]}>{auditResultLabels[result]}</Badge>;
}

export { AuditEventBadge, auditResultLabels };
export type { AuditEventBadgeProps };
