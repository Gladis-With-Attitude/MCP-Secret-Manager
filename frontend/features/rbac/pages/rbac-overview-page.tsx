"use client";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { buttonVariants } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Grid } from "@/components/layout/grid";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";
import { cn } from "@/lib/utils";

import { usePermissionListQuery, useRoleListQuery } from "../queries";
import { RbacErrorView } from "./rbac-error-view";

function RbacOverviewPage() {
  const rolesQuery = useRoleListQuery();
  const permissionsQuery = usePermissionListQuery();

  if (rolesQuery.isLoading || permissionsQuery.isLoading) {
    return <LoadingState title="Loading RBAC" />;
  }

  if (rolesQuery.isError) {
    return <RbacErrorView error={rolesQuery.error} onRetry={() => void rolesQuery.refetch()} />;
  }

  if (permissionsQuery.isError) {
    return (
      <RbacErrorView
        error={permissionsQuery.error}
        onRetry={() => void permissionsQuery.refetch()}
      />
    );
  }

  const roles = rolesQuery.data?.items ?? [];
  const permissions = permissionsQuery.data ?? [];
  const assignments = roles.reduce((count, role) => count + role.assignmentsCount, 0);

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Consult roles, permissions and assignments. The backend remains the authorization authority."
          title="RBAC"
        />
        <Section>
          <Grid columns={3}>
            <Card>
              <Text size="sm" tone="muted">
                Roles
              </Text>
              <p className="text-2xl font-semibold text-foreground">{roles.length}</p>
              <Link
                className={cn(buttonVariants({ variant: "outline" }), "mt-4 w-fit")}
                href="/rbac/roles"
              >
                Manage roles
              </Link>
            </Card>
            <Card>
              <Text size="sm" tone="muted">
                Permissions
              </Text>
              <p className="text-2xl font-semibold text-foreground">{permissions.length}</p>
            </Card>
            <Card>
              <Text size="sm" tone="muted">
                Assignments
              </Text>
              <p className="text-2xl font-semibold text-foreground">{assignments}</p>
            </Card>
          </Grid>
        </Section>
      </Stack>
    </Container>
  );
}

export { RbacOverviewPage };
