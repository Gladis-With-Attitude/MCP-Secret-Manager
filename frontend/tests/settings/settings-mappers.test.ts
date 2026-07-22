import { describe, expect, it } from "vitest";

import {
  canUseSettingsAction,
  defaultNotifications,
  mapNotificationsToDto,
  mapPreferencesDtoToPreferences,
  mapPreferencesToDto,
  mapSettingsResponseToSettingsState,
} from "@/features/settings";

describe("settings mappers", () => {
  it("normalizes preferences and public settings", () => {
    const state = mapSettingsResponseToSettingsState({
      permissions: { update_preferences: false },
      preferences: {
        language: "fr",
        theme: "dark",
        timezone: "Europe/Paris",
      },
      public_settings: {
        api_status: "healthy",
        environment: "local",
      },
    });

    expect(state.preferences.language).toBe("fr");
    expect(state.preferences.theme).toBe("dark");
    expect(state.publicSettings.apiStatus).toBe("healthy");
    expect(canUseSettingsAction(state.permissions, "updatePreferences")).toBe(false);
  });

  it("maps preference and notification DTOs", () => {
    expect(
      mapPreferencesDtoToPreferences({ language: "unsupported", theme: "nope" }),
    ).toMatchObject({
      language: "en",
      theme: "system",
    });
    expect(
      mapPreferencesToDto({
        dateTimeFormat: "short",
        displayDensity: "compact",
        language: "fr",
        theme: "light",
        timezone: "Europe/Paris",
      }),
    ).toMatchObject({
      date_time_format: "short",
      display_density: "compact",
      language: "fr",
      theme: "light",
    });
    expect(mapNotificationsToDto(defaultNotifications).security_alerts).toBe(true);
  });
});
