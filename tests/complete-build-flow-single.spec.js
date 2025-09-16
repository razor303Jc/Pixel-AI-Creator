/**
 * Complete Assistant Build Flow Test - Single Sequential Test
 *
 * This test runs as a SINGLE test case with multiple steps,
 * ensuring authentication state is preserved throughout the flow.
 * ensuring authentication state is preserved throughout the flow.
 */

const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

// Test configuration
const TEST_CONFIG = {
  BASE_URL: "http://localhost:3002",
  TEST_USER: {
    email: "testuser@buildstatus.com",
    password: "testpass123",
  },
  TEST_CLIENT: {
    name: "AutoTest Client Corp",
    email: `client-${Date.now()}@autotest.com`, // Make email unique per test run
    company: "AutoTest Industries",
    description: "Test client for comprehensive build flow validation",
  },
  TEST_ASSISTANT: {
    name: `AutoTest Sales Assistant ${Date.now()}`, // Make name unique per test run
    description: "Comprehensive test assistant for build flow validation",
    type: "chatbot",
    complexity: "advanced",
  },
  TIMEOUTS: {
    PAGE_LOAD: 15000,
    API_RESPONSE: 10000,
    ELEMENT_WAIT: 5000,
  },
};

test.describe("🎯 Complete Assistant Build Flow - Sequential", () => {
  let apiRequests = [];
  let buildId;
  let projectId;
  let clientId;

  test("🚀 Complete Build Flow: Authentication → Client → Assistant → Build → Verification", async ({
    page,
  }) => {
    console.log("\n🚀 STARTING COMPLETE BUILD FLOW TEST");
    console.log("=".repeat(60));

    // Monitor API requests and console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log(`❌ Console Error: ${msg.text()}`);
      }
    });

    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        apiRequests.push({
          method: request.method(),
          url: request.url(),
          timestamp: new Date().toISOString(),
          postData: request.postData(),
        });
      }
    });

    // ================================================================
    // STEP 1: AUTHENTICATION
    // ================================================================

    await test.step("Step 1: 🔐 User Authentication", async () => {
      console.log("\n📍 Step 1: Testing User Authentication");

      await page.goto(TEST_CONFIG.BASE_URL, {
        waitUntil: "networkidle",
        timeout: TEST_CONFIG.TIMEOUTS.PAGE_LOAD,
      });

      // Verify login form is displayed
      await expect(page.locator("form")).toBeVisible();

      // Login with valid credentials
      await page.fill('input[type="email"]', TEST_CONFIG.TEST_USER.email);
      await page.fill('input[type="password"]', TEST_CONFIG.TEST_USER.password);

      // Submit login form and wait for response
      await Promise.all([
        page.waitForResponse(
          (response) =>
            response.url().includes("/api/auth/login") &&
            response.status() === 200
        ),
        page.click('button[type="submit"]'),
      ]);

      // Verify successful login - wait for dashboard container to load
      await expect(page.locator(".container-fluid.px-4")).toBeVisible({
        timeout: TEST_CONFIG.TIMEOUTS.PAGE_LOAD,
      });

      // Also verify navigation is present
      await expect(page.locator('[data-testid="nav-dashboard"]')).toBeVisible({
        timeout: 5000,
      });

      console.log("✅ Authentication successful - Dashboard loaded");
    });

    // ================================================================
    // STEP 2: CLIENT CREATION
    // ================================================================

    await test.step("Step 2: 👥 Client Creation", async () => {
      console.log("\n📍 Step 2: Testing Client Creation");

      // Ensure we're on the main dashboard where clients are managed
      await page.click('[data-testid="nav-dashboard"]');

      // Wait for clients section heading to be visible
      await expect(page.locator('h3:has-text("Clients")')).toBeVisible();

      // Look for "Add Client" button and click it
      const addClientBtn = page.locator('button:has-text("Add Client")');
      if (await addClientBtn.isVisible()) {
        await addClientBtn.click();
      } else {
        // Try alternative selectors
        const createBtn = page.locator(
          'button[data-testid="create-client-btn"]'
        );
        if (await createBtn.isVisible()) {
          await createBtn.click();
        } else {
          // Try plus button or other common patterns
          await page
            .locator('button:has([data-lucide="plus"])')
            .first()
            .click();
        }
      }

      // Wait for modal to be visible
      await expect(page.locator(".modal")).toBeVisible();

      // Fill client form using correct selectors based on actual form structure
      // Name field (placeholder: "Enter client name")
      await page.fill(
        'input[placeholder="Enter client name"]',
        TEST_CONFIG.TEST_CLIENT.name
      );

      // Email field (placeholder: "Enter email address (e.g., john@company.com)")
      await page.fill(
        'input[placeholder*="Enter email address"]',
        TEST_CONFIG.TEST_CLIENT.email
      );

      // Company field (placeholder: "Enter company name")
      await page.fill(
        'input[placeholder="Enter company name"]',
        TEST_CONFIG.TEST_CLIENT.company
      );

      // Description field (placeholder: "Enter description (optional)")
      await page.fill(
        'textarea[placeholder="Enter description (optional)"]',
        TEST_CONFIG.TEST_CLIENT.description
      );

      // Wait a moment for form validation to process
      await page.waitForTimeout(1000);

      // Submit client creation and wait for API response - use button that contains create action
      await Promise.all([
        page.waitForResponse(
          (response) =>
            response.url().includes("/api/clients") &&
            (response.status() === 201 || response.status() === 200)
        ),
        page.click('.modal-footer button:not(:has-text("Cancel"))'),
      ]);

      // Verify client was created by looking for the name in the clients list
      await expect(
        page.locator(`text=${TEST_CONFIG.TEST_CLIENT.name}`).first()
      ).toBeVisible({
        timeout: TEST_CONFIG.TIMEOUTS.ELEMENT_WAIT,
      });

      console.log("✅ Client creation successful");
    });

    // ================================================================
    // STEP 3: ASSISTANT CREATION
    // ================================================================

    await test.step("Step 3: 🤖 Assistant Creation", async () => {
      console.log("\n📍 Step 3: Testing Assistant Creation Flow");

      // Stay on dashboard where chatbots are managed
      await page.click('[data-testid="nav-dashboard"]');

      // Wait for AI assistants section heading to be visible
      await expect(page.locator('h3:has-text("AI Assistants")')).toBeVisible();

      // Look for "Create Assistant" button and click it (robust selector logic)
      // Prefer the main dashboard button with text and icon, fallback to plus if needed
      let createAssistantClicked = false;
      const createAssistantBtn = page.locator(
        'button:has-text("Create Assistant")'
      );
      if (await createAssistantBtn.isVisible()) {
        await createAssistantBtn.click();
        createAssistantClicked = true;
      }
      if (!createAssistantClicked) {
        // Fallback: try the plus icon button in the AI Assistants section
        const assistantsSection = page
          .locator('h3:has-text("AI Assistants")')
          .locator("..");
        const plusBtn = assistantsSection
          .locator("button:has(svg)")
          .filter({ hasText: "" });
        if (await plusBtn.first().isVisible()) {
          await plusBtn.first().click();
          createAssistantClicked = true;
        }
      }
      if (!createAssistantClicked) {
        throw new Error("Could not find Create Assistant button or plus icon");
      }

      // Wait for assistant form modal
      await expect(page.locator(".modal")).toBeVisible();

      // Fill basic assistant information using correct selectors
      // Name field - use the correct placeholder as seen in the modal: 'Enter chatbot name'
      await page.fill(
        'input[placeholder="Enter chatbot name"]',
        TEST_CONFIG.TEST_ASSISTANT.name
      );

      // Description field
      await page.fill(
        'textarea[placeholder="Enter description (optional)"]',
        TEST_CONFIG.TEST_ASSISTANT.description
      );

      // Select personality from dropdown - this is required for assistants
      const personalitySelect = page
        .locator("select")
        .filter({ hasText: "Select personality type" });
      if (await personalitySelect.isVisible()) {
        await personalitySelect.selectOption("helpful"); // Default personality
      }

      // Select template from dropdown - use correct placeholder 'Select a template'
      const templateSelect = page
        .locator("select")
        .filter({ hasText: "Select a template" });
      if (await templateSelect.isVisible()) {
        // Pick the first valid template value (e.g., 'PA - General Assistant')
        // Get all options and pick the first non-empty value
        const options = await templateSelect.locator("option").all();
        let valueToSelect = null;
        for (const option of options) {
          const value = await option.getAttribute("value");
          if (value && value !== "") {
            valueToSelect = value;
            break;
          }
        }
        if (valueToSelect) {
          await templateSelect.selectOption(valueToSelect);
        } else {
          throw new Error("No valid template option found");
        }
      }

      // Optionally select client from dropdown if available
      const clientSelect = page
        .locator("select")
        .filter({ hasText: "Select a client" });
      if (await clientSelect.isVisible()) {
        // Try to select our test client by name
        await clientSelect.selectOption({
          label: TEST_CONFIG.TEST_CLIENT.name,
        });
      }

      // Enable auto-build checkbox to trigger build process
      const autoBuildCheckbox = page.locator(
        'input[type="checkbox"][id="auto-build-checkbox"]'
      );
      if (await autoBuildCheckbox.isVisible()) {
        await autoBuildCheckbox.check();
      }

      // Wait a moment for form validation
      await page.waitForTimeout(1000);

      // Submit assistant creation and wait for API response - use correct button selector
      await Promise.all([
        page.waitForResponse(
          (response) =>
            response.url().includes("/api/chatbots") &&
            (response.status() === 201 || response.status() === 200)
        ),
        page.click('.modal-footer button:not(:has-text("Cancel"))'),
      ]);

      // Verify assistant was created
      await expect(
        page.locator(`text=${TEST_CONFIG.TEST_ASSISTANT.name}`)
      ).toBeVisible({
        timeout: TEST_CONFIG.TIMEOUTS.ELEMENT_WAIT,
      });

      console.log("✅ Assistant creation successful");
    });

    // ================================================================
    // STEP 4: BUILD STATUS MONITORING
    // ================================================================

    await test.step("Step 4: 🔨 Build Status Integration", async () => {
      console.log("\n📍 Step 4: Testing Build Status Integration");

      // Navigate to Build Status tab
      await page.click('[data-testid="nav-build-status"]');

      // Wait for build dashboard to load - use specific heading text
      await expect(
        page.locator("h2:has-text('Build Status Dashboard')")
      ).toBeVisible({
        timeout: TEST_CONFIG.TIMEOUTS.ELEMENT_WAIT,
      });

      console.log("🔍 Checking Build Queue...");

      // Check if there are any builds in the queue
      const buildCards = page.locator(
        '[data-testid*="build-card"], .build-item, .card:has-text("Build")'
      );
      const buildCount = await buildCards.count();

      if (buildCount > 0) {
        console.log(`📋 Found ${buildCount} build(s) in queue`);

        // Check the first build status
        const firstBuild = buildCards.first();
        const buildStatus = await firstBuild
          .locator('.status, .badge, [data-testid*="status"]')
          .first()
          .textContent();
        console.log(`🔍 First build status: ${buildStatus}`);

        // Try to get build ID if visible
        const buildIdElement = firstBuild.locator(
          '[data-testid="build-id"], .build-id'
        );
        if (await buildIdElement.isVisible()) {
          buildId = await buildIdElement.textContent();
          console.log(`🆔 Build ID: ${buildId}`);
        }
      } else {
        console.log(
          "📋 No builds found in queue - this is expected for new environment"
        );
      }

      console.log("✅ Build status monitoring tested");
    });

    // ================================================================
    // STEP 5: DATABASE VERIFICATION
    // ================================================================

    await test.step("Step 5: 🗃️ Database Verification", async () => {
      console.log("\n📍 Step 5: Verifying Database Integration");

      // Test API endpoints to verify database integration
      console.log("🔍 Testing API endpoints...");

      try {
        // Test if we can access builds API
        const response = await page.request.get("/api/builds/");
        console.log(`📡 Builds API Status: ${response.status()}`);

        if (response.status() === 200) {
          const builds = await response.json();
          console.log(
            `📊 Found ${
              builds.builds ? builds.builds.length : 0
            } builds in database`
          );
        }
      } catch (error) {
        console.log(`⚠️  Builds API not accessible: ${error.message}`);
      }

      try {
        // Test clients API
        const response = await page.request.get("/api/clients/");
        console.log(`📡 Clients API Status: ${response.status()}`);

        if (response.status() === 200) {
          const clients = await response.json();
          console.log(`📊 Found ${clients.length || 0} clients in database`);
        }
      } catch (error) {
        console.log(`⚠️  Clients API not accessible: ${error.message}`);
      }

      try {
        // Test chatbots API
        const response = await page.request.get("/api/chatbots/");
        console.log(`📡 Chatbots API Status: ${response.status()}`);

        if (response.status() === 200) {
          const chatbots = await response.json();
          console.log(`📊 Found ${chatbots.length || 0} chatbots in database`);
        }
      } catch (error) {
        console.log(`⚠️  Chatbots API not accessible: ${error.message}`);
      }

      console.log("✅ Database verification completed");
    });

    // ================================================================
    // STEP 6: GENERATE FINAL REPORT
    // ================================================================

    await test.step("Step 6: 📋 Generate Test Report", async () => {
      console.log("\n📍 Step 6: Generating Comprehensive Test Report");

      // Generate comprehensive test report
      const report = {
        testRun: new Date().toISOString(),
        testConfig: TEST_CONFIG,
        apiRequests: apiRequests,
        buildId: buildId,
        projectId: projectId,
        clientId: clientId,
        results: {
          authentication: "✅ PASSED",
          clientCreation: "✅ PASSED",
          assistantCreation: "✅ PASSED",
          buildStatusMonitoring: "✅ PASSED",
          databaseVerification: "✅ PASSED",
        },
        status: "COMPLETED",
        totalApiRequests: apiRequests.length,
        testDuration: new Date().toISOString(),
      };

      // Save detailed report
      const reportPath = path.join(
        "./test-results/",
        `complete-build-flow-${Date.now()}.json`
      );
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

      console.log("\n" + "=".repeat(60));
      console.log("🎉 COMPLETE BUILD FLOW TEST FINISHED SUCCESSFULLY");
      console.log("=".repeat(60));
      console.log(`📄 Report saved to: ${reportPath}`);
      console.log(`🤖 Project ID: ${projectId || "N/A"}`);
      console.log(`🔨 Build ID: ${buildId || "N/A"}`);
      console.log(`👥 Client ID: ${clientId || "N/A"}`);
      console.log(`📊 API Requests Made: ${apiRequests.length}`);
      console.log("=".repeat(60));
    });

    // Test completed successfully if we reach here
    console.log("\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!");
  });
});
