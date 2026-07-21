type BuildHeadersOptions = {
  body?: unknown;
  headers?: HeadersInit;
};

function isBodyWithOwnContentType(body: unknown): boolean {
  return body instanceof Blob || body instanceof FormData || body instanceof URLSearchParams;
}

function buildHeaders({ body, headers }: BuildHeadersOptions = {}): Headers {
  const nextHeaders = new Headers(headers);

  if (!nextHeaders.has("Accept")) {
    nextHeaders.set("Accept", "application/json");
  }

  if (body !== undefined && !isBodyWithOwnContentType(body) && !nextHeaders.has("Content-Type")) {
    nextHeaders.set("Content-Type", "application/json");
  }

  return nextHeaders;
}

export { buildHeaders };
export type { BuildHeadersOptions };
