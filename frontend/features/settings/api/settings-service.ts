import { get, patch } from "@/lib/api";

import type {
  NotificationPreferencesDto,
  SettingsResponseDto,
  UserPreferencesDto,
} from "./settings-dto";

function getSettings(): Promise<SettingsResponseDto> {
  return get<SettingsResponseDto>("/v1/me/settings");
}

function updatePreferences(body: UserPreferencesDto): Promise<UserPreferencesDto> {
  return patch<UserPreferencesDto, UserPreferencesDto>("/v1/me/preferences", body);
}

function updateNotifications(
  body: NotificationPreferencesDto,
): Promise<NotificationPreferencesDto> {
  return patch<NotificationPreferencesDto, NotificationPreferencesDto>(
    "/v1/me/notifications",
    body,
  );
}

const settingsService = {
  getSettings,
  updateNotifications,
  updatePreferences,
};

export { getSettings, settingsService, updateNotifications, updatePreferences };
