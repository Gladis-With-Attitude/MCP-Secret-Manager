"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { Controller, useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Switch } from "@/components/forms/switch";
import { Stack } from "@/components/layout/stack";

import type { NotificationPreferences } from "../types/settings";
import {
  notificationPreferencesSchema,
  type NotificationPreferencesSchemaValues,
} from "../validation/settings-schema";

type NotificationSettingsProps = {
  error?: string | null;
  isSubmitting?: boolean;
  notifications: NotificationPreferences;
  onSubmit: (values: NotificationPreferences) => void | Promise<void>;
  readOnly?: boolean;
};

const notificationFields: Array<{
  description: string;
  label: string;
  name: keyof NotificationPreferencesSchemaValues;
}> = [
  {
    description: "Security-sensitive account and access changes.",
    label: "Security alerts",
    name: "securityAlerts",
  },
  {
    description: "Audit-related activity when the backend exposes notifications.",
    label: "Audit alerts",
    name: "auditAlerts",
  },
  {
    description: "Receive notification messages inside the application.",
    label: "In-app notifications",
    name: "inAppEnabled",
  },
  {
    description: "Receive notification messages by email.",
    label: "Email notifications",
    name: "emailEnabled",
  },
  {
    description: "Non-sensitive release and product updates.",
    label: "Product updates",
    name: "productUpdates",
  },
];

function NotificationSettings({
  error,
  isSubmitting = false,
  notifications,
  onSubmit,
  readOnly = false,
}: NotificationSettingsProps) {
  const { control, handleSubmit } = useForm<NotificationPreferencesSchemaValues>({
    defaultValues: notifications,
    resolver: zodResolver(
      notificationPreferencesSchema,
    ) as Resolver<NotificationPreferencesSchemaValues>,
  });
  const disabled = isSubmitting || readOnly;

  async function handleValidSubmit(values: NotificationPreferencesSchemaValues) {
    await onSubmit(values);
  }

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        {notificationFields.map((field) => (
          <FormField
            description={field.description}
            id={`notification-${field.name}`}
            key={field.name}
            label={field.label}
          >
            <Controller
              control={control}
              name={field.name}
              render={({ field: controllerField }) => (
                <Switch
                  checked={controllerField.value}
                  disabled={disabled}
                  id={`notification-${field.name}`}
                  onCheckedChange={controllerField.onChange}
                />
              )}
            />
          </FormField>
        ))}
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex justify-end">
          <Button disabled={readOnly} isLoading={isSubmitting} type="submit">
            Save notifications
          </Button>
        </div>
      </Stack>
    </form>
  );
}

export { NotificationSettings };
export type { NotificationSettingsProps };
