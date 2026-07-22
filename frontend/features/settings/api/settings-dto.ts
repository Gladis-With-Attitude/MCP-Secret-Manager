type UserPreferencesDto = {
  date_time_format?: string | null;
  display_density?: string | null;
  language?: string | null;
  theme?: string | null;
  timezone?: string | null;
};

type NotificationPreferencesDto = {
  audit_alerts?: boolean | null;
  email_enabled?: boolean | null;
  in_app_enabled?: boolean | null;
  product_updates?: boolean | null;
  security_alerts?: boolean | null;
};

type PublicSettingsDto = {
  api_status?: string | null;
  backend_version?: string | null;
  deployment_mode?: string | null;
  environment?: string | null;
  frontend_version?: string | null;
  instance_name?: string | null;
  public_url?: string | null;
};

type SettingsPermissionDto = {
  read?: boolean;
  update?: boolean;
  update_notifications?: boolean;
  update_preferences?: boolean;
};

type SettingsResponseDto = {
  notifications?: NotificationPreferencesDto | null;
  permissions?: SettingsPermissionDto | null;
  preferences?: UserPreferencesDto | null;
  public_settings?: PublicSettingsDto | null;
};

export type {
  NotificationPreferencesDto,
  PublicSettingsDto,
  SettingsPermissionDto,
  SettingsResponseDto,
  UserPreferencesDto,
};
