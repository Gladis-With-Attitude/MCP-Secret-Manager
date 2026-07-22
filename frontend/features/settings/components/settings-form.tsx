"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Select } from "@/components/forms/select";
import { Stack } from "@/components/layout/stack";

import type {
  DateTimeFormat,
  DisplayDensity,
  ThemePreference,
  UserPreferences,
} from "../types/settings";
import { preferencesSchema, type PreferencesSchemaValues } from "../validation/settings-schema";
import { LanguageSelector } from "./language-selector";
import { ThemeSelector } from "./theme-selector";
import { TimezoneSelector } from "./timezone-selector";

type SettingsFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onSubmit: (values: UserPreferences) => void | Promise<void>;
  preferences: UserPreferences;
  readOnly?: boolean;
};

const dateTimeFormatOptions = [
  { label: "Absolute", value: "absolute" },
  { label: "Relative", value: "relative" },
  { label: "Short", value: "short" },
];

const densityOptions = [
  { label: "Comfortable", value: "comfortable" },
  { label: "Compact", value: "compact" },
];

function SettingsForm({
  error,
  isSubmitting = false,
  onSubmit,
  preferences,
  readOnly = false,
}: SettingsFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    setValue,
    watch,
  } = useForm<PreferencesSchemaValues>({
    defaultValues: preferences,
    resolver: zodResolver(preferencesSchema) as Resolver<PreferencesSchemaValues>,
  });
  const values = watch();
  const disabled = isSubmitting || readOnly;

  async function handleValidSubmit(nextValues: PreferencesSchemaValues) {
    await onSubmit(nextValues);
  }

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        <FormField error={errors.theme?.message} id="settings-theme" label="Theme" required>
          <ThemeSelector
            disabled={disabled}
            onChange={(value) => setValue("theme", value, { shouldDirty: true })}
            value={values.theme as ThemePreference}
          />
        </FormField>
        <FormField
          error={errors.language?.message}
          id="settings-language"
          label="Language"
          required
        >
          <LanguageSelector
            disabled={disabled}
            onChange={(value) => setValue("language", value, { shouldDirty: true })}
            value={values.language}
          />
        </FormField>
        <FormField
          error={errors.timezone?.message}
          id="settings-timezone"
          label="Timezone"
          required
        >
          <TimezoneSelector
            disabled={disabled}
            onChange={(value) => setValue("timezone", value, { shouldDirty: true })}
            value={values.timezone}
          />
        </FormField>
        <FormField
          error={errors.dateTimeFormat?.message}
          id="settings-date-time-format"
          label="Date and time"
          required
        >
          <Select
            disabled={disabled}
            id="settings-date-time-format"
            onValueChange={(value) =>
              setValue("dateTimeFormat", value as DateTimeFormat, { shouldDirty: true })
            }
            options={dateTimeFormatOptions}
            value={values.dateTimeFormat}
          />
        </FormField>
        <FormField
          error={errors.displayDensity?.message}
          id="settings-display-density"
          label="Display density"
          required
        >
          <Select
            disabled={disabled}
            id="settings-display-density"
            onValueChange={(value) =>
              setValue("displayDensity", value as DisplayDensity, { shouldDirty: true })
            }
            options={densityOptions}
            value={values.displayDensity}
          />
        </FormField>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex justify-end">
          <Button disabled={readOnly} isLoading={isSubmitting} type="submit">
            Save preferences
          </Button>
        </div>
      </Stack>
    </form>
  );
}

export { SettingsForm };
export type { SettingsFormProps };
