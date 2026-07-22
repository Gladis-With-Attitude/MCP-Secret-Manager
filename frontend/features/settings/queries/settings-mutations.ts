import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateNotifications, updatePreferences } from "../api/settings-service";
import {
  mapNotificationsDtoToNotifications,
  mapNotificationsToDto,
  mapPreferencesDtoToPreferences,
  mapPreferencesToDto,
} from "../mappers/settings-mappers";
import type { NotificationPreferences, UserPreferences } from "../types/settings";
import { settingsQueryKeys } from "./settings-keys";

function useUpdatePreferencesMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: UserPreferences) =>
      mapPreferencesDtoToPreferences(await updatePreferences(mapPreferencesToDto(values))),
    onSuccess: async (preferences) => {
      queryClient.setQueryData(settingsQueryKeys.settings(), (current: unknown) =>
        current && typeof current === "object" ? { ...current, preferences } : current,
      );
      await queryClient.invalidateQueries({ queryKey: settingsQueryKeys.settings() });
    },
    retry: false,
  });
}

function useUpdateNotificationsMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: NotificationPreferences) =>
      mapNotificationsDtoToNotifications(await updateNotifications(mapNotificationsToDto(values))),
    onSuccess: async (notifications) => {
      queryClient.setQueryData(settingsQueryKeys.settings(), (current: unknown) =>
        current && typeof current === "object" ? { ...current, notifications } : current,
      );
      await queryClient.invalidateQueries({ queryKey: settingsQueryKeys.settings() });
    },
    retry: false,
  });
}

export { useUpdateNotificationsMutation, useUpdatePreferencesMutation };
