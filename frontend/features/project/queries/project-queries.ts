import { useQuery } from "@tanstack/react-query";

import { getProject, listProjects } from "../api/project-service";
import {
  mapProjectDtoToProject,
  mapProjectFiltersToParams,
  mapProjectListResponseToProjectList,
} from "../mappers/project-mappers";
import type { ProjectListFilters } from "../types/project";
import { projectQueryKeys } from "./project-keys";

function useProjectListQuery(vaultId: string, filters: ProjectListFilters = {}) {
  return useQuery({
    enabled: Boolean(vaultId),
    queryFn: async () =>
      mapProjectListResponseToProjectList(
        await listProjects(vaultId, mapProjectFiltersToParams(filters)),
        vaultId,
      ),
    queryKey: projectQueryKeys.list(vaultId, filters),
  });
}

function useProjectDetailQuery(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => mapProjectDtoToProject(await getProject(projectId)),
    queryKey: projectQueryKeys.detail(projectId),
  });
}

export { useProjectDetailQuery, useProjectListQuery };
