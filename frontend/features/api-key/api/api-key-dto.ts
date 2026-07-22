import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

import type { ApiKeyOwnerType } from "../types/api-key";

type ApiKeyPermissionDto = {
  create?: boolean;
  read?: boolean;
  revoke?: boolean;
};

type ApiKeyDto = {
  created_at?: string | null;
  created_by?: string | null;
  description?: string | null;
  expires_at?: string | null;
  granted_permissions?: string[] | null;
  id: string;
  key_prefix?: string | null;
  last_used_at?: string | null;
  name?: string | null;
  owner_id?: string | null;
  owner_name?: string | null;
  owner_type?: ApiKeyOwnerType | string | null;
  permissions?: ApiKeyPermissionDto;
  permission_names?: string[] | null;
  revoked_at?: string | null;
  roles?: string[] | null;
  scopes?: string[] | null;
  status?: string | null;
  token?: string;
};

type ApiKeyCreatedDto = ApiKeyDto & {
  api_key?: string;
  token?: string;
};

type ApiKeyListEnvelopeDto = PaginatedResponse<ApiKeyDto> & {
  permissions?: ApiKeyPermissionDto;
};

type ApiKeyListResponseDto = ApiKeyDto[] | ApiKeyListEnvelopeDto | SuccessResponse<ApiKeyDto[]>;

type ApiKeyActionResponseDto = ApiKeyDto | SuccessResponse<ApiKeyDto>;
type ApiKeyCreatedResponseDto = ApiKeyCreatedDto | SuccessResponse<ApiKeyCreatedDto>;

type CreateApiKeyRequestDto = {
  description?: string;
  expires_at?: string;
  name: string;
  owner_id: string;
  owner_type: ApiKeyOwnerType;
  permissions: string[];
  scopes: string[];
};

type ApiKeyListParamsDto = {
  page?: number;
  page_size?: number;
  q?: string;
  search?: string;
  status?: string;
};

export type {
  ApiKeyActionResponseDto,
  ApiKeyCreatedDto,
  ApiKeyCreatedResponseDto,
  ApiKeyDto,
  ApiKeyListParamsDto,
  ApiKeyListResponseDto,
  ApiKeyPermissionDto,
  CreateApiKeyRequestDto,
};
