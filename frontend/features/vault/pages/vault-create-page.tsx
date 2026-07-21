"use client";

import { useRouter } from "next/navigation";

import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { isApiError } from "@/lib/api";

import { VaultForm } from "../components/vault-form";
import { VaultHeader } from "../components/vault-header";
import { useCreateVaultMutation } from "../queries";
import type { VaultFormValues } from "../types/vault";

function VaultCreatePage() {
  const router = useRouter();
  const createMutation = useCreateVaultMutation();
  const error = createMutation.error
    ? isApiError(createMutation.error)
      ? createMutation.error.userMessage
      : "Unable to create vault."
    : null;

  const handleSubmit = async (values: VaultFormValues) => {
    createMutation.mutate(values, {
      onSuccess: (vault) => router.push(`/vaults/${vault.id}`),
    });
  };

  return (
    <Container size="lg">
      <Stack gap="lg">
        <VaultHeader description="Create a new vault security boundary." title="Create Vault" />
        <Section>
          <VaultForm
            error={error}
            isSubmitting={createMutation.isPending}
            onSubmit={handleSubmit}
            submitLabel="Create vault"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { VaultCreatePage };
