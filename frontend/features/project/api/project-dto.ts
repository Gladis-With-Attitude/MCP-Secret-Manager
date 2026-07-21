import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

type ProjectPermissionDto = {
  archive?: boolean;
  create?: boolean;
  delete?: boolean;
  read?: boolean;
  update?: boolean;
};

type ProjectDto = {
  archived?: boolean;
  created_at?: string | null;
  created_by?: string | null;
  description?: string | null;
  id: string;
  name: string;
  permissions?: ProjectPermissionDto;
  secret_count?: number | null;
  status?: string | null;
  updated_at?: string | null;
  vault_id: string;
  vault_name?: string | null;
  version_count?: number | null;
};

type ProjectListEnvelopeDto = PaginatedResponse<ProjectDto> & {
  permissions?: ProjectPermissionDto;
};

type ProjectListResponseDto = ProjectDto[] | ProjectListEnvelopeDto | SuccessResponse<ProjectDto[]>;

type CreateProjectRequestDto = {
  description?: string;
  name: string;
};

type UpdateProjectRequestDto = {
  description?: string;
  name: string;
};

type ProjectListParamsDto = {
  archived?: boolean;
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
};

type ProjectActionResponseDto = ProjectDto | SuccessResponse<ProjectDto>;

export type {
  CreateProjectRequestDto,
  ProjectActionResponseDto,
  ProjectDto,
  ProjectListParamsDto,
  ProjectListResponseDto,
  ProjectPermissionDto,
  UpdateProjectRequestDto,
};
