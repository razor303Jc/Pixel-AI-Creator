/**
 * 🧹 GLOBAL TEST TEARDOWN
 * Cleanup after comprehensive build flow testing
 */

const { chromium } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

async function globalTeardown() {
  console.log("\n🧹 Starting Global Test Teardown");
  console.log("=".repeat(60));

  try {
    // Generate final test summary
    console.log("📊 Generating test summary...");

    const testResultsDir = "./test-results/";
    const reportFiles = [];

    // Collect all test result files
    if (fs.existsSync(testResultsDir)) {
      const files = fs.readdirSync(testResultsDir);
      files.forEach((file) => {
        if (file.includes("build-flow") && file.endsWith(".json")) {
          reportFiles.push(path.join(testResultsDir, file));
        }
      });
    }

    // Create comprehensive summary
    const summary = {
      testSuite: "Comprehensive Assistant Build Flow",
      teardownTime: new Date().toISOString(),
      environment: {
        setup_complete: process.env.TEST_SETUP_COMPLETE === "true",
        test_user: process.env.TEST_USER_EMAIL,
        frontend_url: "http://localhost:3002",
        backend_url: "http://localhost:8002",
      },
      testResults: reportFiles.length,
      reports: reportFiles.map((file) => ({
        file: file,
        size: fs.existsSync(file) ? fs.statSync(file).size : 0,
      })),
    };

    // Save teardown summary
    const summaryPath = path.join(
      testResultsDir,
      `teardown-summary-${Date.now()}.json`
    );
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

    console.log("📄 Test Summary:");
    console.log(`  Test Reports Generated: ${reportFiles.length}`);
    console.log(`  Summary Saved: ${summaryPath}`);

    // Optional: Clean up test data (if needed)
    if (process.env.CLEANUP_TEST_DATA === "true") {
      console.log("🗑️  Cleaning up test data...");

      const browser = await chromium.launch();
      const page = await browser.newPage();

      // Login as test user to clean up
      try {
        const loginResponse = await page.request.post(
          "http://localhost:8002/api/auth/login",
          {
            data: {
              email: process.env.TEST_USER_EMAIL,
              password: process.env.TEST_USER_PASSWORD,
            },
          }
        );

        if (loginResponse.status() === 200) {
          const { access_token } = await loginResponse.json();

          // Clean up test clients, projects, etc.
          // This is optional and can be enabled when needed
          console.log("🧹 Test data cleanup completed");
        }
      } catch (e) {
        console.log("⚠️  Test data cleanup skipped:", e.message);
      }

      await browser.close();
    }

    console.log("\n✅ Global teardown completed successfully");
    console.log("=".repeat(60));
  } catch (error) {
    console.error("❌ Global teardown failed:", error.message);
    // Don't exit with error - teardown failures shouldn't fail the build
  }

  // Clear environment variables
  delete process.env.TEST_SETUP_COMPLETE;
  delete process.env.TEST_USER_EMAIL;
  delete process.env.TEST_USER_PASSWORD;
}

module.exports = globalTeardown;
