import { get, patch, post } from "@/lib/api";

import type {
  CreateProjectRequestDto,
  ProjectActionResponseDto,
  ProjectDto,
  ProjectListParamsDto,
  ProjectListResponseDto,
  UpdateProjectRequestDto,
} from "./project-dto";

function unwrapProjectResponse(response: ProjectActionResponseDto): ProjectDto {
  return "data" in response ? response.data : response;
}

async function listProjects(
  vaultId: string,
  params?: ProjectListParamsDto,
): Promise<ProjectListResponseDto> {
  return get<ProjectListResponseDto>(`/v1/vaults/${vaultId}/projects`, { params });
}

async function getProject(projectId: string): Promise<ProjectDto> {
  const response = await get<ProjectActionResponseDto>(`/v1/projects/${projectId}`);

  return unwrapProjectResponse(response);
}

async function createProject(
  vaultId: string,
  payload: CreateProjectRequestDto,
): Promise<ProjectDto> {
  const response = await post<ProjectActionResponseDto, CreateProjectRequestDto>(
    `/v1/vaults/${vaultId}/projects`,
    payload,
  );

  return unwrapProjectResponse(response);
}

async function updateProject(
  projectId: string,
  payload: UpdateProjectRequestDto,
): Promise<ProjectDto> {
  const response = await patch<ProjectActionResponseDto, UpdateProjectRequestDto>(
    `/v1/projects/${projectId}`,
    payload,
  );

  return unwrapProjectResponse(response);
}

async function archiveProject(projectId: string): Promise<ProjectDto> {
  const response = await post<ProjectActionResponseDto>(`/v1/projects/${projectId}/archive`);

  return unwrapProjectResponse(response);
}

const projectService = {
  archiveProject,
  createProject,
  getProject,
  listProjects,
  updateProject,
};

export { archiveProject, createProject, getProject, listProjects, projectService, updateProject };
