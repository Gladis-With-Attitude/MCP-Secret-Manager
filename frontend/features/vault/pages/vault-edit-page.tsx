"use client";

import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { isApiError } from "@/lib/api";

import { VaultForm } from "../components/vault-form";
import { VaultHeader } from "../components/vault-header";
import { useUpdateVaultMutation, useVaultDetailQuery } from "../queries";
import type { VaultFormValues } from "../types/vault";
import { VaultErrorView } from "./vault-error-view";

type VaultEditPageProps = {
  vaultId: string;
};

function VaultEditPage({ vaultId }: VaultEditPageProps) {
  const router = useRouter();
  const vaultQuery = useVaultDetailQuery(vaultId);
  const updateMutation = useUpdateVaultMutation(vaultId);
  const error = updateMutation.error
    ? isApiError(updateMutation.error)
      ? updateMutation.error.userMessage
      : "Unable to update vault."
    : null;

  if (vaultQuery.isLoading) {
    return <LoadingState title="Loading vault" />;
  }

  if (vaultQuery.isError) {
    return <VaultErrorView error={vaultQuery.error} onRetry={() => void vaultQuery.refetch()} />;
  }

  const vault = vaultQuery.data;

  if (!vault) {
    return <LoadingState title="Loading vault" />;
  }

  const handleSubmit = async (values: VaultFormValues) => {
    updateMutation.mutate(values, {
      onSuccess: () => router.push(`/vaults/${vault.id}`),
    });
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <VaultHeader
          description="Update non-sensitive vault metadata."
          title="Edit Vault"
          vault={vault}
        />
        <Section>
          <VaultForm
            error={error}
            isSubmitting={updateMutation.isPending}
            onCancel={() => router.push(`/vaults/${vault.id}`)}
            onSubmit={handleSubmit}
            submitLabel="Save changes"
            vault={vault}
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { VaultEditPage };
