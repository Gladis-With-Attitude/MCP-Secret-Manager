import { useQuery } from "@tanstack/react-query";

import { getApiKey, listApiKeys } from "../api/api-key-service";
import {
  mapApiKeyDtoToApiKey,
  mapApiKeyFiltersToParams,
  mapApiKeyListResponseToApiKeyList,
} from "../mappers/api-key-mappers";
import type { ApiKeyListFilters } from "../types/api-key";
import { apiKeyQueryKeys } from "./api-key-keys";

function useApiKeyListQuery(filters: ApiKeyListFilters = {}) {
  return useQuery({
    queryFn: async () =>
      mapApiKeyListResponseToApiKeyList(await listApiKeys(mapApiKeyFiltersToParams(filters))),
    queryKey: apiKeyQueryKeys.list(filters),
  });
}

function useApiKeyDetailQuery(apiKeyId: string) {
  return useQuery({
    enabled: Boolean(apiKeyId),
    queryFn: async () => mapApiKeyDtoToApiKey(await getApiKey(apiKeyId)),
    queryKey: apiKeyQueryKeys.detail(apiKeyId),
  });
}

export { useApiKeyDetailQuery, useApiKeyListQuery };
