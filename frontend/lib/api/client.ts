import { type ApiRuntimeConfig, apiRuntimeConfig } from "./config";
import {
  ApiBaseError,
  ApiNetworkError,
  ApiTimeoutError,
  isApiError,
  normalizeUnknownError,
} from "./errors";
import { buildHeaders } from "./headers";
import { serializeQueryParams } from "./params";
import { parseApiResponse } from "./response";
import type { HttpMethod, RequestOptions } from "./types";

type ApiClientHooks = {
  getAdditionalHeaders?: () => HeadersInit | Promise<HeadersInit>;
  onError?: (error: ApiBaseError) => void | Promise<void>;
  onForbidden?: (error: ApiBaseError) => void | Promise<void>;
  onRequest?: (request: Request) => void | Promise<void>;
  onResponse?: (response: Response) => void | Promise<void>;
  onUnauthorized?: (error: ApiBaseError) => void | Promise<void>;
};

type ApiClient = {
  delete: <TResponse = undefined>(path: string, options?: RequestOptions) => Promise<TResponse>;
  get: <TResponse>(path: string, options?: RequestOptions) => Promise<TResponse>;
  patch: <TResponse, TBody = unknown>(
    path: string,
    body?: TBody,
    options?: RequestOptions<TBody>,
  ) => Promise<TResponse>;
  post: <TResponse, TBody = unknown>(
    path: string,
    body?: TBody,
    options?: RequestOptions<TBody>,
  ) => Promise<TResponse>;
  put: <TResponse, TBody = unknown>(
    path: string,
    body?: TBody,
    options?: RequestOptions<TBody>,
  ) => Promise<TResponse>;
  request: <TResponse, TBody = unknown>(
    path: string,
    options?: RequestOptions<TBody>,
  ) => Promise<TResponse>;
};

const SAFE_RETRY_METHODS: HttpMethod[] = ["GET", "HEAD"];
const CSRF_COOKIE_NAME = "mcp_sm_csrf";
const CSRF_HEADER_NAME = "X-CSRF-Token";
const CSRF_SAFE_METHODS: HttpMethod[] = ["GET", "HEAD"];

function buildApiUrl(baseUrl: string, path: string, params?: RequestOptions["params"]): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  return `${baseUrl}${normalizedPath}${serializeQueryParams(params)}`;
}

function serializeBody(body: unknown): BodyInit | undefined {
  if (body === undefined) {
    return undefined;
  }

  if (
    typeof body === "string" ||
    body instanceof Blob ||
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof ArrayBuffer
  ) {
    return body;
  }

  return JSON.stringify(body);
}

function readBrowserCookie(name: string): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const prefix = `${name}=`;
  const cookie = document.cookie
    .split(";")
    .map((entry) => entry.trim())
    .find((entry) => entry.startsWith(prefix));

  return cookie ? cookie.slice(prefix.length) : null;
}

function addCsrfHeader(method: HttpMethod, headers: Headers): void {
  if (CSRF_SAFE_METHODS.includes(method) || headers.has(CSRF_HEADER_NAME)) {
    return;
  }

  const csrfToken = readBrowserCookie(CSRF_COOKIE_NAME);
  if (csrfToken) {
    headers.set(CSRF_HEADER_NAME, csrfToken);
  }
}

function getRetryCount(method: HttpMethod, retry: RequestOptions["retry"]): number {
  if (!SAFE_RETRY_METHODS.includes(method)) {
    return 0;
  }

  if (typeof retry === "number") {
    return Math.max(0, retry);
  }

  return retry ? 1 : 0;
}

function shouldRetry(error: ApiBaseError): boolean {
  return (
    error.kind === "network" ||
    error.kind === "timeout" ||
    error.kind === "rate_limit" ||
    error.kind === "server"
  );
}

function createTimeoutSignal(
  timeoutMs: number,
  signal?: AbortSignal,
): { cleanup: () => void; signal: AbortSignal } {
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => {
    controller.abort(new ApiTimeoutError());
  }, timeoutMs);

  const abortFromParent = () => {
    controller.abort(signal?.reason);
  };

  if (signal) {
    if (signal.aborted) {
      abortFromParent();
    } else {
      signal.addEventListener("abort", abortFromParent, { once: true });
    }
  }

  return {
    cleanup: () => {
      globalThis.clearTimeout(timeoutId);
      signal?.removeEventListener("abort", abortFromParent);
    },
    signal: controller.signal,
  };
}

async function runErrorHooks(error: ApiBaseError, hooks: ApiClientHooks): Promise<void> {
  if (error.kind === "unauthorized") {
    await hooks.onUnauthorized?.(error);
  }

  if (error.kind === "forbidden") {
    await hooks.onForbidden?.(error);
  }

  await hooks.onError?.(error);
}

function createApiClient(
  config: ApiRuntimeConfig = apiRuntimeConfig,
  hooks: ApiClientHooks = {},
): ApiClient {
  async function request<TResponse, TBody = unknown>(
    path: string,
    options: RequestOptions<TBody> = {},
  ): Promise<TResponse> {
    const method = options.method ?? "GET";
    const retryCount = getRetryCount(method, options.retry);
    let attempt = 0;

    while (true) {
      const { cleanup, signal } = createTimeoutSignal(
        options.timeoutMs ?? config.timeoutMs,
        options.signal,
      );

      try {
        const additionalHeaders = await hooks.getAdditionalHeaders?.();
        const headers = buildHeaders({
          body: options.body,
          headers: new Headers([
            ...new Headers(config.defaultHeaders),
            ...new Headers(additionalHeaders),
            ...new Headers(options.headers),
          ]),
        });
        addCsrfHeader(method, headers);
        const requestInfo = new Request(buildApiUrl(config.baseUrl, path, options.params), {
          body: serializeBody(options.body),
          credentials: options.credentials ?? config.credentials,
          headers,
          method,
          signal,
        });

        await hooks.onRequest?.(requestInfo);

        const response = await fetch(requestInfo);
        await hooks.onResponse?.(response.clone());

        return (await parseApiResponse<TResponse>(response, method)) as TResponse;
      } catch (error) {
        const normalizedError =
          error instanceof ApiTimeoutError
            ? error
            : signal.aborted && signal.reason instanceof ApiTimeoutError
              ? signal.reason
              : isApiError(error)
                ? error
                : error instanceof TypeError
                  ? new ApiNetworkError({ cause: error })
                  : normalizeUnknownError(error);

        if (attempt < retryCount && shouldRetry(normalizedError)) {
          attempt += 1;
          cleanup();
          continue;
        }

        await runErrorHooks(normalizedError, hooks);
        throw normalizedError;
      } finally {
        cleanup();
      }
    }
  }

  return {
    delete: (path, options) => request(path, { ...options, method: "DELETE" }),
    get: (path, options) => request(path, { ...options, method: "GET" }),
    patch: (path, body, options) => request(path, { ...options, body, method: "PATCH" }),
    post: (path, body, options) => request(path, { ...options, body, method: "POST" }),
    put: (path, body, options) => request(path, { ...options, body, method: "PUT" }),
    request,
  };
}

const apiClient = createApiClient();

export { apiClient, buildApiUrl, createApiClient };
export type { ApiClient, ApiClientHooks };
