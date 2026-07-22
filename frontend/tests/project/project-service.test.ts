import { afterEach, describe, expect, it, vi } from "vitest";

describe("project service", () => {
  afterEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("calls the real Project REST endpoints", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.test");
    const fetchMock = vi.fn(async (request: Request) => {
      if (request.method === "GET" && request.url.includes("/v1/vaults/vault_1/projects?")) {
        expect(request.url).toBe(
          "https://api.example.test/v1/vaults/vault_1/projects?page=1&page_size=20&search=api",
        );
        return Response.json({
          data: [{ id: "project_1", name: "API", vault_id: "vault_1" }],
          pagination: { page: 1, pageSize: 20, total: 1 },
          permissions: { archive: true, create: true, read: true, update: true },
          success: true,
        });
      }

      if (request.method === "GET") {
        expect(request.url).toBe("https://api.example.test/v1/projects/project_1");
        return Response.json({ id: "project_1", name: "API", vault_id: "vault_1" });
      }

      if (request.method === "POST" && request.url.endsWith("/archive")) {
        expect(request.url).toBe("https://api.example.test/v1/projects/project_1/archive");
        return Response.json({
          archived: true,
          id: "project_1",
          name: "API",
          vault_id: "vault_1",
        });
      }

      if (request.method === "POST") {
        const body = await request.clone().json();

        expect(request.url).toBe("https://api.example.test/v1/vaults/vault_1/projects");
        expect(body).toEqual({ description: "Application", name: "API" });
        return Response.json(
          { id: "project_1", name: "API", vault_id: "vault_1" },
          { status: 201 },
        );
      }

      const body = await request.clone().json();

      expect(request.method).toBe("PATCH");
      expect(request.url).toBe("https://api.example.test/v1/projects/project_1");
      expect(body).toEqual({ description: "Updated", name: "API Core" });
      return Response.json({ id: "project_1", name: "API Core", vault_id: "vault_1" });
    });
    vi.stubGlobal("fetch", fetchMock);

    const { archiveProject, createProject, getProject, listProjects, updateProject } =
      await import("@/features/project/api/project-service");

    await expect(
      listProjects("vault_1", { page: 1, page_size: 20, search: "api" }),
    ).resolves.toMatchObject({
      data: [{ id: "project_1", name: "API", vault_id: "vault_1" }],
    });
    await expect(getProject("project_1")).resolves.toMatchObject({ id: "project_1" });
    await expect(
      createProject("vault_1", { description: "Application", name: "API" }),
    ).resolves.toMatchObject({ id: "project_1" });
    await expect(
      updateProject("project_1", { description: "Updated", name: "API Core" }),
    ).resolves.toMatchObject({ name: "API Core" });
    await expect(archiveProject("project_1")).resolves.toMatchObject({ archived: true });
  });
});
