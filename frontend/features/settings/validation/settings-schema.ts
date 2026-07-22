import { z } from "zod";

const themePreferenceSchema = z.enum(["light", "dark", "system"]);
const languageSchema = z.enum(["en", "fr"]);
const timezoneSchema = z.string().min(1, "Timezone is required.").max(80);
const dateTimeFormatSchema = z.enum(["absolute", "relative", "short"]);
const displayDensitySchema = z.enum(["comfortable", "compact"]);

const preferencesSchema = z.object({
  dateTimeFormat: dateTimeFormatSchema,
  displayDensity: displayDensitySchema,
  language: languageSchema,
  theme: themePreferenceSchema,
  timezone: timezoneSchema,
});

const notificationPreferencesSchema = z.object({
  auditAlerts: z.boolean(),
  emailEnabled: z.boolean(),
  inAppEnabled: z.boolean(),
  productUpdates: z.boolean(),
  securityAlerts: z.boolean(),
});

type NotificationPreferencesSchemaValues = z.infer<typeof notificationPreferencesSchema>;
type PreferencesSchemaValues = z.infer<typeof preferencesSchema>;

export {
  dateTimeFormatSchema,
  displayDensitySchema,
  languageSchema,
  notificationPreferencesSchema,
  preferencesSchema,
  themePreferenceSchema,
  timezoneSchema,
};
export type { NotificationPreferencesSchemaValues, PreferencesSchemaValues };
