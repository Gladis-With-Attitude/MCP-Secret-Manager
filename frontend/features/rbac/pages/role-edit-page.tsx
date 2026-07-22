"use client";

import { useRouter } from "next/navigation";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { ForbiddenState } from "@/components/feedback/forbidden-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { RoleForm } from "../components/role-form";
import { canUseRbacAction } from "../mappers/rbac-mappers";
import { usePermissionListQuery, useRoleDetailQuery, useUpdateRoleMutation } from "../queries";
import type { RoleFormValues } from "../types/rbac";
import { RbacErrorView } from "./rbac-error-view";

type RoleEditPageProps = {
  roleId: string;
};

function RoleEditPage({ roleId }: RoleEditPageProps) {
  const router = useRouter();
  const roleQuery = useRoleDetailQuery(roleId);
  const permissionsQuery = usePermissionListQuery();
  const updateRoleMutation = useUpdateRoleMutation(roleId);

  if (roleQuery.isLoading || permissionsQuery.isLoading) {
    return <LoadingState title="Loading role" />;
  }

  if (roleQuery.isError) {
    return <RbacErrorView error={roleQuery.error} onRetry={() => void roleQuery.refetch()} />;
  }

  if (permissionsQuery.isError) {
    return (
      <RbacErrorView
        error={permissionsQuery.error}
        onRetry={() => void permissionsQuery.refetch()}
      />
    );
  }

  const role = roleQuery.data;

  if (!role) {
    return <LoadingState title="Loading role" />;
  }

  if (role.kind === "system" || !canUseRbacAction(role.uiPermissions, "update")) {
    return (
      <Container size="md">
        <ForbiddenState
          description="This role cannot be modified from the current frontend context."
          title="Role is read-only"
        />
      </Container>
    );
  }

  function handleSubmit(values: RoleFormValues) {
    updateRoleMutation.mutate(values, {
      onSuccess: (updatedRole) => router.push(`/rbac/roles/${updatedRole.id}`),
    });
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar labels={{ [roleId]: role.name }} />}
          description="Update role metadata and permission selection. The backend validates every change."
          title={`Edit ${role.name}`}
        />
        <Section>
          <RoleForm
            error={updateRoleMutation.error?.message}
            isSubmitting={updateRoleMutation.isPending}
            onCancel={() => router.push(`/rbac/roles/${role.id}`)}
            onSubmit={handleSubmit}
            permissions={permissionsQuery.data ?? []}
            role={role}
            submitLabel="Save role"
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { RoleEditPage };
