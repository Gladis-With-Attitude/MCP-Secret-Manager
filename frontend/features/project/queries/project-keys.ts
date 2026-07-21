import type { ProjectListFilters } from "../types/project";

const projectQueryKeys = {
  all: ["projects"] as const,
  detail: (projectId: string) => [...projectQueryKeys.details(), projectId] as const,
  details: () => [...projectQueryKeys.all, "detail"] as const,
  list: (vaultId: string, filters: ProjectListFilters = {}) =>
    [...projectQueryKeys.lists(), vaultId, filters] as const,
  lists: () => [...projectQueryKeys.all, "list"] as const,
  vault: (vaultId: string) => [...projectQueryKeys.lists(), vaultId] as const,
};

export { projectQueryKeys };
