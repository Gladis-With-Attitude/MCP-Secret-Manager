import { useQuery } from "@tanstack/react-query";

import {
  getCurrentSecretVersion,
  getSecretVersion,
  listSecretVersions,
} from "../api/secret-version-service";
import {
  mapSecretVersionDtoToSecretVersion,
  mapSecretVersionFiltersToParams,
  mapSecretVersionListResponseToSecretVersionList,
} from "../mappers/secret-version-mappers";
import type { SecretVersionListFilters } from "../types/secret-version";
import { secretVersionQueryKeys } from "./secret-version-keys";

function useSecretVersionListQuery(secretId: string, filters: SecretVersionListFilters = {}) {
  return useQuery({
    enabled: Boolean(secretId),
    queryFn: async () =>
      mapSecretVersionListResponseToSecretVersionList(
        await listSecretVersions(secretId, mapSecretVersionFiltersToParams(filters)),
        secretId,
      ),
    queryKey: secretVersionQueryKeys.list(secretId, filters),
  });
}

function useSecretVersionDetailQuery(secretId: string, versionId: string) {
  return useQuery({
    enabled: Boolean(secretId && versionId),
    queryFn: async () =>
      mapSecretVersionDtoToSecretVersion(await getSecretVersion(secretId, versionId)),
    queryKey: secretVersionQueryKeys.detail(secretId, versionId),
  });
}

function useCurrentSecretVersionQuery(secretId: string) {
  return useQuery({
    enabled: Boolean(secretId),
    queryFn: async () =>
      mapSecretVersionDtoToSecretVersion(await getCurrentSecretVersion(secretId)),
    queryKey: secretVersionQueryKeys.current(secretId),
    retry: false,
  });
}

export { useCurrentSecretVersionQuery, useSecretVersionDetailQuery, useSecretVersionListQuery };
