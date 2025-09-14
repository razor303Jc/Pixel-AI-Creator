/**
 * Comprehensive Playwright Configuration for Pixel AI Creator
 * Full UI Testing Suite with Browser Support
 */

const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  // Test directory
  testDir: "./frontend",

  // Global test timeout
  timeout: 60000,

  // Expect timeout for assertions
  expect: {
    timeout: 10000,
  },

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 1,

  // Reporter configuration
  reporter: [
    ["html", { outputFolder: "./reports/html" }],
    ["json", { outputFile: "./reports/test-results.json" }],
    ["junit", { outputFile: "./reports/test-results.xml" }],
    ["list"],
  ],

  // Global setup and teardown
  globalSetup: require.resolve("./setup/global-setup.js"),
  globalTeardown: require.resolve("./setup/global-teardown.js"),

  use: {
    // Base URL for all tests
    baseURL: "http://localhost:3002",

    // Browser context options
    browserName: "chromium",
    headless: false, // Set to false to see browser during development
    viewport: { width: 1280, height: 720 },

    // Capture screenshot on failure
    screenshot: "only-on-failure",

    // Record video on failure
    video: "retain-on-failure",

    // Capture trace on failure
    trace: "retain-on-failure",

    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,

    // Accept downloads
    acceptDownloads: true,
  },

  // Browser projects for cross-browser testing
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
    // Mobile testing
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],

  // Web server configuration
  webServer: {
    command: 'echo "Frontend should be running on localhost:3002"',
    port: 3002,
    reuseExistingServer: !process.env.CI,
  },
});
