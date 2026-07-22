import { EmptyState } from "@/components/feedback/empty-state";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import type { ApiKey } from "../types/api-key";
import { ApiKeyMetadata } from "./api-key-metadata";
import { ApiKeyPermissions } from "./api-key-permissions";

type ApiKeyDetailsProps = {
  apiKey: ApiKey;
};

function ApiKeyDetails({ apiKey }: ApiKeyDetailsProps) {
  return (
    <Stack>
      <ApiKeyMetadata apiKey={apiKey} />
      <Grid columns={2}>
        <Section title="Permissions and scopes">
          <ApiKeyPermissions
            permissions={apiKey.grantedPermissions}
            roles={apiKey.roles}
            scopes={apiKey.scopes}
          />
        </Section>
        <Section title="Value access">
          <EmptyState
            description="Existing API keys are metadata-only. The full value is only displayed once immediately after creation."
            title="Value not retrievable"
          />
        </Section>
      </Grid>
    </Stack>
  );
}

export { ApiKeyDetails };
export type { ApiKeyDetailsProps };
