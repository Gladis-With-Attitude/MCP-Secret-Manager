import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

import type { SecretVersionMetadata, SecretVersionStatus } from "../types/secret-version";

type SecretVersionPermissionDto = {
  create?: boolean;
  read?: boolean;
  read_value?: boolean;
  restore?: boolean;
  rotate?: boolean;
  revoke?: boolean;
};

type SecretVersionDto = {
  active?: boolean;
  algorithm?: string | null;
  created_at?: string | null;
  created_by?: string | null;
  crypto_scheme_version?: string | null;
  id: string;
  is_current?: boolean;
  key_reference?: string | null;
  metadata?: SecretVersionMetadata | null;
  note?: string | null;
  permissions?: SecretVersionPermissionDto;
  secret_id: string;
  status?: SecretVersionStatus | string | null;
  value?: string;
  version: number;
};

type SecretVersionListEnvelopeDto = PaginatedResponse<SecretVersionDto> & {
  permissions?: SecretVersionPermissionDto;
};

type SecretVersionListResponseDto =
  SecretVersionDto[] | SecretVersionListEnvelopeDto | SuccessResponse<SecretVersionDto[]>;

type CreateSecretVersionRequestDto = {
  make_current?: boolean;
  metadata?: SecretVersionMetadata;
  note?: string;
  value: string;
};

type RestoreSecretVersionRequestDto = {
  reason?: string;
};

type SecretVersionActionResponseDto = SecretVersionDto | SuccessResponse<SecretVersionDto>;

type SecretVersionListParamsDto = {
  current_only?: boolean;
  page?: number;
  page_size?: number;
  status?: string;
};

export type {
  CreateSecretVersionRequestDto,
  RestoreSecretVersionRequestDto,
  SecretVersionActionResponseDto,
  SecretVersionDto,
  SecretVersionListParamsDto,
  SecretVersionListResponseDto,
  SecretVersionPermissionDto,
};
