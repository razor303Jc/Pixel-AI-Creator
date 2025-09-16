/**
 * 🎭 COMPREHENSIVE BUILD FLOW TEST CONFIGURATION
 * Playwright configuration for testing the complete assistant creation and build process
 */

const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",

  // Test files for comprehensive build flow
  testMatch: [
    "complete-build-flow-single.spec.js",
    "comprehensive-assistant-build-flow.spec.js",
  ],

  // Run tests sequentially for build flow integrity
  fullyParallel: false,
  workers: 1,

  // Longer timeout for build processes
  timeout: 120000, // 2 minutes per test
  expect: {
    timeout: 30000, // 30 seconds for assertions
  },

  // Retry configuration
  retries: process.env.CI ? 2 : 1,

  // Comprehensive reporting
  reporter: [
    [
      "html",
      {
        outputFolder: "test-reports/build-flow-tests",
        open: "never",
      },
    ],
    [
      "json",
      {
        outputFile: "test-results/build-flow-results.json",
      },
    ],
    [
      "junit",
      {
        outputFile: "test-results/build-flow-junit.xml",
      },
    ],
    ["list", { printSteps: true }],
  ],

  // Global test configuration
  use: {
    // Application under test
    baseURL: "http://localhost:3002",

    // Browser configuration
    headless: process.env.CI ? true : false,
    viewport: { width: 1920, height: 1080 },

    // Debugging and tracing
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",

    // Timeouts
    actionTimeout: 15000,
    navigationTimeout: 30000,

    // Additional context options
    ignoreHTTPSErrors: true,

    // Test data directory
    testIdAttribute: "data-testid",
  },

  // Test projects for different scenarios
  projects: [
    {
      name: "Desktop Chrome - Build Flow",
      use: {
        ...devices["Desktop Chrome"],
        channel: "chrome",
      },
    },

    // Optional: Firefox testing
    // {
    //   name: "Desktop Firefox - Build Flow",
    //   use: { ...devices["Desktop Firefox"] },
    // },

    // Optional: Mobile testing for responsive design
    // {
    //   name: "Mobile - Build Flow",
    //   use: { ...devices["iPhone 13"] },
    // },
  ],

  // Global setup and teardown
  globalSetup: require.resolve("./tests/setup/global-setup.js"),
  globalTeardown: require.resolve("./tests/setup/global-teardown.js"),

  // Web server configuration (if needed)
  webServer: {
    command:
      "echo 'Servers should already be running on localhost:3002 and localhost:8002'",
    url: "http://localhost:3002",
    reuseExistingServer: true,
    timeout: 5000,
  },

  // Output directories
  outputDir: "test-results/",

  // Metadata
  metadata: {
    testSuite: "Pixel AI Creator - Build Flow Tests",
    version: "1.0.0",
    date: new Date().toISOString(),
    environment: process.env.NODE_ENV || "development",
  },
});
