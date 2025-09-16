/**
 * 🔧 GLOBAL TEST SETUP
 * Prepares the test environment for comprehensive build flow testing
 */

const { chromium } = require("@playwright/test");

async function globalSetup() {
  console.log("\n🚀 Starting Global Test Setup for Build Flow Tests");
  console.log("=".repeat(60));

  // Test environment checks
  const checks = {
    frontend: false,
    backend: false,
    database: false,
    authentication: false,
  };

  try {
    // Launch a browser for setup tasks
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // 1. Check if frontend is accessible
    console.log("🌐 Checking frontend availability...");
    try {
      await page.goto("http://localhost:3002", {
        waitUntil: "networkidle",
        timeout: 10000,
      });
      checks.frontend = true;
      console.log("✅ Frontend is accessible");
    } catch (e) {
      console.log("❌ Frontend not accessible:", e.message);
      throw new Error("Frontend server not running on localhost:3002");
    }

    // 2. Check if backend API is accessible
    console.log("🔌 Checking backend API...");
    try {
      const response = await page.request.get(
        "http://localhost:8002/api/health"
      );
      if (response.status() === 200 || response.status() === 404) {
        checks.backend = true;
        console.log("✅ Backend API is accessible");
      }
    } catch (e) {
      console.log("❌ Backend API not accessible");
      throw new Error("Backend API not running on localhost:8002");
    }

    // 3. Verify test user exists or create one
    console.log("👤 Verifying test user...");
    try {
      const loginResponse = await page.request.post(
        "http://localhost:8002/api/auth/login",
        {
          data: {
            email: "testuser@buildstatus.com",
            password: "testpass123",
          },
        }
      );

      if (loginResponse.status() === 200) {
        checks.authentication = true;
        console.log("✅ Test user authentication working");
      } else if (loginResponse.status() === 401) {
        // Try to register the user
        console.log("🔄 Test user not found, creating...");
        const registerResponse = await page.request.post(
          "http://localhost:8002/api/auth/register",
          {
            data: {
              email: "testuser@buildstatus.com",
              password: "testpass123",
              first_name: "Test",
              last_name: "User",
            },
          }
        );

        if (registerResponse.status() === 201) {
          checks.authentication = true;
          console.log("✅ Test user created successfully");
        } else {
          throw new Error("Failed to create test user");
        }
      }
    } catch (e) {
      console.log("❌ Authentication setup failed:", e.message);
      throw new Error("Authentication system not working");
    }

    // 4. Database connectivity check (implicit through API calls)
    if (checks.authentication) {
      checks.database = true;
      console.log("✅ Database connectivity confirmed");
    }

    await browser.close();

    // Summary of checks
    console.log("\n📊 Environment Check Summary:");
    console.log(`Frontend: ${checks.frontend ? "✅" : "❌"}`);
    console.log(`Backend: ${checks.backend ? "✅" : "❌"}`);
    console.log(`Database: ${checks.database ? "✅" : "❌"}`);
    console.log(`Authentication: ${checks.authentication ? "✅" : "❌"}`);

    const allChecksPass = Object.values(checks).every(
      (check) => check === true
    );

    if (!allChecksPass) {
      throw new Error("Some environment checks failed");
    }

    console.log("\n🎉 All environment checks passed!");
    console.log("✅ Test environment is ready for build flow testing");
    console.log("=".repeat(60));

    // Store environment data for tests
    process.env.TEST_SETUP_COMPLETE = "true";
    process.env.TEST_USER_EMAIL = "testuser@buildstatus.com";
    process.env.TEST_USER_PASSWORD = "testpass123";
  } catch (error) {
    console.error("❌ Global setup failed:", error.message);
    console.log("\n🔧 Setup Requirements:");
    console.log("  1. Frontend server running on http://localhost:3002");
    console.log("  2. Backend API running on http://localhost:8002");
    console.log("  3. Database accessible through backend");
    console.log("  4. Authentication system working");
    process.exit(1);
  }
}

module.exports = globalSetup;
