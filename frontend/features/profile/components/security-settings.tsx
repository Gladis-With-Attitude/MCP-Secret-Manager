"use client";

import { useState } from "react";

import { Button } from "@/components/buttons/button";
import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Grid } from "@/components/layout/grid";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";

import type { AccountSecurity, ChangePasswordValues } from "../types/profile";
import { ChangePasswordDialog } from "./change-password-dialog";

type SecuritySettingsProps = {
  canChangePassword?: boolean;
  changePasswordError?: string | null;
  isChangingPassword?: boolean;
  onChangePassword: (values: ChangePasswordValues) => void | Promise<void>;
  security: AccountSecurity;
};

function SecurityCapabilityCard({
  enabled,
  label,
  placeholder,
}: {
  enabled: boolean;
  label: string;
  placeholder?: string;
}) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-foreground">{label}</h3>
          <Text size="sm" tone="muted">
            {placeholder ?? "Managed by backend security policy."}
          </Text>
        </div>
        <Badge variant={enabled ? "success" : "neutral"}>
          {enabled ? "Enabled" : "Not enabled"}
        </Badge>
      </div>
    </Card>
  );
}

function SecuritySettings({
  canChangePassword = false,
  changePasswordError,
  isChangingPassword = false,
  onChangePassword,
  security,
}: SecuritySettingsProps) {
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);

  return (
    <Stack>
      <Grid columns={2}>
        <SecurityCapabilityCard enabled={security.mfaEnabled} label="MFA" />
        <SecurityCapabilityCard enabled={security.passkeysEnabled} label="Passkeys" />
        <SecurityCapabilityCard enabled={security.webAuthnEnabled} label="WebAuthn" />
        <SecurityCapabilityCard
          enabled={security.recoveryKeysAvailable}
          label="Recovery keys"
          placeholder="Shown only if the backend exposes recovery-key management."
        />
      </Grid>
      {security.passwordChangeAvailable && canChangePassword ? (
        <div className="flex justify-end">
          <Button onClick={() => setIsPasswordOpen(true)} variant="outline">
            Change password
          </Button>
        </div>
      ) : null}
      <ChangePasswordDialog
        error={changePasswordError}
        isOpen={isPasswordOpen}
        isSubmitting={isChangingPassword}
        onOpenChange={setIsPasswordOpen}
        onSubmit={async (values) => {
          await onChangePassword(values);
          setIsPasswordOpen(false);
        }}
      />
    </Stack>
  );
}

export { SecuritySettings };
export type { SecuritySettingsProps };
