import { get, patch, post } from "@/lib/api";

import type {
  CreateSecretRequestDto,
  SecretActionResponseDto,
  SecretDto,
  SecretListParamsDto,
  SecretListResponseDto,
  SecretValueResponseDto,
  UpdateSecretRequestDto,
} from "./secret-dto";

function unwrapSecretResponse(response: SecretActionResponseDto): SecretDto {
  return "data" in response ? response.data : response;
}

async function listSecrets(
  projectId: string,
  params?: SecretListParamsDto,
): Promise<SecretListResponseDto> {
  return get<SecretListResponseDto>(`/v1/projects/${projectId}/secrets`, { params });
}

async function searchSecrets(
  projectId: string,
  params?: SecretListParamsDto,
): Promise<SecretListResponseDto> {
  return get<SecretListResponseDto>(`/v1/projects/${projectId}/secrets`, { params });
}

async function getSecret(secretId: string): Promise<SecretDto> {
  const response = await get<SecretActionResponseDto>(`/v1/secrets/${secretId}`);

  return unwrapSecretResponse(response);
}

async function createSecret(
  projectId: string,
  payload: CreateSecretRequestDto,
): Promise<SecretDto> {
  const response = await post<SecretActionResponseDto, CreateSecretRequestDto>(
    `/v1/projects/${projectId}/secrets`,
    payload,
  );

  return unwrapSecretResponse(response);
}

async function updateSecret(secretId: string, payload: UpdateSecretRequestDto): Promise<SecretDto> {
  const response = await patch<SecretActionResponseDto, UpdateSecretRequestDto>(
    `/v1/secrets/${secretId}`,
    payload,
  );

  return unwrapSecretResponse(response);
}

async function archiveSecret(secretId: string): Promise<SecretDto> {
  const response = await post<SecretActionResponseDto>(`/v1/secrets/${secretId}/archive`);

  return unwrapSecretResponse(response);
}

async function readSecretValue(secretId: string): Promise<SecretValueResponseDto> {
  return get<SecretValueResponseDto>(`/v1/secrets/${secretId}/versions/latest`, {
    retry: false,
  });
}

const secretService = {
  archiveSecret,
  createSecret,
  getSecret,
  listSecrets,
  readSecretValue,
  searchSecrets,
  updateSecret,
};

export {
  archiveSecret,
  createSecret,
  getSecret,
  listSecrets,
  readSecretValue,
  searchSecrets,
  secretService,
  updateSecret,
};
