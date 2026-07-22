"use client";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { buttonVariants } from "@/components/buttons/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Pagination } from "@/components/navigation/pagination";
import { cn } from "@/lib/utils";

import { RoleCard } from "../components/role-card";
import { RoleFilters } from "../components/role-filters";
import { RoleTable } from "../components/role-table";
import { useRbacFilters } from "../hooks/use-rbac-filters";
import { canUseRbacAction } from "../mappers/rbac-mappers";
import { useRoleListQuery } from "../queries";
import { RbacErrorView } from "./rbac-error-view";

function RoleListPage() {
  const {
    filters,
    kind,
    page,
    query,
    resetFilters,
    setKind,
    setPage,
    setQuery,
    setStatus,
    status,
  } = useRbacFilters();
  const rolesQuery = useRoleListQuery(filters);

  if (rolesQuery.isLoading) {
    return <LoadingState title="Loading roles" />;
  }

  if (rolesQuery.isError) {
    return <RbacErrorView error={rolesQuery.error} onRetry={() => void rolesQuery.refetch()} />;
  }

  const roleList = rolesQuery.data;
  const roles = roleList?.items ?? [];
  const canCreate = canUseRbacAction(roleList?.permissions ?? {}, "create");
  const isFiltered = Boolean(query || kind !== "all" || status !== "all");
  const pagination = roleList?.pagination;
  const currentPage = Math.floor((pagination?.offset ?? 0) / (pagination?.limit ?? 20)) + 1;
  const totalPages =
    pagination?.total && pagination.limit
      ? Math.max(1, Math.ceil(pagination.total / pagination.limit))
      : undefined;

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            canCreate ? (
              <Link className={buttonVariants()} href="/rbac/roles/new">
                Create role
              </Link>
            ) : undefined
          }
          breadcrumb={<BreadcrumbBar />}
          description="Consult and administer backend-defined roles."
          title="Roles"
        />
        <Section title="Filters">
          <RoleFilters
            kind={kind}
            onKindChange={setKind}
            onReset={resetFilters}
            onSearchChange={setQuery}
            onStatusChange={setStatus}
            search={query}
            status={status}
          />
        </Section>
        <Section>
          {roles.length ? (
            <>
              <div className="hidden md:block">
                <RoleTable roles={roles} />
              </div>
              <div className="grid gap-4 md:hidden">
                {roles.map((role) => (
                  <RoleCard key={role.id} role={role} />
                ))}
              </div>
            </>
          ) : (
            <EmptyState
              action={
                isFiltered ? (
                  <button
                    className={cn(buttonVariants({ variant: "outline" }))}
                    onClick={resetFilters}
                    type="button"
                  >
                    Reset filters
                  </button>
                ) : canCreate ? (
                  <Link className={buttonVariants()} href="/rbac/roles/new">
                    Create first role
                  </Link>
                ) : undefined
              }
              description={
                isFiltered
                  ? "No role matches the current filters."
                  : "No custom role is visible for the current user."
              }
              title={isFiltered ? "No matching role" : "No roles"}
            />
          )}
          {pagination?.hasNextPage || pagination?.hasPreviousPage ? (
            <Pagination
              className="mt-6"
              isNextDisabled={!pagination.hasNextPage}
              isPreviousDisabled={!pagination.hasPreviousPage}
              onNext={() => setPage(page + 1)}
              onPrevious={() => setPage(Math.max(1, page - 1))}
              pageLabel={
                totalPages ? `Page ${currentPage} of ${totalPages}` : `Page ${currentPage}`
              }
            />
          ) : null}
        </Section>
      </Stack>
    </Container>
  );
}

export { RoleListPage };
