/**
 * Global Setup for Playwright Tests
 * Ensures clean state before all tests
 */

const { chromium } = require("@playwright/test");

async function globalSetup(config) {
  console.log("🚀 Starting global test setup...");

  // Create a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for application to be ready
    console.log("⏳ Waiting for application to be ready...");
    await page.goto("http://localhost:3002", { waitUntil: "networkidle" });

    // Check if the application loads successfully
    await page.waitForSelector("body", { timeout: 30000 });
    console.log("✅ Application is ready");

    // Clear any existing local storage/session storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    console.log("🧹 Cleared browser storage");
  } catch (error) {
    console.error("❌ Global setup failed:", error);
    throw error;
  } finally {
    await browser.close();
  }

  console.log("✅ Global setup completed successfully");
}

module.exports = globalSetup;
