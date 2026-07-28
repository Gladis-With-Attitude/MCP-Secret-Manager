import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";
const webServerPort = new URL(baseURL).port || "3000";

export default defineConfig({
  expect: {
    timeout: 15_000,
  },
  forbidOnly: Boolean(process.env.CI),
  fullyParallel: false,
  outputDir: "test-results/playwright",
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  retries: process.env.CI ? 1 : 0,
  testDir: ".",
  testMatch: ["tests/e2e/**/*.spec.ts", "e2e/**/*.spec.ts"],
  timeout: 90_000,
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run start",
    env: {
      PORT: webServerPort,
    },
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    url: baseURL,
  },
  workers: 1,
});
