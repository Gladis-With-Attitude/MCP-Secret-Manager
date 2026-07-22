"use client";

import { useState } from "react";

import { useRouter } from "next/navigation";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { ApiKeyCreatedDialog } from "../components/api-key-created-dialog";
import { ApiKeyForm } from "../components/api-key-form";
import { useCreateApiKeyMutation } from "../queries";
import type { ApiKeyCreated, ApiKeyFormValues } from "../types/api-key";

function ApiKeyCreatePage() {
  const router = useRouter();
  const createMutation = useCreateApiKeyMutation();
  const [createdApiKey, setCreatedApiKey] = useState<ApiKeyCreated | null>(null);

  function handleSubmit(values: ApiKeyFormValues) {
    createMutation.mutate(values, {
      onSuccess: (created) => {
        setCreatedApiKey(created);
      },
    });
  }

  function handleCreatedDialogClose() {
    setCreatedApiKey(null);
    router.push("/api-keys");
  }

  if (createMutation.isSuccess && createdApiKey === null) {
    return <LoadingState title="Clearing API key value" />;
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Create an API key for a technical actor. The full value is shown only once after creation."
          title="Create API key"
        />
        <Section>
          <ApiKeyForm
            error={createMutation.error instanceof Error ? createMutation.error.message : null}
            isSubmitting={createMutation.isPending}
            onCancel={() => router.push("/api-keys")}
            onSubmit={handleSubmit}
            submitLabel="Create API key"
          />
        </Section>
      </Stack>
      <ApiKeyCreatedDialog createdApiKey={createdApiKey} onClose={handleCreatedDialogClose} />
    </Container>
  );
}

export { ApiKeyCreatePage };
