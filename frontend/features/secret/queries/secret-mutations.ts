import { useMutation, useQueryClient } from "@tanstack/react-query";

import { archiveSecret, createSecret, updateSecret } from "../api/secret-service";
import {
  mapSecretDtoToSecret,
  mapSecretFormToCreateDto,
  mapSecretFormToUpdateDto,
} from "../mappers/secret-mappers";
import type { SecretFormValues } from "../types/secret";
import { secretQueryKeys } from "./secret-keys";

function useCreateSecretMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: SecretFormValues) =>
      mapSecretDtoToSecret(await createSecret(projectId, mapSecretFormToCreateDto(values))),
    onSuccess: async (secret) => {
      queryClient.setQueryData(secretQueryKeys.detail(secret.id), secret);
      await queryClient.invalidateQueries({ queryKey: secretQueryKeys.project(secret.projectId) });
    },
    retry: false,
  });
}

function useUpdateSecretMutation(secretId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: SecretFormValues) =>
      mapSecretDtoToSecret(await updateSecret(secretId, mapSecretFormToUpdateDto(values))),
    onSuccess: async (secret) => {
      queryClient.setQueryData(secretQueryKeys.detail(secret.id), secret);
      await queryClient.invalidateQueries({ queryKey: secretQueryKeys.project(secret.projectId) });
    },
    retry: false,
  });
}

function useArchiveSecretMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (secretId: string) => mapSecretDtoToSecret(await archiveSecret(secretId)),
    onSuccess: async (secret) => {
      queryClient.setQueryData(secretQueryKeys.detail(secret.id), secret);
      await queryClient.invalidateQueries({ queryKey: secretQueryKeys.project(secret.projectId) });
    },
    retry: false,
  });
}

export { useArchiveSecretMutation, useCreateSecretMutation, useUpdateSecretMutation };
