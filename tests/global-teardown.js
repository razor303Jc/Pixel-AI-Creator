/**
 * Global Teardown for Playwright Tests
 * Cleanup after all tests complete
 */

async function globalTeardown(config) {
  console.log("🧹 Starting global teardown...");

  try {
    // Clean up any test data
    console.log("Cleaning up test environment...");

    // Remove any temporary files or data
    // Reset any global state if needed

    // Clear environment variables
    delete process.env.SETUP_COMPLETE;

    console.log("✅ Global teardown completed");
  } catch (error) {
    console.error("❌ Global teardown failed:", error.message);
    // Don't throw error in teardown to avoid masking test results
  }
}

module.exports = globalTeardown;
