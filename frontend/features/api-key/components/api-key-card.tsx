import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { ApiKey } from "../types/api-key";
import { ApiKeyBadge } from "./api-key-badge";
import { ApiKeyLastUsed } from "./api-key-last-used";

type ApiKeyCardProps = {
  apiKey: ApiKey;
  canRevoke?: boolean;
  onRevoke?: (apiKey: ApiKey) => void;
};

function ApiKeyCard({ apiKey, canRevoke = false, onRevoke }: ApiKeyCardProps) {
  return (
    <Card>
      <Stack gap="sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <Text className="font-medium">{apiKey.name}</Text>
            <Text className="text-muted-foreground" size="sm">
              Prefix {apiKey.keyPrefix ?? "unavailable"}
            </Text>
          </div>
          <ApiKeyBadge status={apiKey.status} />
        </div>
        <ApiKeyLastUsed lastUsedAt={apiKey.lastUsedAt} />
        <div className="flex flex-wrap gap-2">
          <Button asChild size="compact" variant="outline">
            <Link href={`/api-keys/${apiKey.id}`}>View metadata</Link>
          </Button>
          {canRevoke && apiKey.status !== "revoked" ? (
            <Button onClick={() => onRevoke?.(apiKey)} size="compact" variant="danger">
              Revoke
            </Button>
          ) : null}
        </div>
      </Stack>
    </Card>
  );
}

export { ApiKeyCard };
export type { ApiKeyCardProps };
