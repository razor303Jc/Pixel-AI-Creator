/**
 * PIXEL AI CREATOR - ENHANCED VALIDATION TEST SUITE
 * Playwright Configuration for Registration Validation Tests
 *
 * 🎭 Test Configuration for:
 * - Registration validation tests
 * - Toast notification tests
 * - Cross-browser testing
 * - Mobile responsiveness
 * - Accessibility testing
 */

const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",

  // Test files to include
  testMatch: [
    "test_registration_validation.spec.js",
    "test_toast_notifications.spec.js",
  ],

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [
    ["html", { outputFolder: "test-reports/validation-tests" }],
    ["json", { outputFile: "test-results/validation-results.json" }],
    ["list"],
  ],

  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: "http://localhost:3002",

    // Collect trace when retrying the failed test
    trace: "on-first-retry",

    // Take screenshot on failure
    screenshot: "only-on-failure",

    // Record video on failure
    video: "retain-on-failure",

    // Global test timeout
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Configure projects for major browsers
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

    // Test against mobile viewports
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"], hasTouch: true },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"], hasTouch: true },
    },

    // Test against tablet viewports
    {
      name: "iPad",
      use: { ...devices["iPad Pro"], hasTouch: true },
    },
  ],

  // Run your local dev server before starting the tests
  webServer: [
    {
      command: "cd frontend && npm start",
      port: 3002,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: "cd api && python main.py",
      port: 8002,
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
  ],

  // Global setup and teardown
  globalSetup: require.resolve("./tests/global-setup.js"),
  globalTeardown: require.resolve("./tests/global-teardown.js"),

  // Test timeout
  timeout: 60000,
  expect: {
    timeout: 10000,
  },

  // Output directory for test artifacts
  outputDir: "test-results/artifacts",
});
