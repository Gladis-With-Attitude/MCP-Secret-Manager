import type { APIError } from "./types";

type ApiErrorKind =
  | "conflict"
  | "forbidden"
  | "network"
  | "not_found"
  | "rate_limit"
  | "server"
  | "timeout"
  | "unauthorized"
  | "unknown"
  | "validation";

type ApiErrorOptions = APIError & {
  cause?: unknown;
  kind: ApiErrorKind;
  userMessage?: string;
};

class ApiBaseError extends Error {
  readonly code?: string;
  readonly details?: unknown;
  readonly fieldErrors?: Record<string, string[]>;
  readonly kind: ApiErrorKind;
  readonly requestId?: string;
  readonly status?: number;
  readonly userMessage: string;

  constructor({
    cause,
    code,
    details,
    fieldErrors,
    kind,
    message,
    requestId,
    status,
    userMessage,
  }: ApiErrorOptions) {
    super(message, { cause });
    this.name = "ApiBaseError";
    this.code = code;
    this.details = details;
    this.fieldErrors = fieldErrors;
    this.kind = kind;
    this.requestId = requestId;
    this.status = status;
    this.userMessage = userMessage ?? message;
  }
}

class ApiNetworkError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind" | "message"> & { message?: string } = {}) {
    super({
      kind: "network",
      message: options.message ?? "Network request failed.",
      userMessage: options.userMessage ?? "The server cannot be reached. Please try again.",
      ...options,
    });
    this.name = "ApiNetworkError";
  }
}

class ApiTimeoutError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind" | "message"> & { message?: string } = {}) {
    super({
      kind: "timeout",
      message: options.message ?? "Network request timed out.",
      userMessage: options.userMessage ?? "The request took too long. Please try again.",
      ...options,
    });
    this.name = "ApiTimeoutError";
  }
}

class ApiUnauthorizedError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({ kind: "unauthorized", userMessage: "Your session is no longer valid.", ...options });
    this.name = "ApiUnauthorizedError";
  }
}

class ApiForbiddenError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({
      kind: "forbidden",
      userMessage: "You do not have access to this content.",
      ...options,
    });
    this.name = "ApiForbiddenError";
  }
}

class ApiNotFoundError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({ kind: "not_found", userMessage: "The requested content was not found.", ...options });
    this.name = "ApiNotFoundError";
  }
}

class ApiConflictError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({
      kind: "conflict",
      userMessage: "The request conflicts with the current server state.",
      ...options,
    });
    this.name = "ApiConflictError";
  }
}

class ApiValidationError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({ kind: "validation", userMessage: "Some fields need attention.", ...options });
    this.name = "ApiValidationError";
  }
}

class ApiRateLimitError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({
      kind: "rate_limit",
      userMessage: "Too many requests. Please wait and try again.",
      ...options,
    });
    this.name = "ApiRateLimitError";
  }
}

class ApiServerError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind">) {
    super({
      kind: "server",
      userMessage: "The server could not complete the request.",
      ...options,
    });
    this.name = "ApiServerError";
  }
}

class ApiUnknownError extends ApiBaseError {
  constructor(options: Omit<ApiErrorOptions, "kind" | "message"> & { message?: string } = {}) {
    super({
      kind: "unknown",
      message: options.message ?? "Unexpected API error.",
      userMessage: options.userMessage ?? "An unexpected error occurred.",
      ...options,
    });
    this.name = "ApiUnknownError";
  }
}

function isApiError(error: unknown): error is ApiBaseError {
  return error instanceof ApiBaseError;
}

function normalizeUnknownError(error: unknown): ApiBaseError {
  if (isApiError(error)) {
    return error;
  }

  if (error instanceof DOMException && error.name === "AbortError") {
    return new ApiTimeoutError({ cause: error });
  }

  if (error instanceof TypeError) {
    return new ApiNetworkError({ cause: error });
  }

  if (error instanceof Error) {
    return new ApiUnknownError({ cause: error, message: error.message });
  }

  return new ApiUnknownError({ details: error });
}

function createHttpError(status: number, apiError: APIError): ApiBaseError {
  const options = {
    ...apiError,
    message: apiError.message,
    status,
  };

  if (status === 401) {
    return new ApiUnauthorizedError(options);
  }

  if (status === 403) {
    return new ApiForbiddenError(options);
  }

  if (status === 404) {
    return new ApiNotFoundError(options);
  }

  if (status === 409) {
    return new ApiConflictError(options);
  }

  if (status === 400 || status === 422) {
    return new ApiValidationError(options);
  }

  if (status === 429) {
    return new ApiRateLimitError(options);
  }

  if (status >= 500) {
    return new ApiServerError(options);
  }

  return new ApiUnknownError(options);
}

export {
  ApiBaseError,
  ApiConflictError,
  ApiForbiddenError,
  ApiNetworkError,
  ApiNotFoundError,
  ApiRateLimitError,
  ApiServerError,
  ApiTimeoutError,
  ApiUnauthorizedError,
  ApiUnknownError,
  ApiValidationError,
  createHttpError,
  isApiError,
  normalizeUnknownError,
};
export type { ApiErrorKind, ApiErrorOptions };
