import { afterEach, describe, expect, it, vi } from "vitest";

describe("vault service", () => {
  afterEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("calls the real Vault REST endpoints", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.test");
    const fetchMock = vi.fn(async (request: Request) => {
      if (request.method === "GET" && request.url.includes("/v1/vaults?")) {
        expect(request.url).toBe(
          "https://api.example.test/v1/vaults?page=1&page_size=20&search=prod",
        );
        return Response.json({
          data: [{ id: "vault_1", name: "Production" }],
          pagination: { page: 1, pageSize: 20, total: 1 },
          permissions: { archive: true, create: true, read: true, update: true },
          success: true,
        });
      }

      if (request.method === "GET") {
        expect(request.url).toBe("https://api.example.test/v1/vaults/vault_1");
        return Response.json({ id: "vault_1", name: "Production" });
      }

      if (request.method === "POST" && request.url.endsWith("/archive")) {
        expect(request.url).toBe("https://api.example.test/v1/vaults/vault_1/archive");
        return Response.json({ archived: true, id: "vault_1", name: "Production" });
      }

      if (request.method === "POST") {
        const body = await request.clone().json();

        expect(request.url).toBe("https://api.example.test/v1/vaults");
        expect(body).toEqual({ description: "Primary", name: "Production" });
        return Response.json({ id: "vault_1", name: "Production" }, { status: 201 });
      }

      const body = await request.clone().json();

      expect(request.method).toBe("PATCH");
      expect(request.url).toBe("https://api.example.test/v1/vaults/vault_1");
      expect(body).toEqual({ description: "Updated", name: "Platform" });
      return Response.json({ id: "vault_1", name: "Platform" });
    });
    vi.stubGlobal("fetch", fetchMock);

    const { archiveVault, createVault, getVault, listVaults, updateVault } =
      await import("@/features/vault/api/vault-service");

    await expect(listVaults({ page: 1, page_size: 20, search: "prod" })).resolves.toMatchObject({
      data: [{ id: "vault_1", name: "Production" }],
    });
    await expect(getVault("vault_1")).resolves.toMatchObject({ id: "vault_1" });
    await expect(
      createVault({ description: "Primary", name: "Production" }),
    ).resolves.toMatchObject({ id: "vault_1" });
    await expect(
      updateVault("vault_1", { description: "Updated", name: "Platform" }),
    ).resolves.toMatchObject({ name: "Platform" });
    await expect(archiveVault("vault_1")).resolves.toMatchObject({ archived: true });
  });
});
