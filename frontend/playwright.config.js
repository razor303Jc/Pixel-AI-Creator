// Playwright configuration for Pixel AI Creator UI tests
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "../tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html"], ["json", { outputFile: "test-results/results.json" }]],
  use: {
    baseURL: "http://localhost:3002",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"], hasTouch: true },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"], hasTouch: true },
    },
  ],

  webServer: {
    command: "npm run dev",
    port: 3002,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
