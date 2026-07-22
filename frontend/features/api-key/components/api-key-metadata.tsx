import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { ApiKey } from "../types/api-key";
import { ApiKeyBadge } from "./api-key-badge";
import { ApiKeyExpiration } from "./api-key-expiration";
import { ApiKeyLastUsed } from "./api-key-last-used";

type ApiKeyMetadataProps = {
  apiKey: ApiKey;
};

function MetadataRow({ label, value }: { label: string; value?: number | string | null }) {
  return (
    <div className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:items-center">
      <Text className="text-muted-foreground" size="sm">
        {label}
      </Text>
      <Text className="break-words" size="sm">
        {value ?? "Unavailable"}
      </Text>
    </div>
  );
}

function ApiKeyMetadata({ apiKey }: ApiKeyMetadataProps) {
  return (
    <Card>
      <Stack gap="sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Text className="font-medium">{apiKey.name}</Text>
          <ApiKeyBadge status={apiKey.status} />
        </div>
        <Divider />
        <MetadataRow label="API Key ID" value={apiKey.id} />
        <MetadataRow label="Prefix" value={apiKey.keyPrefix} />
        <MetadataRow label="Owner" value={apiKey.ownerName ?? apiKey.ownerId} />
        <MetadataRow label="Owner type" value={apiKey.ownerType} />
        <MetadataRow label="Description" value={apiKey.description} />
        <MetadataRow label="Created at" value={apiKey.createdAt} />
        <MetadataRow label="Created by" value={apiKey.createdBy} />
        <div className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:items-center">
          <Text className="text-muted-foreground" size="sm">
            Expiration
          </Text>
          <ApiKeyExpiration expiresAt={apiKey.expiresAt} />
        </div>
        <div className="grid gap-1 sm:grid-cols-[10rem_1fr] sm:items-center">
          <Text className="text-muted-foreground" size="sm">
            Last used
          </Text>
          <ApiKeyLastUsed lastUsedAt={apiKey.lastUsedAt} />
        </div>
        <MetadataRow label="Revoked at" value={apiKey.revokedAt} />
      </Stack>
    </Card>
  );
}

export { ApiKeyMetadata };
export type { ApiKeyMetadataProps };
