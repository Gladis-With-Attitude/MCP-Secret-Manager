"use client";

import { useRouter } from "next/navigation";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { RoleForm } from "../components/role-form";
import { useCreateRoleMutation, usePermissionListQuery } from "../queries";
import type { RoleFormValues } from "../types/rbac";
import { RbacErrorView } from "./rbac-error-view";

function RoleCreatePage() {
  const router = useRouter();
  const permissionsQuery = usePermissionListQuery();
  const createRoleMutation = useCreateRoleMutation();

  if (permissionsQuery.isLoading) {
    return <LoadingState title="Loading permissions" />;
  }

  if (permissionsQuery.isError) {
    return (
      <RbacErrorView
        error={permissionsQuery.error}
        onRetry={() => void permissionsQuery.refetch()}
      />
    );
  }

  function handleSubmit(values: RoleFormValues) {
    createRoleMutation.mutate(values, {
      onSuccess: (role) => router.push(`/rbac/roles/${role.id}`),
    });
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Create a role from backend-defined permissions."
          title="Create role"
        />
        <Section>
          <RoleForm
            error={createRoleMutation.error?.message}
            isSubmitting={createRoleMutation.isPending}
            onCancel={() => router.push("/rbac/roles")}
            onSubmit={handleSubmit}
            permissions={permissionsQuery.data ?? []}
            submitLabel="Create role"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { RoleCreatePage };
