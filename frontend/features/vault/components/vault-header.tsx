import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { PageHeader } from "@/components/layout/page-header";

import { canUseVaultAction } from "../mappers/vault-mappers";
import type { Vault } from "../types/vault";
import { VaultStatusBadge } from "./vault-status-badge";

type VaultHeaderProps = {
  description?: string;
  onArchive?: () => void;
  title: string;
  vault?: Vault;
};

function VaultHeader({ description, onArchive, title, vault }: VaultHeaderProps) {
  return (
    <PageHeader
      actions={
        vault ? (
          <>
            {canUseVaultAction(vault.permissions, "update") ? (
              <Button asChild variant="outline">
                <Link href={`/vaults/${vault.id}/edit`}>Edit</Link>
              </Button>
            ) : null}
            {onArchive &&
            canUseVaultAction(vault.permissions, "archive") &&
            vault.status !== "archived" ? (
              <Button onClick={onArchive} variant="danger">
                Archive
              </Button>
            ) : null}
          </>
        ) : undefined
      }
      badges={vault ? <VaultStatusBadge status={vault.status} /> : undefined}
      breadcrumb={<BreadcrumbBar labels={vault ? { [vault.id]: vault.name } : undefined} />}
      description={description ?? vault?.description}
      title={title}
    />
  );
}

export { VaultHeader };
export type { VaultHeaderProps };
