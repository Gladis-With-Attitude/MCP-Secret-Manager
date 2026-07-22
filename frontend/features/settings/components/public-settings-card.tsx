import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Grid } from "@/components/layout/grid";
import { Text } from "@/components/typography/text";

import type { PublicSettings } from "../types/settings";

type PublicSettingsCardProps = {
  settings: PublicSettings;
};

function PublicSettingsCard({ settings }: PublicSettingsCardProps) {
  return (
    <Grid columns={3}>
      <Card>
        <Text size="sm" tone="muted">
          Instance
        </Text>
        <p className="text-sm font-medium text-foreground">
          {settings.instanceName ?? "MCP Secret Manager"}
        </p>
      </Card>
      <Card>
        <Text size="sm" tone="muted">
          Environment
        </Text>
        <p className="text-sm font-medium text-foreground">
          {settings.environment ?? "Not exposed"}
        </p>
      </Card>
      <Card>
        <Text size="sm" tone="muted">
          API status
        </Text>
        <Badge variant={settings.apiStatus === "healthy" ? "success" : "neutral"}>
          {settings.apiStatus ?? "unknown"}
        </Badge>
      </Card>
      <Card>
        <Text size="sm" tone="muted">
          Frontend version
        </Text>
        <p className="text-sm font-medium text-foreground">
          {settings.frontendVersion ?? "Not exposed"}
        </p>
      </Card>
      <Card>
        <Text size="sm" tone="muted">
          Backend version
        </Text>
        <p className="text-sm font-medium text-foreground">
          {settings.backendVersion ?? "Not exposed"}
        </p>
      </Card>
      <Card>
        <Text size="sm" tone="muted">
          Deployment
        </Text>
        <p className="text-sm font-medium text-foreground">
          {settings.deploymentMode ?? "Not exposed"}
        </p>
      </Card>
    </Grid>
  );
}

export { PublicSettingsCard };
export type { PublicSettingsCardProps };
