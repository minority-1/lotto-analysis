import { defineConfig, devices } from "@playwright/test";

const host = "127.0.0.1";
const appPort = 3100;
const apiPort = 18000;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://${host}:${appPort}`,
    channel: "chrome",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop-chrome", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chrome", use: { ...devices["Pixel 7"] } },
  ],
  webServer: [
    {
      command: `node e2e/fixtures/api-server.mjs --port ${apiPort}`,
      port: apiPort,
      reuseExistingServer: false,
    },
    {
      command: `pnpm dev --hostname ${host} --port ${appPort}`,
      port: appPort,
      reuseExistingServer: false,
      env: { LOTTO_API_BASE_URL: `http://${host}:${apiPort}/api` },
    },
  ],
});
