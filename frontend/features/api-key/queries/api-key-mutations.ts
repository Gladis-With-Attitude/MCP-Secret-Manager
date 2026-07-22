import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createApiKey, revokeApiKey } from "../api/api-key-service";
import {
  mapApiKeyCreatedDtoToApiKeyCreated,
  mapApiKeyDtoToApiKey,
  mapApiKeyFormToCreateDto,
} from "../mappers/api-key-mappers";
import type { ApiKeyFormValues } from "../types/api-key";
import { apiKeyQueryKeys } from "./api-key-keys";

function useCreateApiKeyMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: ApiKeyFormValues) =>
      mapApiKeyCreatedDtoToApiKeyCreated(await createApiKey(mapApiKeyFormToCreateDto(values))),
    onSuccess: async (created) => {
      queryClient.setQueryData(apiKeyQueryKeys.detail(created.metadata.id), created.metadata);
      await queryClient.invalidateQueries({ queryKey: apiKeyQueryKeys.lists() });
    },
    retry: false,
  });
}

function useRevokeApiKeyMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (apiKeyId: string) => mapApiKeyDtoToApiKey(await revokeApiKey(apiKeyId)),
    onSuccess: async (apiKey) => {
      queryClient.setQueryData(apiKeyQueryKeys.detail(apiKey.id), apiKey);
      await queryClient.invalidateQueries({ queryKey: apiKeyQueryKeys.lists() });
    },
    retry: false,
  });
}

export { useCreateApiKeyMutation, useRevokeApiKeyMutation };
