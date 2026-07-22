import { useMutation, useQueryClient } from "@tanstack/react-query";

import { changePassword, revokeSession, updateCurrentProfile } from "../api/profile-service";
import {
  mapChangePasswordToDto,
  mapProfileFormToUpdateDto,
  mapUserProfileDtoToUserProfile,
} from "../mappers/profile-mappers";
import type { ChangePasswordValues, ProfileFormValues } from "../types/profile";
import { profileQueryKeys } from "./profile-keys";

function useUpdateProfileMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: ProfileFormValues) =>
      mapUserProfileDtoToUserProfile(await updateCurrentProfile(mapProfileFormToUpdateDto(values))),
    onSuccess: async (profile) => {
      queryClient.setQueryData(profileQueryKeys.user(), profile);
      await queryClient.invalidateQueries({ queryKey: profileQueryKeys.user() });
    },
    retry: false,
  });
}

function useChangePasswordMutation() {
  return useMutation({
    mutationFn: async (values: ChangePasswordValues) =>
      changePassword(mapChangePasswordToDto(values)),
    retry: false,
  });
}

function useRevokeSessionMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sessionId: string) => revokeSession(sessionId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: profileQueryKeys.sessions() });
    },
    retry: false,
  });
}

export { useChangePasswordMutation, useRevokeSessionMutation, useUpdateProfileMutation };
