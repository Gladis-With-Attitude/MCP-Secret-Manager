import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Grid } from "@/components/layout/grid";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { UserProfile } from "../types/profile";

type ProfileCardProps = {
  profile: UserProfile;
};

function ProfileCard({ profile }: ProfileCardProps) {
  return (
    <Card>
      <Stack gap="md">
        <div className="flex items-start gap-4">
          <div className="flex size-14 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-lg font-semibold text-foreground">
            {profile.name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold text-foreground">{profile.name}</h2>
            <Text size="sm" tone="muted">
              {profile.email ?? profile.id}
            </Text>
            <div className="mt-2 flex flex-wrap gap-2">
              <Badge variant="neutral">{profile.accountType}</Badge>
              {profile.primaryRole ? <Badge variant="info">{profile.primaryRole}</Badge> : null}
            </div>
          </div>
        </div>
        <Grid columns={3}>
          <div>
            <Text size="sm" tone="muted">
              Organization
            </Text>
            <p className="text-sm text-foreground">{profile.organization ?? "Not available"}</p>
          </div>
          <div>
            <Text size="sm" tone="muted">
              Last login
            </Text>
            <p className="text-sm text-foreground">{profile.lastLoginAt ?? "Not available"}</p>
          </div>
          <div>
            <Text size="sm" tone="muted">
              Created
            </Text>
            <p className="text-sm text-foreground">{profile.createdAt ?? "Not available"}</p>
          </div>
        </Grid>
      </Stack>
    </Card>
  );
}

export { ProfileCard };
export type { ProfileCardProps };
