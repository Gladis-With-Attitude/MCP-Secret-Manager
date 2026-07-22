import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Text } from "@/components/typography/text";

import { canUseSecretAction } from "../mappers/secret-mappers";
import type { Secret } from "../types/secret";
import { SecretStatusBadge } from "./secret-status-badge";
import { SecretTypeBadge } from "./secret-type-badge";

type SecretCardProps = {
  secret: Secret;
  vaultId: string;
};

function SecretCard({ secret, vaultId }: SecretCardProps) {
  return (
    <Card className="grid gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold text-foreground">{secret.name}</h3>
          <Text tone="muted">{secret.description ?? "No description"}</Text>
        </div>
        <div className="flex shrink-0 flex-wrap justify-end gap-2">
          <SecretTypeBadge type={secret.type} />
          <SecretStatusBadge status={secret.status} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 text-sm text-muted-foreground">
        <span>Project: {secret.projectName ?? secret.projectId}</span>
        <span>Version: {secret.currentVersion ?? "Unavailable"}</span>
      </div>
      <div className="flex flex-wrap justify-end gap-2">
        <Button asChild size="compact" variant="outline">
          <Link href={`/vaults/${vaultId}/projects/${secret.projectId}/secrets/${secret.id}`}>
            Open
          </Link>
        </Button>
        {canUseSecretAction(secret.permissions, "update") ? (
          <Button asChild size="compact" variant="ghost">
            <Link
              href={`/vaults/${vaultId}/projects/${secret.projectId}/secrets/${secret.id}/edit`}
            >
              Edit
            </Link>
          </Button>
        ) : null}
      </div>
    </Card>
  );
}

export { SecretCard };
export type { SecretCardProps };
