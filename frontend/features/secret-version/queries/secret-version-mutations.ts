import { useMutation, useQueryClient } from "@tanstack/react-query";

import { secretQueryKeys } from "@/features/secret";

import { createSecretVersion, restoreSecretVersion } from "../api/secret-version-service";
import {
  mapSecretVersionDtoToSecretVersion,
  mapSecretVersionFormToCreateDto,
} from "../mappers/secret-version-mappers";
import type { SecretVersionFormValues, SecretVersionRestoreValues } from "../types/secret-version";
import { secretVersionQueryKeys } from "./secret-version-keys";

function useCreateSecretVersionMutation(secretId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: SecretVersionFormValues) =>
      mapSecretVersionDtoToSecretVersion(
        await createSecretVersion(secretId, mapSecretVersionFormToCreateDto(values)),
      ),
    onSuccess: async (secretVersion) => {
      queryClient.setQueryData(
        secretVersionQueryKeys.detail(secretVersion.secretId, secretVersion.id),
        secretVersion,
      );
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: secretVersionQueryKeys.secret(secretVersion.secretId),
        }),
        queryClient.invalidateQueries({ queryKey: secretQueryKeys.detail(secretVersion.secretId) }),
      ]);
    },
    retry: false,
  });
}

function useRestoreSecretVersionMutation(secretId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: SecretVersionRestoreValues) =>
      mapSecretVersionDtoToSecretVersion(
        await restoreSecretVersion(secretId, values.versionId, { reason: values.reason }),
      ),
    onSuccess: async (secretVersion) => {
      queryClient.setQueryData(
        secretVersionQueryKeys.detail(secretVersion.secretId, secretVersion.id),
        secretVersion,
      );
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: secretVersionQueryKeys.secret(secretVersion.secretId),
        }),
        queryClient.invalidateQueries({ queryKey: secretQueryKeys.detail(secretVersion.secretId) }),
      ]);
    },
    retry: false,
  });
}

export { useCreateSecretVersionMutation, useRestoreSecretVersionMutation };
