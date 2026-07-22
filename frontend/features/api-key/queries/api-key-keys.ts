import type { ApiKeyListFilters } from "../types/api-key";

const apiKeyQueryKeys = {
  all: ["api-keys"] as const,
  detail: (apiKeyId: string) => [...apiKeyQueryKeys.details(), apiKeyId] as const,
  details: () => [...apiKeyQueryKeys.all, "detail"] as const,
  list: (filters: ApiKeyListFilters = {}) => [...apiKeyQueryKeys.lists(), filters] as const,
  lists: () => [...apiKeyQueryKeys.all, "list"] as const,
};

export { apiKeyQueryKeys };
