import { defineConfig, devices } from "@playwright/test";

/**
 * Human-Like Workflow Testing Configuration
 * Single session testing to simulate realistic user behavior
 * Single worker configuration to avoid system overload
 */
export default defineConfig({
  testDir: "./tests",
  testMatch: ["**/test_human_workflow.spec.js"],

  /* Single worker to avoid system overload */
  workers: 1,

  /* No parallel execution */
  fullyParallel: false,

  /* Retry once on failure */
  retries: 1,

  /* Reporter configuration */
  reporter: [
    ["list"],
    ["html", { outputFolder: "test-results/human-workflow-report" }],
  ],

  /* Test configuration */
  use: {
    /* Base URL for Docker frontend */
    baseURL: "http://localhost:3002",

    /* Screenshot and video settings */
    screenshot: "only-on-failure",
    video: "retain-on-failure",

    /* Timeouts */
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },

  /* Single browser project */
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  /* Test timeout */
  timeout: 60 * 1000,
  expect: {
    timeout: 10000,
  },

  /* Output directory */
  outputDir: "test-results/human-workflow-artifacts",
});
