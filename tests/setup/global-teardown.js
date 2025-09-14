/**
 * Global Teardown for Playwright Tests
 * Cleanup after all tests complete
 */

async function globalTeardown(config) {
  console.log("🧹 Starting global test teardown...");

  // Add any cleanup logic here
  // For example: clear test data, reset database state, etc.

  console.log("✅ Global teardown completed");
}

module.exports = globalTeardown;
