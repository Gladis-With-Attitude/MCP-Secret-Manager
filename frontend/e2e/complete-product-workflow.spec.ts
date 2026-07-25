import { type APIRequestContext, type APIResponse, expect, test } from "@playwright/test";

const apiBaseURL = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
const bootstrapApiKey = process.env.E2E_BOOTSTRAP_API_KEY ?? "";

test.skip(!bootstrapApiKey, "E2E_BOOTSTRAP_API_KEY is required for real backend E2E tests.");

type CurrentSessionResponse = {
  user: {
    id: string;
  };
};

async function expectOkJson<T>(response: APIResponse, status: number): Promise<T> {
  expect(response.status()).toBe(status);
  return (await response.json()) as T;
}

async function post(
  request: APIRequestContext,
  path: string,
  data?: Record<string, unknown>,
): Promise<APIResponse> {
  return request.post(`${apiBaseURL}${path}`, { data });
}

async function get(
  request: APIRequestContext,
  path: string,
  params?: Record<string, number | string>,
): Promise<APIResponse> {
  return request.get(`${apiBaseURL}${path}`, { params });
}

async function remove(request: APIRequestContext, path: string): Promise<APIResponse> {
  return request.delete(`${apiBaseURL}${path}`);
}

test.describe("C1 complete product workflow", () => {
  test("covers login, core resources, secret lifecycle, API keys, audit, RBAC, and logout", async ({
    request,
  }) => {
    const suffix = (process.env.E2E_RUN_ID ?? Date.now().toString(36)).toLowerCase();
    const secretValueV1 = "not-a-real-secret-playwright-v1";
    const secretValueV2 = "not-a-real-secret-playwright-v2";

    const health = await get(request, "/v1/health");
    expect(health.ok()).toBe(true);

    const login = await post(request, "/v1/auth/session", { api_key: bootstrapApiKey });
    const session = await expectOkJson<CurrentSessionResponse>(login, 201);
    const ownerId = session.user.id;

    const currentSession = await get(request, "/v1/auth/session");
    expect((await expectOkJson<CurrentSessionResponse>(currentSession, 200)).user.id).toBe(ownerId);

    const vault = await post(request, "/v1/vaults", {
      description: "C1 Playwright vault",
      name: `C1 Vault ${suffix}`,
    });
    const vaultId = (await expectOkJson<{ id: string }>(vault, 201)).id;

    const project = await post(request, `/v1/vaults/${vaultId}/projects`, {
      description: "C1 Playwright project",
      name: `C1 Project ${suffix}`,
    });
    const projectId = (await expectOkJson<{ id: string }>(project, 201)).id;

    const secret = await post(request, `/v1/projects/${projectId}/secrets`, {
      description: "C1 Playwright metadata",
      key: `C1_SECRET_${suffix.replace(/[^a-z0-9]/g, "_").toUpperCase()}`,
      metadata: { owner: "platform" },
      tags: ["c1", "playwright"],
      type: "generic",
    });
    const secretText = await secret.text();
    expect(secret.status()).toBe(201);
    expect(secretText).not.toContain(secretValueV1);
    expect(secretText).not.toContain(secretValueV2);
    const secretId = (JSON.parse(secretText) as { id: string }).id;

    const initialVersion = await post(request, `/v1/secrets/${secretId}/versions`, {
      value: secretValueV1,
    });
    expect(initialVersion.status()).toBe(201);
    expect(await initialVersion.text()).not.toContain(secretValueV1);

    const rotatedVersion = await post(request, `/v1/secrets/${secretId}/versions`, {
      value: secretValueV2,
    });
    const rotatedPayload = await expectOkJson<{ active: boolean; version: number }>(
      rotatedVersion,
      201,
    );
    expect(rotatedPayload).toMatchObject({ active: true, version: 2 });

    const versions = await expectOkJson<Array<{ active: boolean; version: number }>>(
      await get(request, `/v1/secrets/${secretId}/versions`),
      200,
    );
    expect(versions.map((version) => version.version)).toEqual([1, 2]);
    expect(versions.map((version) => version.active)).toEqual([false, true]);

    const latestValue = await expectOkJson<{ value: string }>(
      await get(request, `/v1/secrets/${secretId}/versions/latest`),
      200,
    );
    expect(latestValue.value).toBe(secretValueV2);

    const createdApiKey = await expectOkJson<{ api_key: string; id: string; key_prefix: string }>(
      await post(request, "/v1/api-keys", {
        description: "C1 Playwright API key",
        name: `c1-api-key-${suffix}`,
        owner_id: ownerId,
        owner_type: "user",
        permissions: ["secret.read"],
        scopes: ["global"],
      }),
      201,
    );
    expect(createdApiKey.api_key).toContain(createdApiKey.key_prefix);

    const listedApiKeys = await get(request, "/v1/api-keys", { q: `c1-api-key-${suffix}` });
    const listedApiKeyText = await listedApiKeys.text();
    expect(listedApiKeys.status()).toBe(200);
    expect(listedApiKeyText).toContain(createdApiKey.id);
    expect(listedApiKeyText).not.toContain(createdApiKey.api_key);

    const revokedApiKey = await expectOkJson<{ status: string }>(
      await post(request, `/v1/api-keys/${createdApiKey.id}/revoke`),
      200,
    );
    expect(revokedApiKey.status).toBe("revoked");

    const permissions = await expectOkJson<{ data: Array<{ id: string; name: string }> }>(
      await get(request, "/v1/permissions"),
      200,
    );
    const secretReadPermission = permissions.data.find(
      (permission) => permission.name === "secret.read",
    );
    expect(secretReadPermission).toBeDefined();

    const role = await expectOkJson<{ id: string }>(
      await post(request, "/v1/roles", {
        description: "C1 Playwright role",
        name: `c1-secret-reader-${suffix}`,
        permission_ids: [secretReadPermission?.id],
      }),
      201,
    );

    const assignedRole = await expectOkJson<{ role_id: string }>(
      await post(request, `/v1/actors/${ownerId}/roles/${role.id}`),
      201,
    );
    expect(assignedRole.role_id).toBe(role.id);

    const roleAssignments = await get(request, `/v1/actors/${ownerId}/roles`);
    expect(await roleAssignments.text()).toContain(role.id);

    const revokedRole = await expectOkJson<{ status: string }>(
      await remove(request, `/v1/actors/${ownerId}/roles/${role.id}`),
      200,
    );
    expect(revokedRole.status).toBe("revoked");

    const audit = await get(request, "/v1/audit/events", { limit: 200 });
    const auditText = await audit.text();
    expect(audit.status()).toBe(200);
    for (const action of [
      "session.create",
      "vault.create",
      "project.create",
      "secret.create",
      "secret.rotate",
      "secret.decrypt",
      "apikey.create",
      "apikey.revoke",
      "role.create",
      "role.assign",
      "role.revoke",
    ]) {
      expect(auditText).toContain(action);
    }
    expect(auditText).not.toContain(secretValueV1);
    expect(auditText).not.toContain(secretValueV2);

    expect((await remove(request, "/v1/auth/session")).status()).toBe(204);
    expect((await get(request, "/v1/auth/session")).status()).toBe(401);
  });
});
