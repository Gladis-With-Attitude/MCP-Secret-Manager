type ThemePreference = "dark" | "light" | "system";

type DateTimeFormat = "absolute" | "relative" | "short";

type DisplayDensity = "comfortable" | "compact";

type LanguagePreference = "en" | "fr";

type UserPreferences = {
  dateTimeFormat: DateTimeFormat;
  displayDensity: DisplayDensity;
  language: LanguagePreference;
  theme: ThemePreference;
  timezone: string;
};

type NotificationPreferences = {
  auditAlerts: boolean;
  emailEnabled: boolean;
  inAppEnabled: boolean;
  productUpdates: boolean;
  securityAlerts: boolean;
};

type PublicSettings = {
  apiStatus?: "degraded" | "healthy" | "unknown";
  backendVersion?: string;
  deploymentMode?: string;
  environment?: string;
  frontendVersion?: string;
  instanceName?: string;
  publicUrl?: string;
};

type SettingsPermissions = Partial<{
  read: boolean;
  update: boolean;
  updateNotifications: boolean;
  updatePreferences: boolean;
}>;

type SettingsState = {
  notifications: NotificationPreferences;
  permissions: SettingsPermissions;
  preferences: UserPreferences;
  publicSettings: PublicSettings;
};

export type {
  DateTimeFormat,
  DisplayDensity,
  LanguagePreference,
  NotificationPreferences,
  PublicSettings,
  SettingsPermissions,
  SettingsState,
  ThemePreference,
  UserPreferences,
};
