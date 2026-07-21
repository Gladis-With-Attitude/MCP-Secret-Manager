import { Grid } from "@/components/layout/grid";

import type { Vault } from "../types/vault";
import { VaultCard } from "./vault-card";

type VaultGridProps = {
  vaults: Vault[];
};

function VaultGrid({ vaults }: VaultGridProps) {
  return (
    <Grid columns={3}>
      {vaults.map((vault) => (
        <VaultCard key={vault.id} vault={vault} />
      ))}
    </Grid>
  );
}

export { VaultGrid };
export type { VaultGridProps };
