"use client";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";

import { SettingsForm } from "../components/settings-form";
import { canUseSettingsAction } from "../mappers/settings-mappers";
import { useSettingsQuery, useUpdatePreferencesMutation } from "../queries";
import type { UserPreferences } from "../types/settings";
import { SettingsErrorView } from "./settings-error-view";

function PreferencesPage() {
  const settingsQuery = useSettingsQuery();
  const updatePreferencesMutation = useUpdatePreferencesMutation();

  if (settingsQuery.isLoading) {
    return <LoadingState title="Loading preferences" />;
  }

  if (settingsQuery.isError) {
    return (
      <SettingsErrorView error={settingsQuery.error} onRetry={() => void settingsQuery.refetch()} />
    );
  }

  const settings = settingsQuery.data;

  if (!settings) {
    return <LoadingState title="Loading preferences" />;
  }

  const canUpdate = canUseSettingsAction(settings.permissions, "updatePreferences");

  function handleSubmit(values: UserPreferences) {
    updatePreferencesMutation.mutate(values);
  }

  return (
    <Container size="lg">
      <Stack gap="lg">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Configure personal display preferences. Internationalization is prepared through language selection."
          title="Preferences"
        />
        <Section>
          <SettingsForm
            error={updatePreferencesMutation.error?.message}
            isSubmitting={updatePreferencesMutation.isPending}
            onSubmit={handleSubmit}
            preferences={settings.preferences}
            readOnly={!canUpdate}
          />
        </Section>
      </Stack>
    </Container>
  );
}

export { PreferencesPage };
