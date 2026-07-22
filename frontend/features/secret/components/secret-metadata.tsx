import type { ReactNode } from "react";

import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { Secret } from "../types/secret";
import { SecretStatusBadge } from "./secret-status-badge";
import { SecretTypeBadge } from "./secret-type-badge";

type SecretMetadataProps = {
  secret: Secret;
};

function MetadataRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="grid gap-1 sm:grid-cols-3 sm:gap-4">
      <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
      <dd className="text-sm text-foreground sm:col-span-2">{value}</dd>
    </div>
  );
}

function SecretMetadata({ secret }: SecretMetadataProps) {
  const metadataEntries = Object.entries(secret.metadata);

  return (
    <Card>
      <Stack>
        <div>
          <h2 className="text-base font-semibold text-foreground">Metadata</h2>
          <Text tone="muted">Non-sensitive secret metadata. The secret value is not included.</Text>
        </div>
        <Divider />
        <dl className="grid gap-4">
          <MetadataRow
            label="Identifier"
            value={<code className="break-all text-xs">{secret.id}</code>}
          />
          <MetadataRow label="Project" value={secret.projectName ?? secret.projectId} />
          <MetadataRow label="Vault" value={secret.vaultName ?? secret.vaultId ?? "Unavailable"} />
          <MetadataRow label="Type" value={<SecretTypeBadge type={secret.type} />} />
          <MetadataRow label="Status" value={<SecretStatusBadge status={secret.status} />} />
          <MetadataRow label="Description" value={secret.description ?? "Unavailable"} />
          <MetadataRow label="Current version" value={secret.currentVersion ?? "Unavailable"} />
          <MetadataRow label="Version count" value={secret.versionCount ?? "Unavailable"} />
          <MetadataRow label="Last version" value={secret.lastVersionAt ?? "Unavailable"} />
          <MetadataRow
            label="Tags"
            value={
              secret.tags.length > 0 ? (
                <span className="flex flex-wrap gap-2">
                  {secret.tags.map((tag) => (
                    <Badge key={tag} variant="neutral">
                      {tag}
                    </Badge>
                  ))}
                </span>
              ) : (
                "Unavailable"
              )
            }
          />
          <MetadataRow
            label="Custom metadata"
            value={
              metadataEntries.length > 0 ? (
                <span className="grid gap-1">
                  {metadataEntries.map(([key, value]) => (
                    <span key={key}>
                      <span className="text-muted-foreground">{key}: </span>
                      {String(value)}
                    </span>
                  ))}
                </span>
              ) : (
                "Unavailable"
              )
            }
          />
          <MetadataRow label="Created" value={secret.createdAt ?? "Unavailable"} />
          <MetadataRow label="Updated" value={secret.updatedAt ?? "Unavailable"} />
          <MetadataRow label="Created by" value={secret.createdBy ?? "Unavailable"} />
        </dl>
      </Stack>
    </Card>
  );
}

export { SecretMetadata };
export type { SecretMetadataProps };
