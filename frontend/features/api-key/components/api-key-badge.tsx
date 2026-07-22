import { Badge } from "@/components/display/badge";

import type { ApiKeyStatus } from "../types/api-key";

type ApiKeyBadgeProps = {
  status: ApiKeyStatus;
};

const apiKeyStatusLabels: Record<ApiKeyStatus, string> = {
  active: "Active",
  expired: "Expired",
  revoked: "Revoked",
  unknown: "Unknown",
};

const apiKeyStatusVariants: Record<ApiKeyStatus, "danger" | "neutral" | "success" | "warning"> = {
  active: "success",
  expired: "warning",
  revoked: "danger",
  unknown: "neutral",
};

function ApiKeyBadge({ status }: ApiKeyBadgeProps) {
  return <Badge variant={apiKeyStatusVariants[status]}>{apiKeyStatusLabels[status]}</Badge>;
}

export { ApiKeyBadge, apiKeyStatusLabels };
export type { ApiKeyBadgeProps };
