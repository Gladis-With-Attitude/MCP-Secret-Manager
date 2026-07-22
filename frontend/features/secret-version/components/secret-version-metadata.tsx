import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { SecretVersion } from "../types/secret-version";
import { CurrentVersionIndicator } from "./current-version-indicator";
import { VersionBadge } from "./version-badge";

type SecretVersionMetadataProps = {
  version: SecretVersion;
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

function SecretVersionMetadata({ version }: SecretVersionMetadataProps) {
  const metadataEntries = Object.entries(version.metadata);

  return (
    <Card>
      <Stack gap="sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CurrentVersionIndicator isCurrent={version.isCurrent} version={version.version} />
          <VersionBadge status={version.status} />
        </div>
        <Divider />
        <MetadataRow label="Version ID" value={version.id} />
        <MetadataRow label="Secret ID" value={version.secretId} />
        <MetadataRow label="Created at" value={version.createdAt} />
        <MetadataRow label="Created by" value={version.createdBy} />
        <MetadataRow label="Algorithm" value={version.algorithm} />
        <MetadataRow label="Crypto scheme" value={version.cryptoSchemeVersion} />
        <MetadataRow label="Key reference" value={version.keyReference} />
        <MetadataRow label="Note" value={version.note} />
        {metadataEntries.length ? (
          <>
            <Divider />
            {metadataEntries.map(([key, value]) => (
              <MetadataRow key={key} label={key} value={String(value)} />
            ))}
          </>
        ) : null}
      </Stack>
    </Card>
  );
}

export { SecretVersionMetadata };
export type { SecretVersionMetadataProps };
