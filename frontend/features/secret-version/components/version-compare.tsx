import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { SecretVersion } from "../types/secret-version";

type VersionCompareProps = {
  currentVersion: SecretVersion;
  selectedVersion: SecretVersion;
};

function CompareRow({
  current,
  label,
  selected,
}: {
  current?: string | null;
  label: string;
  selected?: string | null;
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-[9rem_1fr_1fr] sm:items-center">
      <Text className="text-muted-foreground" size="sm">
        {label}
      </Text>
      <Text size="sm">{selected ?? "Unavailable"}</Text>
      <Text size="sm">{current ?? "Unavailable"}</Text>
    </div>
  );
}

function VersionCompare({ currentVersion, selectedVersion }: VersionCompareProps) {
  return (
    <Card>
      <Stack gap="sm">
        <div className="grid gap-2 sm:grid-cols-[9rem_1fr_1fr]">
          <span />
          <Text className="font-medium" size="sm">
            Selected
          </Text>
          <Text className="font-medium" size="sm">
            Current
          </Text>
        </div>
        <Divider />
        <CompareRow
          current={`Version ${currentVersion.version}`}
          label="Version"
          selected={`Version ${selectedVersion.version}`}
        />
        <CompareRow
          current={currentVersion.status}
          label="Status"
          selected={selectedVersion.status}
        />
        <CompareRow
          current={currentVersion.createdAt}
          label="Created"
          selected={selectedVersion.createdAt}
        />
        <CompareRow
          current={currentVersion.algorithm}
          label="Algorithm"
          selected={selectedVersion.algorithm}
        />
        <CompareRow
          current={currentVersion.cryptoSchemeVersion}
          label="Crypto scheme"
          selected={selectedVersion.cryptoSchemeVersion}
        />
      </Stack>
    </Card>
  );
}

export { VersionCompare };
export type { VersionCompareProps };
