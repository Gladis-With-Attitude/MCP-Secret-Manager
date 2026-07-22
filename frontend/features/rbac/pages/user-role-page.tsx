"use client";

import { useState } from "react";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { AssignRoleDialog } from "../components/assign-role-dialog";
import { RemoveRoleDialog } from "../components/remove-role-dialog";
import { UserRoleList } from "../components/user-role-list";
import { canUseRbacAction } from "../mappers/rbac-mappers";
import {
  useActorRolesQuery,
  useAssignRoleMutation,
  useRevokeRoleMutation,
  useRoleListQuery,
} from "../queries";
import type { RoleAssignmentValues, UserRole } from "../types/rbac";
import { RbacErrorView } from "./rbac-error-view";

type UserRolePageProps = {
  userId: string;
};

function UserRolePage({ userId }: UserRolePageProps) {
  const actorRolesQuery = useActorRolesQuery(userId);
  const rolesQuery = useRoleListQuery();
  const assignMutation = useAssignRoleMutation();
  const revokeMutation = useRevokeRoleMutation(userId);
  const [isAssignOpen, setIsAssignOpen] = useState(false);
  const [selectedUserRole, setSelectedUserRole] = useState<UserRole | null>(null);

  if (actorRolesQuery.isLoading || rolesQuery.isLoading) {
    return <LoadingState title="Loading assignments" />;
  }

  if (actorRolesQuery.isError) {
    return (
      <RbacErrorView error={actorRolesQuery.error} onRetry={() => void actorRolesQuery.refetch()} />
    );
  }

  if (rolesQuery.isError) {
    return <RbacErrorView error={rolesQuery.error} onRetry={() => void rolesQuery.refetch()} />;
  }

  const actorRoles = actorRolesQuery.data;
  const canAssign = canUseRbacAction(actorRoles?.permissions ?? {}, "assign");
  const canRevoke = canUseRbacAction(actorRoles?.permissions ?? {}, "revoke");

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
            canAssign ? (
              <Button onClick={() => setIsAssignOpen(true)} variant="outline">
                Assign role
              </Button>
            ) : undefined
          }
          breadcrumb={<BreadcrumbBar labels={{ [userId]: userId }} />}
          description="Consult and update role assignments for this actor."
          title="Actor roles"
        />
        <Section>
          <UserRoleList
            canRevoke={canRevoke}
            onRevoke={setSelectedUserRole}
            userRoles={actorRoles?.items ?? []}
          />
        </Section>
      </Stack>
      <AssignRoleDialog
        actorId={userId}
        error={assignMutation.error?.message}
        isOpen={isAssignOpen}
        isSubmitting={assignMutation.isPending}
        onOpenChange={setIsAssignOpen}
        onSubmit={handleAssign}
        roles={rolesQuery.data?.items ?? []}
      />
      <RemoveRoleDialog
        isOpen={Boolean(selectedUserRole)}
        isSubmitting={revokeMutation.isPending}
        onConfirm={() => {
          if (!selectedUserRole) {
            return;
          }

          revokeMutation.mutate(selectedUserRole.roleId, {
            onSuccess: () => setSelectedUserRole(null),
          });
        }}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedUserRole(null);
          }
        }}
        userRole={selectedUserRole}
      />
    </Container>
  );
}

export { UserRolePage };
