import { useMutation, useQueryClient } from "@tanstack/react-query";

import { archiveProject, createProject, updateProject } from "../api/project-service";
import {
  mapProjectDtoToProject,
  mapProjectFormToCreateDto,
  mapProjectFormToUpdateDto,
} from "../mappers/project-mappers";
import type { ProjectFormValues } from "../types/project";
import { projectQueryKeys } from "./project-keys";

function useCreateProjectMutation(vaultId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: ProjectFormValues) =>
      mapProjectDtoToProject(await createProject(vaultId, mapProjectFormToCreateDto(values))),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectQueryKeys.detail(project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectQueryKeys.vault(project.vaultId) });
    },
    retry: false,
  });
}

function useUpdateProjectMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: ProjectFormValues) =>
      mapProjectDtoToProject(await updateProject(projectId, mapProjectFormToUpdateDto(values))),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectQueryKeys.detail(project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectQueryKeys.vault(project.vaultId) });
    },
    retry: false,
  });
}

function useArchiveProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectId: string) =>
      mapProjectDtoToProject(await archiveProject(projectId)),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectQueryKeys.detail(project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectQueryKeys.vault(project.vaultId) });
    },
    retry: false,
  });
}

export { useArchiveProjectMutation, useCreateProjectMutation, useUpdateProjectMutation };
