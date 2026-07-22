"use client";

import { useState } from "react";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { useAuth } from "@/hooks/use-auth";

import { ProfileCard } from "../components/profile-card";
import { ProfileForm } from "../components/profile-form";
import { RevokeSessionDialog } from "../components/revoke-session-dialog";
import { SecuritySettings } from "../components/security-settings";
import { SessionList } from "../components/session-list";
import { canUseProfileAction } from "../mappers/profile-mappers";
import {
  useAccountSecurityQuery,
  useActiveSessionsQuery,
  useChangePasswordMutation,
  useCurrentProfileQuery,
  useRevokeSessionMutation,
  useUpdateProfileMutation,
} from "../queries";
import type { ActiveSession, ChangePasswordValues, ProfileFormValues } from "../types/profile";
import { ProfileErrorView } from "./profile-error-view";

function ProfilePage() {
  const { logout } = useAuth();
  const profileQuery = useCurrentProfileQuery();
  const securityQuery = useAccountSecurityQuery();
  const sessionsQuery = useActiveSessionsQuery();
  const updateProfileMutation = useUpdateProfileMutation();
  const changePasswordMutation = useChangePasswordMutation();
  const revokeSessionMutation = useRevokeSessionMutation();
  const [selectedSession, setSelectedSession] = useState<ActiveSession | null>(null);

  if (profileQuery.isLoading || securityQuery.isLoading || sessionsQuery.isLoading) {
    return <LoadingState title="Loading profile" />;
  }

  if (profileQuery.isError) {
    return (
      <ProfileErrorView error={profileQuery.error} onRetry={() => void profileQuery.refetch()} />
    );
  }

  if (securityQuery.isError) {
    return (
      <ProfileErrorView error={securityQuery.error} onRetry={() => void securityQuery.refetch()} />
    );
  }

  if (sessionsQuery.isError) {
    return (
      <ProfileErrorView error={sessionsQuery.error} onRetry={() => void sessionsQuery.refetch()} />
    );
  }

  const profile = profileQuery.data;
  const security = securityQuery.data;
  const sessions = sessionsQuery.data ?? [];

  if (!profile || !security) {
    return <LoadingState title="Loading profile" />;
  }

  const canUpdate = canUseProfileAction(profile.permissions, "update");
  const canChangePassword = canUseProfileAction(profile.permissions, "changePassword");
  const canRevokeSessions = canUseProfileAction(profile.permissions, "revokeSessions");

  function handleProfileSubmit(values: ProfileFormValues) {
    updateProfileMutation.mutate(values);
  }

  function handleChangePassword(values: ChangePasswordValues) {
    changePasswordMutation.mutate(values);
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        <PageHeader
          actions={
            <Button onClick={() => void logout()} variant="outline">
              Logout
            </Button>
          }
          breadcrumb={<BreadcrumbBar />}
          description="Manage your account metadata, preferences context and account security."
          title="Profile"
        />
        <Section>
          <ProfileCard profile={profile} />
        </Section>
        <Section
          description="Only non-sensitive profile fields are shown here."
          title="Personal information"
        >
          <ProfileForm
            error={updateProfileMutation.error?.message}
            isSubmitting={updateProfileMutation.isPending}
            onSubmit={handleProfileSubmit}
            profile={profile}
            readOnly={!canUpdate}
          />
        </Section>
        <Section
          description="Security operations remain backend-owned. Future strong-auth options are shown only as status."
          title="Security"
        >
          <SecuritySettings
            canChangePassword={canChangePassword}
            changePasswordError={changePasswordMutation.error?.message}
            isChangingPassword={changePasswordMutation.isPending}
            onChangePassword={handleChangePassword}
            security={security}
          />
        </Section>
        <Section description="Session metadata never includes tokens." title="Active sessions">
          <SessionList
            canRevoke={canRevokeSessions}
            onRevoke={setSelectedSession}
            sessions={sessions}
          />
        </Section>
      </Stack>
      <RevokeSessionDialog
        isOpen={Boolean(selectedSession)}
        isSubmitting={revokeSessionMutation.isPending}
        onConfirm={() => {
          if (!selectedSession) {
            return;
          }

          revokeSessionMutation.mutate(selectedSession.id, {
            onSuccess: () => setSelectedSession(null),
          });
        }}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedSession(null);
          }
        }}
        session={selectedSession}
      />
    </Container>
  );
}

export { ProfilePage };
