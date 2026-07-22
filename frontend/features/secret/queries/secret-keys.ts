import type { SecretListFilters } from "../types/secret";

const secretQueryKeys = {
  all: ["secrets"] as const,
  detail: (secretId: string) => [...secretQueryKeys.details(), secretId] as const,
  details: () => [...secretQueryKeys.all, "detail"] as const,
  list: (projectId: string, filters: SecretListFilters = {}) =>
    [...secretQueryKeys.lists(), projectId, filters] as const,
  lists: () => [...secretQueryKeys.all, "list"] as const,
  project: (projectId: string) => [...secretQueryKeys.lists(), projectId] as const,
};

export { secretQueryKeys };
