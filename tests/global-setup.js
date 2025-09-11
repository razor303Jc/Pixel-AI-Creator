/**
 * Global Setup for Playwright Tests
 * Ensures services are running before tests begin
 */

const { chromium } = require("@playwright/test");

async function globalSetup(config) {
  console.log("🚀 Starting global setup...");

  // Start a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Check if frontend is accessible
    console.log("Checking frontend availability...");
    await page.goto("http://localhost:3002", {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    });
    console.log("✅ Frontend is accessible");

    // Check if API is accessible
    console.log("Checking API availability...");
    const apiResponse = await page.request.get("http://localhost:8002/health");
    if (apiResponse.ok()) {
      console.log("✅ API is accessible");
    } else {
      console.log("⚠️  API health check failed, but continuing with tests");
    }

    // Set up any global test data or authentication if needed
    console.log("Setting up test environment...");

    // Store any global state
    process.env.SETUP_COMPLETE = "true";
  } catch (error) {
    console.error("❌ Global setup failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }

  console.log("✅ Global setup completed");
}

module.exports = globalSetup;
