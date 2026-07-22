import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { PageHeader } from "@/components/layout/page-header";

import { canUseSecretAction } from "../mappers/secret-mappers";
import type { Secret } from "../types/secret";
import { SecretStatusBadge } from "./secret-status-badge";
import { SecretTypeBadge } from "./secret-type-badge";

type SecretHeaderProps = {
  description?: string;
  onArchive?: () => void;
  projectId: string;
  projectName?: string | null;
  secret?: Secret;
  title: string;
  vaultId: string;
  vaultName?: string | null;
};

function SecretHeader({
  description,
  onArchive,
  projectId,
  projectName,
  secret,
  title,
  vaultId,
  vaultName,
}: SecretHeaderProps) {
  const labels = {
    [projectId]: projectName ?? "Project",
    [vaultId]: vaultName ?? "Vault",
    ...(secret ? { [secret.id]: secret.name } : {}),
  };

  return (
    <PageHeader
      actions={
        secret ? (
          <>
            <Button asChild variant="outline">
              <Link href={`/vaults/${vaultId}/projects/${projectId}/secrets`}>Back to secrets</Link>
            </Button>
            {canUseSecretAction(secret.permissions, "update") ? (
              <Button asChild variant="outline">
                <Link href={`/vaults/${vaultId}/projects/${projectId}/secrets/${secret.id}/edit`}>
                  Edit
                </Link>
              </Button>
            ) : null}
            {onArchive &&
            canUseSecretAction(secret.permissions, "archive") &&
            secret.status !== "archived" ? (
              <Button onClick={onArchive} variant="danger">
                Archive
              </Button>
            ) : null}
          </>
        ) : undefined
      }
      badges={
        secret ? (
          <>
            <SecretTypeBadge type={secret.type} />
            <SecretStatusBadge status={secret.status} />
          </>
        ) : undefined
      }
      breadcrumb={<BreadcrumbBar labels={labels} />}
      description={description ?? secret?.description}
      title={title}
    />
  );
}

export { SecretHeader };
export type { SecretHeaderProps };
