import { apiClient } from "./client";
import type { RequestOptions } from "./types";

function get<TResponse>(path: string, options?: RequestOptions): Promise<TResponse> {
  return apiClient.get<TResponse>(path, options);
}

function post<TResponse, TBody = unknown>(
  path: string,
  body?: TBody,
  options?: RequestOptions<TBody>,
): Promise<TResponse> {
  return apiClient.post<TResponse, TBody>(path, body, options);
}

function put<TResponse, TBody = unknown>(
  path: string,
  body?: TBody,
  options?: RequestOptions<TBody>,
): Promise<TResponse> {
  return apiClient.put<TResponse, TBody>(path, body, options);
}

function patch<TResponse, TBody = unknown>(
  path: string,
  body?: TBody,
  options?: RequestOptions<TBody>,
): Promise<TResponse> {
  return apiClient.patch<TResponse, TBody>(path, body, options);
}

function remove<TResponse = undefined>(path: string, options?: RequestOptions): Promise<TResponse> {
  return apiClient.delete<TResponse>(path, options);
}

export { get, patch, post, put, remove };
