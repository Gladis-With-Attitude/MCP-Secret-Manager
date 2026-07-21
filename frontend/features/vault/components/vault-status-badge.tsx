import { Badge } from "@/components/display/badge";

import type { VaultStatus } from "../types/vault";

type VaultStatusBadgeProps = {
  status: VaultStatus;
};

function VaultStatusBadge({ status }: VaultStatusBadgeProps) {
  if (status === "locked") {
    return <Badge variant="warning">Locked</Badge>;
  }

  if (status === "archived") {
    return <Badge variant="neutral">Archived</Badge>;
  }

  return <Badge variant="success">Active</Badge>;
}

export { VaultStatusBadge };
export type { VaultStatusBadgeProps };
