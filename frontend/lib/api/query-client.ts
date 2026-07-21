import { QueryClient } from "@tanstack/react-query";

import { isApiError } from "./errors";

const QUERY_STALE_TIME_MS = 60 * 1000;
const QUERY_GC_TIME_MS = 5 * 60 * 1000;

function shouldRetryQuery(failureCount: number, error: unknown): boolean {
  if (failureCount >= 1) {
    return false;
  }

  if (!isApiError(error)) {
    return true;
  }

  return (
    error.kind === "network" ||
    error.kind === "timeout" ||
    error.kind === "rate_limit" ||
    error.kind === "server"
  );
}

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      mutations: {
        retry: false,
      },
      queries: {
        gcTime: QUERY_GC_TIME_MS,
        refetchOnReconnect: true,
        refetchOnWindowFocus: false,
        retry: shouldRetryQuery,
        staleTime: QUERY_STALE_TIME_MS,
        throwOnError: false,
      },
    },
  });
}

export { createQueryClient, QUERY_GC_TIME_MS, QUERY_STALE_TIME_MS, shouldRetryQuery };
