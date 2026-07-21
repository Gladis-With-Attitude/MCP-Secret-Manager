import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Text } from "@/components/typography/text";

import { canUseVaultAction } from "../mappers/vault-mappers";
import type { Vault } from "../types/vault";
import { VaultStatusBadge } from "./vault-status-badge";

type VaultCardProps = {
  vault: Vault;
};

function VaultCard({ vault }: VaultCardProps) {
  return (
    <Card className="grid gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold text-foreground">{vault.name}</h3>
          {vault.description ? <Text tone="muted">{vault.description}</Text> : null}
        </div>
        <VaultStatusBadge status={vault.status} />
      </div>
      <div className="grid grid-cols-2 gap-3 text-sm text-muted-foreground">
        <span>Projects: {vault.projectCount ?? "Unavailable"}</span>
        <span>Secrets: {vault.secretCount ?? "Unavailable"}</span>
      </div>
      <div className="flex flex-wrap justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${vault.id}`}>Open</Link>
        </Button>
        {canUseVaultAction(vault.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link href={`/vaults/${vault.id}/edit`}>Edit</Link>
          </Button>
        ) : null}
      </div>
    </Card>
  );
}

export { VaultCard };
export type { VaultCardProps };
