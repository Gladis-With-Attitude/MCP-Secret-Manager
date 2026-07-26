import type { Page } from "@playwright/test";
import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const adminApiKey = process.env.PLAYWRIGHT_ADMIN_API_KEY;

type CurrentSessionResponse = {
  user: {
    id: string;
    name: string;
  };
};

function pathIdFromUrl(page: Page, pattern: RegExp, label: string): string {
  const match = page.url().match(pattern);
  expect(match, `${label} should be present in ${page.url()}`).not.toBeNull();

  return match?.[1] ?? "";
}

async function signIn(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "MCP Secret Manager" })).toBeVisible();
  await page.getByLabel("API key").fill(adminApiKey ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
}

async function getCurrentUserId(page: Page): Promise<string> {
  const response = await page.context().request.get(`${apiBaseUrl}/v1/auth/session`);
  expect(response.ok()).toBeTruthy();
  const session = (await response.json()) as CurrentSessionResponse;

  return session.user.id;
}

test.describe("production readiness workflow", () => {
  test.skip(!adminApiKey, "Set PLAYWRIGHT_ADMIN_API_KEY to a bootstrapped administrator API key.");

  test("validates the core secret-manager workflow end to end", async ({ page }) => {
    const suffix = Date.now().toString(36);
    const vaultName = `E2E Vault ${suffix}`;
    const projectName = `E2E Project ${suffix}`;
    const secretName = `E2E_SECRET_${suffix.toUpperCase()}`;
    const secretValue = `not-a-secret-e2e-value-${suffix}`;
    const apiKeyName = `e2e-key-${suffix}`;
    const roleName = `e2e-role-${suffix}`;

    await signIn(page);
    const userId = await getCurrentUserId(page);

    await page.goto("/vaults/new");
    await page.getByLabel("Name").fill(vaultName);
    await page.getByLabel("Description").fill("Non-sensitive Playwright workflow vault.");
    await page.getByRole("button", { name: "Create vault" }).click();
    await expect(page.getByRole("heading", { name: vaultName })).toBeVisible();
    const vaultId = pathIdFromUrl(page, /\/vaults\/([^/?]+)$/, "vault id");

    await page.goto(`/vaults/${vaultId}/projects/new`);
    await page.getByLabel("Name").fill(projectName);
    await page.getByLabel("Description").fill("Non-sensitive Playwright workflow project.");
    await page.getByRole("button", { name: "Create project" }).click();
    await expect(page.getByRole("heading", { name: projectName })).toBeVisible();
    const projectId = pathIdFromUrl(page, /\/vaults\/[^/]+\/projects\/([^/?]+)$/, "project id");

    await page.goto(`/vaults/${vaultId}/projects/${projectId}/secrets/new`);
    await page.getByLabel("Name").fill(secretName);
    await page.getByLabel("Description").fill("Playwright metadata only.");
    await page.getByLabel("Tags").fill("e2e, workflow");
    await page.getByLabel("Metadata").fill('{"source":"playwright"}');
    await page.getByRole("button", { name: "Create secret" }).click();
    await expect(page.getByRole("heading", { name: secretName })).toBeVisible();
    const secretId = pathIdFromUrl(
      page,
      /\/vaults\/[^/]+\/projects\/[^/]+\/secrets\/([^/?]+)$/,
      "secret id",
    );

    await page.goto(`/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}/versions/rotate`);
    await page.getByLabel("New value").fill(secretValue);
    await page.getByLabel("Rotation note").fill("Playwright rotation check.");
    await page.getByLabel("Metadata").fill('{"source":"playwright-rotation"}');
    await page.getByRole("button", { name: "Create version" }).click();
    await expect(page.getByRole("heading", { name: "Version 1" })).toBeVisible();

    await page.goto(`/vaults/${vaultId}/projects/${projectId}/secrets/${secretId}`);
    await page.getByRole("button", { name: "Reveal value" }).click();
    await expect(page.getByText(secretValue)).toBeVisible();
    await page.getByRole("button", { name: "Hide" }).click();
    await expect(page.getByText(secretValue)).toBeHidden();

    await page.goto("/api-keys/new");
    await page.getByLabel("Name").fill(apiKeyName);
    await page.getByLabel("Description").fill("Playwright-created key to revoke.");
    await page.getByRole("combobox", { name: "Owner type" }).click();
    await page.getByRole("option", { name: "User" }).click();
    await page.getByLabel("Owner ID").fill(userId);
    await page.getByLabel("Permissions").fill("secret.read");
    await page.getByLabel("Scopes").fill("global");
    await page.getByRole("button", { exact: true, name: "Create API key" }).click();
    await expect(page.getByRole("dialog", { name: "API key created" })).toBeVisible();
    await expect(page.locator("code").filter({ hasText: /^mcp_sm_/ })).toBeVisible();
    await page.getByRole("button", { name: "I have saved it" }).click();
    await expect(page).toHaveURL(/\/api-keys$/);

    const apiKeyRow = page.getByRole("row", { name: new RegExp(apiKeyName) });
    await expect(apiKeyRow).toBeVisible();
    await apiKeyRow.getByRole("button", { name: "Revoke" }).click();
    await page
      .getByRole("dialog", { name: "Revoke API key" })
      .getByRole("button", {
        name: "Revoke API key",
      })
      .click();
    await expect(apiKeyRow.getByText("revoked")).toBeVisible();

    await page.goto("/rbac/roles/new");
    await page.getByLabel("Role name").fill(roleName);
    await page.getByLabel("Description").fill("Playwright custom role.");
    await page.getByRole("checkbox", { name: "Select role.read" }).click();
    await page.getByRole("button", { name: "Create role" }).click();
    await expect(page.getByRole("heading", { name: roleName })).toBeVisible();

    await page.goto("/audit");
    await page.getByLabel("Action").fill("secret.decrypt");
    await page.getByRole("button", { name: "Apply filters" }).click();
    await expect(page.getByRole("table", { name: "Audit logs" })).toContainText("secret.decrypt");
    await expect(page.getByRole("table", { name: "Audit logs" })).toContainText("Success");

    await page.getByRole("button", { name: /Account/ }).click();
    await expect(page.getByText("Authentication required")).toBeVisible();
  });
});
