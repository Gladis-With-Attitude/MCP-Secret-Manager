import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Grid } from "@/components/layout/grid";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { Role } from "../types/rbac";
import { PermissionMatrix } from "./permission-matrix";

type RoleDetailsProps = {
  role: Role;
};

function RoleDetails({ role }: RoleDetailsProps) {
  return (
    <Stack gap="lg">
      <Section>
        <Grid columns={4}>
          <Card>
            <Text size="sm" tone="muted">
              Kind
            </Text>
            <Badge variant={role.kind === "system" ? "info" : "neutral"}>{role.kind}</Badge>
          </Card>
          <Card>
            <Text size="sm" tone="muted">
              Status
            </Text>
            <Badge variant={role.status === "active" ? "success" : "warning"}>{role.status}</Badge>
          </Card>
          <Card>
            <Text size="sm" tone="muted">
              Permissions
            </Text>
            <p className="text-2xl font-semibold text-foreground">{role.permissionsCount}</p>
          </Card>
          <Card>
            <Text size="sm" tone="muted">
              Assignments
            </Text>
            <p className="text-2xl font-semibold text-foreground">{role.assignmentsCount}</p>
          </Card>
        </Grid>
      </Section>
      <Section title="Permissions">
        <PermissionMatrix
          permissions={role.permissions}
          readOnly
          selectedPermissionIds={role.permissionIds}
        />
      </Section>
    </Stack>
  );
}

export { RoleDetails };
export type { RoleDetailsProps };
