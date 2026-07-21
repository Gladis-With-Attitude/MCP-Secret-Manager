import {
  ApiForbiddenError,
  ApiNetworkError,
  ApiTimeoutError,
  ApiUnauthorizedError,
  isApiError,
} from "@/lib/api/errors";

import type { AuthError } from "./types";

function createAuthError(error: Omit<AuthError, "message"> & { message?: string }): AuthError {
  return {
    ...error,
    message: error.message ?? "Authentication state could not be resolved.",
  };
}

function createSessionExpiredError(cause?: unknown): AuthError {
  return createAuthError({
    cause,
    kind: "session_expired",
    message: "Your session has expired.",
  });
}

function normalizeAuthError(error: unknown): AuthError {
  if (error instanceof ApiUnauthorizedError) {
    return createAuthError({
      cause: error,
      code: error.code,
      kind: "unauthorized",
      message: error.userMessage,
    });
  }

  if (error instanceof ApiForbiddenError) {
    return createAuthError({
      cause: error,
      code: error.code,
      kind: "forbidden",
      message: error.userMessage,
    });
  }

  if (error instanceof ApiNetworkError || error instanceof ApiTimeoutError) {
    return createAuthError({
      cause: error,
      code: error.code,
      kind: "network",
      message: error.userMessage,
    });
  }

  if (isApiError(error)) {
    return createAuthError({
      cause: error,
      code: error.code,
      kind: "unknown",
      message: error.userMessage,
    });
  }

  if (error instanceof Error) {
    return createAuthError({
      cause: error,
      kind: "unknown",
      message: error.message,
    });
  }

  return createAuthError({
    cause: error,
    kind: "unknown",
  });
}

export { createAuthError, createSessionExpiredError, normalizeAuthError };
