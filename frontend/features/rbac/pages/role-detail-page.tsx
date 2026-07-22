"use client";

import { useState } from "react";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button, buttonVariants } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Stack } from "@/components/layout/stack";
import { cn } from "@/lib/utils";

import { AssignRoleDialog } from "../components/assign-role-dialog";
import { RoleDetails } from "../components/role-details";
import { canUseRbacAction } from "../mappers/rbac-mappers";
import { useAssignRoleMutation, useRoleDetailQuery, useRoleListQuery } from "../queries";
import type { RoleAssignmentValues } from "../types/rbac";
import { RbacErrorView } from "./rbac-error-view";

type RoleDetailPageProps = {
  roleId: string;
};

function RoleDetailPage({ roleId }: RoleDetailPageProps) {
  const roleQuery = useRoleDetailQuery(roleId);
  const rolesQuery = useRoleListQuery();
  const assignMutation = useAssignRoleMutation();
  const [isAssignOpen, setIsAssignOpen] = useState(false);

  if (roleQuery.isLoading) {
    return <LoadingState title="Loading role" />;
  }

  if (roleQuery.isError) {
    return <RbacErrorView error={roleQuery.error} onRetry={() => void roleQuery.refetch()} />;
  }

  const role = roleQuery.data;

  if (!role) {
    return <LoadingState title="Loading role" />;
  }

  const canUpdate = canUseRbacAction(role.uiPermissions, "update") && role.kind !== "system";
  const canAssign = canUseRbacAction(role.uiPermissions, "assign");

  function handleAssign(values: RoleAssignmentValues) {
    assignMutation.mutate(values, {
      onSuccess: () => setIsAssignOpen(false),
    });
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            <div className="flex flex-wrap gap-2">
              <Link className={cn(buttonVariants({ variant: "outline" }))} href="/rbac/roles">
                Back to roles
              </Link>
              {canAssign ? (
                <Button onClick={() => setIsAssignOpen(true)} variant="outline">
                  Assign role
                </Button>
              ) : null}
              {canUpdate ? (
                <Link className={buttonVariants()} href={`/rbac/roles/${role.id}/edit`}>
                  Edit role
                </Link>
              ) : null}
            </div>
          }
          breadcrumb={<BreadcrumbBar labels={{ [roleId]: role.name }} />}
          description={role.description ?? "Role details and backend-defined permissions."}
          title={role.name}
        />
        <RoleDetails role={role} />
      </Stack>
      <AssignRoleDialog
        error={assignMutation.error?.message}
        isOpen={isAssignOpen}
        isSubmitting={assignMutation.isPending}
        onOpenChange={setIsAssignOpen}
        onSubmit={handleAssign}
        roles={rolesQuery.data?.items ?? [role]}
      />
    </Container>
  );
}

export { RoleDetailPage };
