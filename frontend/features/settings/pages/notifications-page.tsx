"use client";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { NotificationSettings } from "../components/notification-settings";
import { canUseSettingsAction } from "../mappers/settings-mappers";
import { useSettingsQuery, useUpdateNotificationsMutation } from "../queries";
import type { NotificationPreferences } from "../types/settings";
import { SettingsErrorView } from "./settings-error-view";

function NotificationsPage() {
  const settingsQuery = useSettingsQuery();
  const updateNotificationsMutation = useUpdateNotificationsMutation();

  if (settingsQuery.isLoading) {
    return <LoadingState title="Loading notifications" />;
  }

  if (settingsQuery.isError) {
    return (
      <SettingsErrorView error={settingsQuery.error} onRetry={() => void settingsQuery.refetch()} />
    );
  }

  const settings = settingsQuery.data;

  if (!settings) {
    return <LoadingState title="Loading notifications" />;
  }

  const canUpdate = canUseSettingsAction(settings.permissions, "updateNotifications");

  function handleSubmit(values: NotificationPreferences) {
    updateNotificationsMutation.mutate(values);
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Configure notification categories. Messages must never contain secrets."
          title="Notifications"
        />
        <Section>
          <NotificationSettings
            error={updateNotificationsMutation.error?.message}
            isSubmitting={updateNotificationsMutation.isPending}
            notifications={settings.notifications}
            onSubmit={handleSubmit}
            readOnly={!canUpdate}
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { NotificationsPage };
