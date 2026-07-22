import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

import type { SecretMetadata, SecretType } from "../types/secret";

type SecretPermissionDto = {
  archive?: boolean;
  create?: boolean;
  delete?: boolean;
  read?: boolean;
  read_value?: boolean;
  update?: boolean;
};

type SecretDto = {
  archived?: boolean;
  created_at?: string | null;
  created_by?: string | null;
  current_version?: number | null;
  description?: string | null;
  id: string;
  key?: string;
  last_version_at?: string | null;
  metadata?: SecretMetadata | null;
  name?: string;
  permissions?: SecretPermissionDto;
  project_id: string;
  project_name?: string | null;
  provider?: string | null;
  status?: string | null;
  tags?: string[] | null;
  type?: SecretType | string | null;
  updated_at?: string | null;
  vault_id?: string | null;
  vault_name?: string | null;
  version_count?: number | null;
};

type SecretListEnvelopeDto = PaginatedResponse<SecretDto> & {
  permissions?: SecretPermissionDto;
};

type SecretListResponseDto = SecretDto[] | SecretListEnvelopeDto | SuccessResponse<SecretDto[]>;

type CreateSecretRequestDto = {
  description?: string;
  key: string;
  metadata?: SecretMetadata;
  tags?: string[];
  type?: SecretType;
};

type UpdateSecretRequestDto = {
  description?: string;
  key: string;
  metadata?: SecretMetadata;
  tags?: string[];
  type?: SecretType;
};

type SecretListParamsDto = {
  archived?: boolean;
  page?: number;
  page_size?: number;
  provider?: string;
  q?: string;
  search?: string;
  status?: string;
  type?: string;
};

type SecretActionResponseDto = SecretDto | SuccessResponse<SecretDto>;

type SecretValueResponseDto =
  | {
      expires_at?: string | null;
      value: string;
    }
  | SuccessResponse<{
      expires_at?: string | null;
      value: string;
    }>;

export type {
  CreateSecretRequestDto,
  SecretActionResponseDto,
  SecretDto,
  SecretListParamsDto,
  SecretListResponseDto,
  SecretPermissionDto,
  SecretValueResponseDto,
  UpdateSecretRequestDto,
};
