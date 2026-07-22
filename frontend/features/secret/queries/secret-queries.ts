import { useQuery } from "@tanstack/react-query";

import { getSecret, listSecrets, searchSecrets } from "../api/secret-service";
import {
  mapSecretDtoToSecret,
  mapSecretFiltersToParams,
  mapSecretListResponseToSecretList,
} from "../mappers/secret-mappers";
import type { SecretListFilters } from "../types/secret";
import { secretQueryKeys } from "./secret-keys";

function useSecretListQuery(projectId: string, filters: SecretListFilters = {}) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const params = mapSecretFiltersToParams(filters);
      const response = filters.search?.trim()
        ? await searchSecrets(projectId, params)
        : await listSecrets(projectId, params);

      return mapSecretListResponseToSecretList(response, projectId);
    },
    queryKey: secretQueryKeys.list(projectId, filters),
  });
}

function useSecretDetailQuery(secretId: string) {
  return useQuery({
    enabled: Boolean(secretId),
    queryFn: async () => mapSecretDtoToSecret(await getSecret(secretId)),
    queryKey: secretQueryKeys.detail(secretId),
  });
}

export { useSecretDetailQuery, useSecretListQuery };
