import { Badge } from "@/components/display/badge";

import type { SecretStatus } from "../types/secret";

type SecretStatusBadgeProps = {
  status: SecretStatus;
};

const statusLabel = {
  active: "Active",
  archived: "Archived",
  deleted: "Deleted",
  missing_version: "Missing version",
} satisfies Record<SecretStatus, string>;

function SecretStatusBadge({ status }: SecretStatusBadgeProps) {
  const variant =
    status === "active" ? "success" : status === "missing_version" ? "danger" : "warning";

  return <Badge variant={variant}>{statusLabel[status]}</Badge>;
}

export { SecretStatusBadge };
export type { SecretStatusBadgeProps };
