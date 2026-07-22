import type { SecretVersionListFilters } from "../types/secret-version";

const secretVersionQueryKeys = {
  all: ["secret-versions"] as const,
  current: (secretId: string) => [...secretVersionQueryKeys.secret(secretId), "current"] as const,
  detail: (secretId: string, versionId: string) =>
    [...secretVersionQueryKeys.details(secretId), versionId] as const,
  details: (secretId: string) => [...secretVersionQueryKeys.secret(secretId), "detail"] as const,
  list: (secretId: string, filters: SecretVersionListFilters = {}) =>
    [...secretVersionQueryKeys.lists(secretId), filters] as const,
  lists: (secretId: string) => [...secretVersionQueryKeys.secret(secretId), "list"] as const,
  secret: (secretId: string) => [...secretVersionQueryKeys.all, secretId] as const,
};

export { secretVersionQueryKeys };
