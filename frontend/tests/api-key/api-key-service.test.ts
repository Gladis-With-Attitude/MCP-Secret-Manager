import { describe, expect, it, vi } from "vitest";

import {
  createApiKey,
  getApiKey,
  listApiKeys,
  revokeApiKey,
} from "@/features/api-key/api/api-key-service";

const httpMocks = vi.hoisted(() => ({
  get: vi.fn(async () => ({ id: "key_1" })),
  post: vi.fn(async () => ({ id: "key_1" })),
}));

vi.mock("@/lib/api", () => ({
  get: httpMocks.get,
  post: httpMocks.post,
}));

describe("api key service", () => {
  it("uses the API key REST endpoints", async () => {
    await listApiKeys({ page: 1, page_size: 20, search: "agent" });
    await getApiKey("key_1");
    await createApiKey({
      name: "agent",
      owner_id: "owner_1",
      owner_type: "user",
      permissions: ["secret.read"],
      scopes: ["global"],
    });
    await revokeApiKey("key_1");

    expect(httpMocks.get).toHaveBeenNthCalledWith(1, "/v1/api-keys", {
      params: { page: 1, page_size: 20, search: "agent" },
    });
    expect(httpMocks.get).toHaveBeenNthCalledWith(2, "/v1/api-keys/key_1");
    expect(httpMocks.post).toHaveBeenNthCalledWith(
      1,
      "/v1/api-keys",
      {
        name: "agent",
        owner_id: "owner_1",
        owner_type: "user",
        permissions: ["secret.read"],
        scopes: ["global"],
      },
      { retry: false },
    );
    expect(httpMocks.post).toHaveBeenNthCalledWith(2, "/v1/api-keys/key_1/revoke", undefined, {
      retry: false,
    });
  });
});
