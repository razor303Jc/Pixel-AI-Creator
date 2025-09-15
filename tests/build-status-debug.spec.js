const { test, expect } = require("@playwright/test");

test.describe("Build Status Page Debugging", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Login with test credentials
    try {
      const signInButton = page.locator(
        'button:has-text("Sign In"), .btn:has-text("Sign In")'
      );

      if (await signInButton.isVisible({ timeout: 3000 })) {
        console.log("🔐 Logging in with test credentials...");

        const emailInput = page.locator(
          'input[type="email"], input[name="email"]'
        );
        const passwordInput = page.locator(
          'input[type="password"], input[name="password"]'
        );

        await emailInput.fill("jc@razorflow-ai.com");
        await passwordInput.fill("securepassword123");
        await signInButton.click();

        // Wait for navigation after login
        await page.waitForSelector(
          '[data-testid="nav-dashboard"], .nav-link, .dashboard, .sidebar, .navbar',
          { timeout: 15000 }
        );
        console.log("✅ Successfully logged in");
      } else {
        console.log("✅ Already logged in");
      }
    } catch (error) {
      console.log("⚠️ Login process - continuing with existing session");
    }
  });

  test("should debug Build Status page and API calls", async ({ page }) => {
    console.log("🔍 Starting Build Status debugging...");

    // Listen to console logs
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log(`❌ Browser Console Error: ${msg.text()}`);
      } else if (msg.type() === "warn") {
        console.log(`⚠️ Browser Console Warning: ${msg.text()}`);
      }
    });

    // Listen to network requests
    const apiRequests = [];
    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          headers: request.headers(),
          postData: request.postData(),
        });
        console.log(`📡 API Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on("response", (response) => {
      if (response.url().includes("/api/")) {
        console.log(`📡 API Response: ${response.status()} ${response.url()}`);
      }
    });

    // Navigate to Build Status page
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")', {
      timeout: 10000,
    });

    console.log("✅ Successfully navigated to Build Status page");

    // Wait for any API calls to complete
    await page.waitForTimeout(3000);

    // Check for error messages on the page
    const errorAlerts = page.locator(".alert-danger");
    const errorCount = await errorAlerts.count();

    if (errorCount > 0) {
      for (let i = 0; i < errorCount; i++) {
        const errorText = await errorAlerts.nth(i).textContent();
        console.log(`❌ Error on page: ${errorText}`);
      }
    }

    // Check for empty state message
    const infoAlerts = page.locator(".alert-info");
    const infoCount = await infoAlerts.count();

    if (infoCount > 0) {
      for (let i = 0; i < infoCount; i++) {
        const infoText = await infoAlerts.nth(i).textContent();
        console.log(`ℹ️ Info message: ${infoText}`);
      }
    }

    // Check for build cards
    const buildCards = page.locator(".card");
    const buildCount = await buildCards.count();
    console.log(`📊 Found ${buildCount} build cards`);

    // Log all API requests made
    console.log(`📡 Total API requests made: ${apiRequests.length}`);
    apiRequests.forEach((req, index) => {
      console.log(`${index + 1}. ${req.method} ${req.url}`);
      if (req.postData) {
        console.log(`   Data: ${req.postData}`);
      }
    });

    // Test manual refresh functionality
    const refreshButton = page.locator('button:has-text("Refresh")');
    if (await refreshButton.isVisible()) {
      console.log("🔄 Testing manual refresh...");
      await refreshButton.click();
      await page.waitForTimeout(2000);
    }

    // Check auto-refresh button state
    const autoRefreshButton = page.locator('button:has-text("Auto Refresh")');
    if (await autoRefreshButton.isVisible()) {
      const buttonText = await autoRefreshButton.textContent();
      console.log(`🔄 Auto-refresh status: ${buttonText}`);
    }
  });

  test("should test assistant creation with auto-build debugging", async ({
    page,
  }) => {
    console.log("🚀 Testing assistant creation with detailed debugging...");

    // Listen to network requests
    const apiRequests = [];
    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        const postData = request.postData();
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          postData: postData,
        });
        console.log(`📡 API Request: ${request.method()} ${request.url()}`);
        if (postData) {
          console.log(`📡 Request Data: ${postData}`);
        }
      }
    });

    page.on("response", async (response) => {
      if (response.url().includes("/api/")) {
        console.log(`📡 API Response: ${response.status()} ${response.url()}`);
        if (response.status() >= 400) {
          try {
            const responseText = await response.text();
            console.log(`❌ Error Response: ${responseText}`);
          } catch (e) {
            console.log(`❌ Could not read error response`);
          }
        }
      }
    });

    // Navigate to main dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForSelector('button:has-text("Create Assistant")', {
      timeout: 10000,
    });

    const assistantName = `Debug Test ${Date.now()}`;

    // Create assistant with auto-build
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      assistantName
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });
    await page.fill(
      'textarea[placeholder*="description"]',
      "Testing auto-build debugging"
    );

    // Enable auto-build
    await page.check("#auto-build-checkbox");
    await expect(page.locator("#auto-build-checkbox")).toBeChecked();
    console.log("✅ Auto-build checkbox checked");

    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Wait for any success/error messages
    await page.waitForTimeout(3000);

    // Check for success messages
    const toasts = page.locator(".toast, .alert");
    const toastCount = await toasts.count();

    if (toastCount > 0) {
      for (let i = 0; i < toastCount; i++) {
        const toastText = await toasts.nth(i).textContent();
        console.log(`📢 Toast/Alert message: ${toastText}`);
      }
    }

    // Log all API requests from assistant creation
    console.log(`📡 Assistant creation API requests: ${apiRequests.length}`);
    apiRequests.forEach((req, index) => {
      console.log(`${index + 1}. ${req.method} ${req.url}`);
      if (req.postData) {
        console.log(`   Data: ${req.postData}`);
      }
    });

    // Navigate to Build Status to see if the build appears
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")', {
      timeout: 5000,
    });

    // Wait for builds to load
    await page.waitForTimeout(5000);

    // Check for new builds
    const buildCards = page.locator(".card");
    const buildCount = await buildCards.count();
    console.log(`📊 Found ${buildCount} build cards after creation`);

    if (buildCount > 0) {
      // Check the first build card for our assistant
      const firstCard = buildCards.first();
      const cardText = await firstCard.textContent();
      console.log(`📊 First build card content: ${cardText}`);

      if (cardText.includes(assistantName)) {
        console.log("✅ Found our assistant in the build list!");
      } else {
        console.log("⚠️ Our assistant not found in the build list");
      }
    }
  });
});
