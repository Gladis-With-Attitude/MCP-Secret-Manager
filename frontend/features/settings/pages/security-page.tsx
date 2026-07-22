"use client";

import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { buttonVariants } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { EmptyState } from "@/components/feedback/empty-state";
import { Container } from "@/components/layout/container";
import { Grid } from "@/components/layout/grid";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { cn } from "@/lib/utils";

function SecurityPage() {
  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Account security is managed from the profile security section and validated by the backend."
          title="Security"
        />
        <Section>
          <Grid columns={2}>
            <Card>
              <Stack gap="sm">
                <h2 className="text-base font-semibold text-foreground">Password and sessions</h2>
                <p className="text-sm text-muted-foreground">
                  Change password and revoke active sessions from your profile.
                </p>
                <Link
                  className={cn(buttonVariants({ variant: "outline" }), "w-fit")}
                  href="/profile"
                >
                  Open profile
                </Link>
              </Stack>
            </Card>
            <Card>
              <EmptyState
                description="MFA, Passkeys, WebAuthn and recovery-key flows will be enabled only when backend support is available."
                title="Strong authentication"
              />
            </Card>
          </Grid>
        </Section>
      </Stack>
    </Container>
  );
}

export { SecurityPage };
