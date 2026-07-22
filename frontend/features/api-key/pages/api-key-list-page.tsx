"use client";

import { useState } from "react";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Pagination } from "@/components/navigation/pagination";

import { ApiKeyFilters } from "../components/api-key-filters";
import { ApiKeyList } from "../components/api-key-list";
import { RevokeApiKeyDialog } from "../components/revoke-api-key-dialog";
import { useApiKeyFilters } from "../hooks/use-api-key-filters";
import { canUseApiKeyAction } from "../mappers/api-key-mappers";
import { useApiKeyListQuery, useRevokeApiKeyMutation } from "../queries";
import type { ApiKey } from "../types/api-key";
import { ApiKeyErrorView } from "./api-key-error-view";

function ApiKeyListPage() {
  const { filters, page, resetFilters, search, setPage, setSearch, setStatus, status } =
    useApiKeyFilters();
  const apiKeysQuery = useApiKeyListQuery(filters);
  const revokeMutation = useRevokeApiKeyMutation();
  const [selectedApiKey, setSelectedApiKey] = useState<ApiKey | null>(null);

  if (apiKeysQuery.isLoading) {
    return <LoadingState title="Loading API keys" />;
  }

  if (apiKeysQuery.isError) {
    return (
      <ApiKeyErrorView error={apiKeysQuery.error} onRetry={() => void apiKeysQuery.refetch()} />
    );
  }

  const apiKeyList = apiKeysQuery.data;
  const canCreate = canUseApiKeyAction(apiKeyList?.permissions ?? {}, "create");
  const canRevoke = canUseApiKeyAction(apiKeyList?.permissions ?? {}, "revoke");
  const isFiltered = Boolean(search || status !== "all");
  const pagination = apiKeyList?.pagination;
  const currentPage = pagination?.page ?? page;
  const hasPagination =
    Boolean(pagination?.hasNextPage || pagination?.hasPreviousPage) ||
    Boolean(pagination?.total && pagination?.pageSize && pagination.total > pagination.pageSize);

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            canCreate ? (
              <Button asChild>
                <Link href="/api-keys/new">Create API key</Link>
              </Button>
            ) : undefined
          }
          breadcrumb={<BreadcrumbBar />}
          description="Manage API keys used by agents, services and external integrations. Full key values are never shown after creation."
          title="API Keys"
        />
        <Section>
          <ApiKeyFilters
            onReset={resetFilters}
            onSearchChange={setSearch}
            onStatusChange={setStatus}
            search={search}
            status={status}
          />
        </Section>
        <Section>
          <ApiKeyList
            apiKeys={apiKeyList?.items ?? []}
            canCreate={canCreate}
            canRevoke={canRevoke}
            isFiltered={isFiltered}
            onCreateAction={
              <Button asChild>
                <Link href="/api-keys/new">Create first API key</Link>
              </Button>
            }
            onResetFilters={resetFilters}
            onRevoke={setSelectedApiKey}
          />
          {hasPagination ? (
            <Pagination
              className="mt-6"
              isNextDisabled={!pagination?.hasNextPage}
              isPreviousDisabled={!pagination?.hasPreviousPage}
              onNext={() => setPage(currentPage + 1)}
              onPrevious={() => setPage(Math.max(1, currentPage - 1))}
              pageLabel={
                pagination?.total
                  ? `Page ${currentPage} of ${Math.max(1, Math.ceil(pagination.total / (pagination.pageSize ?? 20)))}`
                  : `Page ${currentPage}`
              }
            />
          ) : null}
        </Section>
      </Stack>
      <RevokeApiKeyDialog
        apiKey={selectedApiKey}
        isOpen={Boolean(selectedApiKey)}
        isSubmitting={revokeMutation.isPending}
        onConfirm={() => {
          if (!selectedApiKey) {
            return;
          }

          revokeMutation.mutate(selectedApiKey.id, {
            onSuccess: () => setSelectedApiKey(null),
          });
        }}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedApiKey(null);
          }
        }}
      />
    </Container>
  );
}

export { ApiKeyListPage };
