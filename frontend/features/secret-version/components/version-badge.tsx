import { Badge } from "@/components/display/badge";

import type { SecretVersionStatus } from "../types/secret-version";

type VersionBadgeProps = {
  status: SecretVersionStatus;
};

const statusLabels: Record<SecretVersionStatus, string> = {
  active: "Active",
  current: "Current",
  deprecated: "Deprecated",
  destroyed: "Destroyed",
  revoked: "Revoked",
  unknown: "Unknown",
};

const statusVariants: Record<
  SecretVersionStatus,
  "danger" | "info" | "neutral" | "success" | "warning"
> = {
  active: "info",
  current: "success",
  deprecated: "warning",
  destroyed: "danger",
  revoked: "danger",
  unknown: "neutral",
};

function VersionBadge({ status }: VersionBadgeProps) {
  return <Badge variant={statusVariants[status]}>{statusLabels[status]}</Badge>;
}

export { statusLabels, VersionBadge };
export type { VersionBadgeProps };
