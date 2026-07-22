import type {
  NotificationPreferencesDto,
  PublicSettingsDto,
  SettingsPermissionDto,
  SettingsResponseDto,
  UserPreferencesDto,
} from "../api/settings-dto";
import type {
  DateTimeFormat,
  DisplayDensity,
  LanguagePreference,
  NotificationPreferences,
  PublicSettings,
  SettingsPermissions,
  SettingsState,
  ThemePreference,
  UserPreferences,
} from "../types/settings";

const defaultPreferences: UserPreferences = {
  dateTimeFormat: "absolute",
  displayDensity: "comfortable",
  language: "en",
  theme: "system",
  timezone: "UTC",
};

const defaultNotifications: NotificationPreferences = {
  auditAlerts: true,
  emailEnabled: true,
  inAppEnabled: true,
  productUpdates: false,
  securityAlerts: true,
};

function normalizeTheme(value?: string | null): ThemePreference {
  return value === "light" || value === "dark" || value === "system" ? value : "system";
}

function normalizeLanguage(value?: string | null): LanguagePreference {
  return value === "fr" ? "fr" : "en";
}

function normalizeDateTimeFormat(value?: string | null): DateTimeFormat {
  return value === "relative" || value === "short" ? value : "absolute";
}

function normalizeDisplayDensity(value?: string | null): DisplayDensity {
  return value === "compact" ? "compact" : "comfortable";
}

function mapPreferencesDtoToPreferences(dto?: UserPreferencesDto | null): UserPreferences {
  return {
    dateTimeFormat: normalizeDateTimeFormat(dto?.date_time_format),
    displayDensity: normalizeDisplayDensity(dto?.display_density),
    language: normalizeLanguage(dto?.language),
    theme: normalizeTheme(dto?.theme),
    timezone: dto?.timezone || defaultPreferences.timezone,
  };
}

function mapPreferencesToDto(preferences: UserPreferences): UserPreferencesDto {
  return {
    date_time_format: preferences.dateTimeFormat,
    display_density: preferences.displayDensity,
    language: preferences.language,
    theme: preferences.theme,
    timezone: preferences.timezone,
  };
}

function mapNotificationsDtoToNotifications(
  dto?: NotificationPreferencesDto | null,
): NotificationPreferences {
  return {
    auditAlerts: dto?.audit_alerts ?? defaultNotifications.auditAlerts,
    emailEnabled: dto?.email_enabled ?? defaultNotifications.emailEnabled,
    inAppEnabled: dto?.in_app_enabled ?? defaultNotifications.inAppEnabled,
    productUpdates: dto?.product_updates ?? defaultNotifications.productUpdates,
    securityAlerts: dto?.security_alerts ?? defaultNotifications.securityAlerts,
  };
}

function mapNotificationsToDto(notifications: NotificationPreferences): NotificationPreferencesDto {
  return {
    audit_alerts: notifications.auditAlerts,
    email_enabled: notifications.emailEnabled,
    in_app_enabled: notifications.inAppEnabled,
    product_updates: notifications.productUpdates,
    security_alerts: notifications.securityAlerts,
  };
}

function mapPublicSettingsDtoToPublicSettings(dto?: PublicSettingsDto | null): PublicSettings {
  return {
    apiStatus:
      dto?.api_status === "healthy" || dto?.api_status === "degraded" ? dto.api_status : "unknown",
    backendVersion: dto?.backend_version ?? undefined,
    deploymentMode: dto?.deployment_mode ?? undefined,
    environment: dto?.environment ?? undefined,
    frontendVersion: dto?.frontend_version ?? undefined,
    instanceName: dto?.instance_name ?? undefined,
    publicUrl: dto?.public_url ?? undefined,
  };
}

function mapSettingsPermissions(dto?: SettingsPermissionDto | null): SettingsPermissions {
  return {
    read: dto?.read,
    update: dto?.update,
    updateNotifications: dto?.update_notifications,
    updatePreferences: dto?.update_preferences,
  };
}

function mapSettingsResponseToSettingsState(dto: SettingsResponseDto): SettingsState {
  return {
    notifications: mapNotificationsDtoToNotifications(dto.notifications),
    permissions: mapSettingsPermissions(dto.permissions),
    preferences: mapPreferencesDtoToPreferences(dto.preferences),
    publicSettings: mapPublicSettingsDtoToPublicSettings(dto.public_settings),
  };
}

function canUseSettingsAction(
  permissions: SettingsPermissions,
  action: keyof SettingsPermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseSettingsAction,
  defaultNotifications,
  defaultPreferences,
  mapNotificationsDtoToNotifications,
  mapNotificationsToDto,
  mapPreferencesDtoToPreferences,
  mapPreferencesToDto,
  mapPublicSettingsDtoToPublicSettings,
  mapSettingsPermissions,
  mapSettingsResponseToSettingsState,
};
