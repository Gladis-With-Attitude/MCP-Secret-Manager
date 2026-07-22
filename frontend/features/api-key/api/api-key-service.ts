import { get, post } from "@/lib/api";

import type {
  ApiKeyActionResponseDto,
  ApiKeyCreatedResponseDto,
  ApiKeyDto,
  ApiKeyListParamsDto,
  ApiKeyListResponseDto,
  CreateApiKeyRequestDto,
} from "./api-key-dto";

function unwrapApiKeyResponse(response: ApiKeyActionResponseDto): ApiKeyDto {
  return "data" in response ? response.data : response;
}

async function listApiKeys(params?: ApiKeyListParamsDto): Promise<ApiKeyListResponseDto> {
  return get<ApiKeyListResponseDto>("/v1/tokens", { params });
}

async function getApiKey(apiKeyId: string): Promise<ApiKeyDto> {
  const response = await get<ApiKeyActionResponseDto>(`/v1/tokens/${apiKeyId}`);

  return unwrapApiKeyResponse(response);
}

async function createApiKey(payload: CreateApiKeyRequestDto): Promise<ApiKeyCreatedResponseDto> {
  return post<ApiKeyCreatedResponseDto, CreateApiKeyRequestDto>("/v1/tokens", payload, {
    retry: false,
  });
}

async function revokeApiKey(apiKeyId: string): Promise<ApiKeyDto> {
  const response = await post<ApiKeyActionResponseDto>(`/v1/tokens/${apiKeyId}/revoke`, undefined, {
    retry: false,
  });

  return unwrapApiKeyResponse(response);
}

const apiKeyService = {
  createApiKey,
  getApiKey,
  listApiKeys,
  revokeApiKey,
};

export { apiKeyService, createApiKey, getApiKey, listApiKeys, revokeApiKey };
