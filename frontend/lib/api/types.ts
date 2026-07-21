type HttpMethod = "DELETE" | "GET" | "HEAD" | "PATCH" | "POST" | "PUT";

type Cursor = string;

type Pagination = {
  limit?: number;
  offset?: number;
  page?: number;
  pageSize?: number;
};

type CursorPagination = {
  cursor?: Cursor | null;
  limit?: number;
};

type SortDirection = "asc" | "desc";

type Sort = {
  direction: SortDirection;
  field: string;
};

type FilterValue = boolean | null | number | string | string[] | undefined;

type Filter = Record<string, FilterValue>;

type QueryParams = Record<string, FilterValue | number[]>;

type SuccessResponse<TData> = {
  data: TData;
  success: true;
};

type PaginatedResponse<TData> = {
  data: TData[];
  pagination: {
    cursor?: Cursor | null;
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    limit?: number;
    nextCursor?: Cursor | null;
    offset?: number;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  success: true;
};

type APIError = {
  code?: string;
  details?: unknown;
  fieldErrors?: Record<string, string[]>;
  message: string;
  requestId?: string;
  status?: number;
};

type RequestCredentialsMode = "include" | "omit" | "same-origin";

type RequestOptions<TBody = unknown> = {
  body?: TBody;
  credentials?: RequestCredentialsMode;
  headers?: HeadersInit;
  method?: HttpMethod;
  params?: QueryParams;
  retry?: boolean | number;
  signal?: AbortSignal;
  timeoutMs?: number;
};

type EmptyResponse = undefined;

export type {
  APIError,
  Cursor,
  CursorPagination,
  EmptyResponse,
  Filter,
  FilterValue,
  HttpMethod,
  PaginatedResponse,
  Pagination,
  QueryParams,
  RequestCredentialsMode,
  RequestOptions,
  Sort,
  SortDirection,
  SuccessResponse,
};
