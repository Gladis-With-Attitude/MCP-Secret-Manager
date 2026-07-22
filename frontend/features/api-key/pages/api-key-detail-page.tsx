"use client";

import { useState } from "react";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Stack } from "@/components/layout/stack";

import { ApiKeyDetails } from "../components/api-key-details";
import { RevokeApiKeyDialog } from "../components/revoke-api-key-dialog";
import { canUseApiKeyAction } from "../mappers/api-key-mappers";
import { useApiKeyDetailQuery, useRevokeApiKeyMutation } from "../queries";
import { ApiKeyErrorView } from "./api-key-error-view";

type ApiKeyDetailPageProps = {
  apiKeyId: string;
};

function ApiKeyDetailPage({ apiKeyId }: ApiKeyDetailPageProps) {
  const apiKeyQuery = useApiKeyDetailQuery(apiKeyId);
  const revokeMutation = useRevokeApiKeyMutation();
  const [isRevokeOpen, setIsRevokeOpen] = useState(false);

  if (apiKeyQuery.isLoading) {
    return <LoadingState title="Loading API key" />;
  }

  if (apiKeyQuery.isError) {
    return <ApiKeyErrorView error={apiKeyQuery.error} onRetry={() => void apiKeyQuery.refetch()} />;
  }

  const apiKey = apiKeyQuery.data;

  if (!apiKey) {
    return <LoadingState title="Loading API key" />;
  }

  const canRevoke = canUseApiKeyAction(apiKey.permissions, "revoke");

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            <div className="flex flex-wrap gap-2">
              <Button asChild variant="outline">
                <Link href="/api-keys">Back to API keys</Link>
              </Button>
              {canRevoke && apiKey.status !== "revoked" ? (
                <Button onClick={() => setIsRevokeOpen(true)} variant="danger">
                  Revoke API key
                </Button>
              ) : null}
            </div>
          }
          breadcrumb={<BreadcrumbBar labels={{ [apiKeyId]: apiKey.name }} />}
          description="Inspect API key metadata. The full key value cannot be retrieved after creation."
          title={apiKey.name}
        />
        <ApiKeyDetails apiKey={apiKey} />
      </Stack>
      <RevokeApiKeyDialog
        apiKey={apiKey}
        isOpen={isRevokeOpen}
        isSubmitting={revokeMutation.isPending}
        onConfirm={() => {
          revokeMutation.mutate(apiKey.id, {
            onSuccess: () => setIsRevokeOpen(false),
          });
        }}
        onOpenChange={setIsRevokeOpen}
      />
    </Container>
  );
}

export { ApiKeyDetailPage };
