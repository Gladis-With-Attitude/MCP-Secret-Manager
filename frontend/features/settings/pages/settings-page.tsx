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
import { cn } from "@/lib/utils";

import { PublicSettingsCard } from "../components/public-settings-card";
import { useSettingsQuery } from "../queries";
import { SettingsErrorView } from "./settings-error-view";

const settingsLinks = [
  {
    description: "Theme, language, timezone and display preferences.",
    href: "/settings/preferences",
    title: "Preferences",
  },
  {
    description: "Password, sessions and future strong-auth controls.",
    href: "/settings/security",
    title: "Security",
  },
  {
    description: "Email and in-app notification preferences.",
    href: "/settings/notifications",
    title: "Notifications",
  },
];

function SettingsPage() {
  const settingsQuery = useSettingsQuery();

  if (settingsQuery.isLoading) {
    return <LoadingState title="Loading settings" />;
  }

  if (settingsQuery.isError) {
    return (
      <SettingsErrorView error={settingsQuery.error} onRetry={() => void settingsQuery.refetch()} />
    );
  }

  const settings = settingsQuery.data;

  if (!settings) {
    return <LoadingState title="Loading settings" />;
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Review safe application settings and personal configuration surfaces."
          title="Settings"
        />
        <Section description="Only non-sensitive public diagnostics are displayed." title="System">
          <PublicSettingsCard settings={settings.publicSettings} />
        </Section>
        <Section title="Settings areas">
          <Grid columns={3}>
            {settingsLinks.map((item) => (
              <Card key={item.href}>
                <Stack gap="sm">
                  <div>
                    <h2 className="text-base font-semibold text-foreground">{item.title}</h2>
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  </div>
                  <Link
                    className={cn(buttonVariants({ variant: "outline" }), "w-fit")}
                    href={item.href}
                  >
                    Open
                  </Link>
                </Stack>
              </Card>
            ))}
          </Grid>
        </Section>
      </Stack>
    </Container>
  );
}

export { SettingsPage };
