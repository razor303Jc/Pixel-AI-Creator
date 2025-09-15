const { test, expect } = require("@playwright/test");

test.describe("Direct Build Status Access Test", () => {
  test("should access Build Status directly and test the auto-build issue", async ({
    page,
  }) => {
    console.log("🎯 Testing Build Status issue with direct access approach...");

    // Set up console and network monitoring
    const consoleMessages = [];
    const networkRequests = [];
    const networkResponses = [];

    page.on("console", (msg) => {
      consoleMessages.push(`${msg.type()}: ${msg.text()}`);
      console.log(`🖥️ Console ${msg.type()}: ${msg.text()}`);
    });

    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        networkRequests.push({
          method: request.method(),
          url: request.url(),
          data: request.postData(),
        });
        console.log(`📡 API Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on("response", (response) => {
      if (response.url().includes("/api/")) {
        networkResponses.push({
          status: response.status(),
          url: response.url(),
        });
        console.log(`📡 API Response: ${response.status()} ${response.url()}`);
      }
    });

    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Try multiple authentication approaches
    console.log("\n🔐 Testing various authentication methods...");

    // Method 1: Standard form fill
    try {
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const submitButton = page.locator(
        'button[type="submit"], button:has-text("Sign In")'
      );

      if (await emailInput.isVisible({ timeout: 3000 })) {
        await emailInput.fill("jc@razorflow-ai.com");
        await passwordInput.fill("securepassword123");
        await submitButton.click();
        await page.waitForTimeout(3000);
        console.log("✅ Method 1: Form fill completed");
      }
    } catch (e) {
      console.log("⚠️ Method 1 failed, trying alternatives...");
    }

    // Method 2: Check if already authenticated
    let currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);

    // Method 3: Try direct navigation to dashboard
    if (
      currentUrl.includes("/login") ||
      currentUrl === "http://localhost:3002/"
    ) {
      try {
        await page.goto("http://localhost:3002/#dashboard");
        await page.waitForTimeout(2000);
        console.log("🔄 Tried direct dashboard navigation");
      } catch (e) {
        console.log("⚠️ Direct navigation failed");
      }
    }

    // Method 4: Check for different authentication states
    const pageContent = await page.textContent("body");
    console.log(
      `📄 Page contains dashboard elements: ${
        pageContent.includes("Dashboard") ||
        pageContent.includes("Create Assistant")
      }`
    );

    // If we can find any dashboard-like content, proceed
    if (
      pageContent.includes("Dashboard") ||
      pageContent.includes("Create") ||
      pageContent.includes("Assistant")
    ) {
      console.log(
        "✅ Found dashboard-like content, proceeding with Build Status test..."
      );

      // Look for Build Status navigation
      const buildStatusSelectors = [
        '[data-testid="nav-build-status"]',
        'text="Build Status"',
        'button:has-text("Build Status")',
        '.nav-link:has-text("Build")',
        '*:has-text("Build Status")',
      ];

      let buildStatusFound = false;
      for (const selector of buildStatusSelectors) {
        try {
          const element = page.locator(selector);
          if (await element.isVisible({ timeout: 2000 })) {
            console.log(`✅ Found Build Status with selector: ${selector}`);
            await element.click();
            await page.waitForTimeout(2000);
            buildStatusFound = true;
            break;
          }
        } catch (e) {
          continue;
        }
      }

      if (buildStatusFound) {
        console.log("🎯 Successfully accessed Build Status page!");
        await page.screenshot({
          path: "build-status-accessed.png",
          fullPage: true,
        });

        // Check for build content
        const buildCards = await page.locator(".card").count();
        const errorAlerts = await page.locator(".alert-danger").count();
        const infoAlerts = await page.locator(".alert-info").count();

        console.log(`📊 Build cards found: ${buildCards}`);
        console.log(`❌ Error alerts: ${errorAlerts}`);
        console.log(`ℹ️ Info alerts: ${infoAlerts}`);

        // Check for specific error messages
        if (errorAlerts > 0) {
          for (let i = 0; i < errorAlerts; i++) {
            const errorText = await page
              .locator(".alert-danger")
              .nth(i)
              .textContent();
            console.log(`❌ Error ${i + 1}: ${errorText}`);
          }
        }

        // Check for API errors in network requests
        const apiErrors = networkResponses.filter((r) => r.status >= 400);
        if (apiErrors.length > 0) {
          console.log(`📡 API Errors detected: ${apiErrors.length}`);
          apiErrors.forEach((error) => {
            console.log(`   ${error.status} ${error.url}`);
          });
        }

        // Test the builds API endpoint directly
        console.log("\n🔬 Testing builds API endpoint...");
        try {
          const response = await page.evaluate(async () => {
            try {
              const res = await fetch("/api/builds/", {
                headers: {
                  Authorization: `Bearer ${localStorage.getItem("authToken")}`,
                  "Content-Type": "application/json",
                },
              });
              return {
                status: res.status,
                data: await res.text(),
              };
            } catch (error) {
              return {
                error: error.message,
              };
            }
          });

          console.log(`📡 Direct API test result: ${JSON.stringify(response)}`);
        } catch (e) {
          console.log(`❌ Direct API test failed: ${e.message}`);
        }
      } else {
        console.log("❌ Build Status navigation not found");

        // Try to create an assistant to test the auto-build feature
        console.log("\n🤖 Testing assistant creation to trigger auto-build...");

        const createButton = page.locator(
          'button:has-text("Create Assistant"), button:has-text("Create")'
        );
        if (await createButton.isVisible({ timeout: 5000 })) {
          await createButton.click();
          await page.waitForSelector(".modal", { timeout: 5000 });

          const assistantName = `Auto Build Test ${Date.now()}`;
          await page.fill(
            'input[name="name"], input[placeholder*="name"]',
            assistantName
          );

          // Look for auto-build checkbox
          const autoCheckboxes = page.locator('input[type="checkbox"]');
          const checkboxCount = await autoCheckboxes.count();
          console.log(`🔘 Found ${checkboxCount} checkboxes`);

          for (let i = 0; i < checkboxCount; i++) {
            const label = await page.locator("label").nth(i).textContent();
            console.log(`   Checkbox ${i + 1}: ${label}`);
            if (
              label &&
              label.toLowerCase().includes("auto") &&
              label.toLowerCase().includes("build")
            ) {
              await autoCheckboxes.nth(i).check();
              console.log(`✅ Checked auto-build checkbox: ${label}`);
              break;
            }
          }

          // Submit form
          await page.click('button:has-text("Create"), button[type="submit"]');
          await page.waitForTimeout(3000);

          console.log("✅ Assistant creation attempted with auto-build");

          // Check network requests for build queue
          const buildRequests = networkRequests.filter(
            (req) => req.url.includes("/builds/") || req.url.includes("queue")
          );
          console.log(`📡 Build-related requests: ${buildRequests.length}`);
          buildRequests.forEach((req) => {
            console.log(`   ${req.method} ${req.url}`);
            if (req.data) console.log(`   Data: ${req.data}`);
          });
        }
      }
    } else {
      console.log(
        "❌ No dashboard content found - authentication may have failed"
      );
      await page.screenshot({ path: "auth-failed-state.png", fullPage: true });
    }

    // Summary
    console.log("\n📊 Test Summary:");
    console.log(`🖥️ Console messages: ${consoleMessages.length}`);
    console.log(`📡 API requests: ${networkRequests.length}`);
    console.log(`📡 API responses: ${networkResponses.length}`);

    // Show any console errors
    const errors = consoleMessages.filter((msg) => msg.startsWith("error:"));
    if (errors.length > 0) {
      console.log("❌ Console errors found:");
      errors.forEach((error) => console.log(`   ${error}`));
    }

    await page.screenshot({
      path: "final-build-status-test-state.png",
      fullPage: true,
    });
  });
});
