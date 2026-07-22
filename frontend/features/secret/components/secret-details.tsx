import Link from "next/link";

import { Button } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { canUseSecretAction } from "../mappers/secret-mappers";
import type { Secret, SecretValueResult } from "../types/secret";
import { SecretMetadata } from "./secret-metadata";
import { SecretValuePreview } from "./secret-value-preview";

type SecretDetailsProps = {
  onRevealValue: () => Promise<SecretValueResult>;
  secret: Secret;
  versionsHref?: string;
};

function SecretDetails({ onRevealValue, secret, versionsHref }: SecretDetailsProps) {
  return (
    <Stack>
      <SecretValuePreview
        canReveal={canUseSecretAction(secret.permissions, "readValue")}
        onReveal={onRevealValue}
      />
      <SecretMetadata secret={secret} />
      <Grid columns={3}>
        <Section title="Versions">
          <EmptyState
            action={
              versionsHref ? (
                <Button asChild variant="outline">
                  <Link href={versionsHref}>Open version history</Link>
                </Button>
              ) : undefined
            }
            description="Consult immutable metadata-only versions. Secret values are never displayed in history."
            title={
              secret.currentVersion
                ? `Current version ${secret.currentVersion}`
                : "No version metadata loaded"
            }
          />
        </Section>
        <Section title="Permissions">
          <EmptyState
            description="Permission details will be displayed when the backend exposes the authorized summary."
            title="No permission summary"
          />
        </Section>
        <Section title="Recent Activity">
          <EmptyState
            description="Audit data belongs to the Audit feature and is intentionally not implemented here."
            title="No activity loaded"
          />
        </Section>
      </Grid>
    </Stack>
  );
}

export { SecretDetails };
export type { SecretDetailsProps };
