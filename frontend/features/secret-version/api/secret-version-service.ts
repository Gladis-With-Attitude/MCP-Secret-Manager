import { get, post } from "@/lib/api";

import type {
  CreateSecretVersionRequestDto,
  RestoreSecretVersionRequestDto,
  SecretVersionActionResponseDto,
  SecretVersionDto,
  SecretVersionListParamsDto,
  SecretVersionListResponseDto,
} from "./secret-version-dto";

function unwrapSecretVersionResponse(response: SecretVersionActionResponseDto): SecretVersionDto {
  return "data" in response ? response.data : response;
}

async function listSecretVersions(
  secretId: string,
  params?: SecretVersionListParamsDto,
): Promise<SecretVersionListResponseDto> {
  return get<SecretVersionListResponseDto>(`/v1/secrets/${secretId}/versions`, { params });
}

async function getSecretVersion(secretId: string, versionId: string): Promise<SecretVersionDto> {
  const response = await get<SecretVersionActionResponseDto>(
    `/v1/secrets/${secretId}/versions/${versionId}`,
  );

  return unwrapSecretVersionResponse(response);
}

async function getCurrentSecretVersion(secretId: string): Promise<SecretVersionDto> {
  const response = await get<SecretVersionActionResponseDto>(
    `/v1/secrets/${secretId}/versions/latest`,
  );

  return unwrapSecretVersionResponse(response);
}

async function createSecretVersion(
  secretId: string,
  payload: CreateSecretVersionRequestDto,
): Promise<SecretVersionDto> {
  const response = await post<SecretVersionActionResponseDto, CreateSecretVersionRequestDto>(
    `/v1/secrets/${secretId}/versions`,
    payload,
    { retry: false },
  );

  return unwrapSecretVersionResponse(response);
}

async function restoreSecretVersion(
  secretId: string,
  versionId: string,
  payload: RestoreSecretVersionRequestDto = {},
): Promise<SecretVersionDto> {
  const response = await post<SecretVersionActionResponseDto, RestoreSecretVersionRequestDto>(
    `/v1/secrets/${secretId}/versions/${versionId}/restore`,
    payload,
    { retry: false },
  );

  return unwrapSecretVersionResponse(response);
}

const secretVersionService = {
  createSecretVersion,
  getCurrentSecretVersion,
  getSecretVersion,
  listSecretVersions,
  restoreSecretVersion,
};

export {
  createSecretVersion,
  getCurrentSecretVersion,
  getSecretVersion,
  listSecretVersions,
  restoreSecretVersion,
  secretVersionService,
};
