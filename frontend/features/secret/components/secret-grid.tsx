import { Grid } from "@/components/layout/grid";

import type { Secret } from "../types/secret";
import { SecretCard } from "./secret-card";

type SecretGridProps = {
  secrets: Secret[];
  vaultId: string;
};

function SecretGrid({ secrets, vaultId }: SecretGridProps) {
  return (
    <Grid columns={3}>
      {secrets.map((secret) => (
        <SecretCard key={secret.id} secret={secret} vaultId={vaultId} />
      ))}
    </Grid>
  );
}

export { SecretGrid };
export type { SecretGridProps };
