import type { RequestCredentialsMode } from "./types";

type AppEnvironment = "development" | "local" | "production" | "staging" | "test";

type ApiRuntimeConfig = {
  baseUrl: string;
  credentials: RequestCredentialsMode;
  defaultHeaders: HeadersInit;
  environment: AppEnvironment;
  timeoutMs: number;
};

const DEFAULT_TIMEOUT_MS = 15_000;

function normalizeBaseUrl(baseUrl: string): string {
  const trimmedBaseUrl = baseUrl.trim();

  if (!trimmedBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL must be configured.");
  }

  return trimmedBaseUrl.replace(/\/+$/, "");
}

function readAppEnvironment(value: string | undefined): AppEnvironment {
  if (
    value === "development" ||
    value === "local" ||
    value === "production" ||
    value === "staging" ||
    value === "test"
  ) {
    return value;
  }

  return "local";
}

function createApiRuntimeConfig(overrides: Partial<ApiRuntimeConfig> = {}): ApiRuntimeConfig {
  return {
    baseUrl: normalizeBaseUrl(overrides.baseUrl ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? ""),
    credentials: overrides.credentials ?? "include",
    defaultHeaders: overrides.defaultHeaders ?? {},
    environment: overrides.environment ?? readAppEnvironment(process.env.NEXT_PUBLIC_APP_ENV),
    timeoutMs: overrides.timeoutMs ?? DEFAULT_TIMEOUT_MS,
  };
}

const apiRuntimeConfig = createApiRuntimeConfig();

export { apiRuntimeConfig, createApiRuntimeConfig, DEFAULT_TIMEOUT_MS };
export type { ApiRuntimeConfig, AppEnvironment };
