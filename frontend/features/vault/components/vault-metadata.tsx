import type { ReactNode } from "react";

import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { Vault } from "../types/vault";
import { VaultStatusBadge } from "./vault-status-badge";

type VaultMetadataProps = {
  vault: Vault;
};

function MetadataRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="grid gap-1 sm:grid-cols-3 sm:gap-4">
      <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
      <dd className="sm:col-span-2 text-sm text-foreground">{value}</dd>
    </div>
  );
}

function VaultMetadata({ vault }: VaultMetadataProps) {
  return (
    <Card>
      <Stack>
        <div>
          <h2 className="text-base font-semibold text-foreground">Metadata</h2>
          <Text tone="muted">Non-sensitive vault metadata returned by the backend.</Text>
        </div>
        <Divider />
        <dl className="grid gap-4">
          <MetadataRow
            label="Identifier"
            value={<code className="break-all text-xs">{vault.id}</code>}
          />
          <MetadataRow label="Status" value={<VaultStatusBadge status={vault.status} />} />
          <MetadataRow label="Description" value={vault.description ?? "Unavailable"} />
          <MetadataRow label="Projects" value={vault.projectCount ?? "Unavailable"} />
          <MetadataRow label="Secrets" value={vault.secretCount ?? "Unavailable"} />
          <MetadataRow label="Created" value={vault.createdAt ?? "Unavailable"} />
          <MetadataRow label="Updated" value={vault.updatedAt ?? "Unavailable"} />
          <MetadataRow label="Created by" value={vault.createdBy ?? "Unavailable"} />
        </dl>
      </Stack>
    </Card>
  );
}

export { VaultMetadata };
export type { VaultMetadataProps };
