const { test, expect } = require("@playwright/test");

test.describe("Login and Navigation Debug", () => {
  test("should properly login and check Build Status", async ({ page }) => {
    console.log("🔍 Starting login and navigation debug...");

    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    console.log(`🌐 Initial URL: ${page.url()}`);

    // Check if we're on login page
    const isLoginPage =
      page.url().includes("/login") ||
      (await page.locator('input[type="email"]').isVisible());

    if (isLoginPage) {
      console.log("🔐 On login page, attempting to login...");

      // Fill login form
      await page.fill('input[type="email"]', "jc@razorflow-ai.com");
      await page.fill('input[type="password"]', "securepassword123");

      // Click submit button
      const submitButton = page.locator(
        'button[type="submit"], button:has-text("Sign In"), .btn:has-text("Sign In")'
      );
      await submitButton.click();

      // Wait for navigation
      await page.waitForURL("**", { timeout: 15000 });
      console.log(`🌐 URL after login: ${page.url()}`);

      // Wait for page to load completely
      await page.waitForLoadState("networkidle");

      // Take screenshot after successful login
      await page.screenshot({
        path: "debug-after-successful-login.png",
        fullPage: true,
      });
    }

    // Now check for navigation elements
    console.log("🔍 Looking for navigation elements...");

    // Check various navigation patterns
    const navTests = [
      {
        selector: '[data-testid="nav-dashboard"]',
        name: "Dashboard (data-testid)",
      },
      {
        selector: '[data-testid="nav-build-status"]',
        name: "Build Status (data-testid)",
      },
      { selector: 'a:has-text("Dashboard")', name: "Dashboard link" },
      { selector: 'a:has-text("Build Status")', name: "Build Status link" },
      { selector: 'button:has-text("Dashboard")', name: "Dashboard button" },
      {
        selector: 'button:has-text("Build Status")',
        name: "Build Status button",
      },
      { selector: ".nav-link", name: "Nav links" },
      { selector: ".navbar a", name: "Navbar links" },
      { selector: ".sidebar a", name: "Sidebar links" },
      { selector: "nav a", name: "Nav tag links" },
    ];

    for (const test of navTests) {
      const element = page.locator(test.selector);
      const count = await element.count();
      if (count > 0) {
        console.log(`✅ Found ${count} ${test.name}`);
        const text = await element.first().textContent();
        console.log(`   Text: "${text}"`);
      }
    }

    // Try to find any element with "Build" in it
    const buildElements = page.locator('*:has-text("Build"):visible');
    const buildCount = await buildElements.count();
    console.log(`🔍 Found ${buildCount} elements containing "Build"`);

    for (let i = 0; i < Math.min(buildCount, 5); i++) {
      const text = await buildElements.nth(i).textContent();
      const tagName = await buildElements.nth(i).evaluate((el) => el.tagName);
      console.log(`   ${i + 1}. ${tagName}: "${text}"`);
    }

    // Check the entire page text to see if Build Status exists anywhere
    const bodyText = await page.textContent("body");
    if (bodyText.includes("Build Status")) {
      console.log("✅ 'Build Status' text found on page");
    } else {
      console.log("❌ 'Build Status' text NOT found on page");
    }

    // Check for any tabs or navigation sections
    const tabElements = page.locator(
      '.tab, .nav-tab, .nav-item, .tab-pane, [role="tab"]'
    );
    const tabCount = await tabElements.count();
    console.log(`📑 Found ${tabCount} tab-like elements`);

    for (let i = 0; i < Math.min(tabCount, 10); i++) {
      const text = await tabElements.nth(i).textContent();
      console.log(`   Tab ${i + 1}: "${text}"`);
    }

    // Try to manually navigate to build status if we can find it
    try {
      const buildStatusElement = page
        .locator('*:has-text("Build Status"):visible')
        .first();
      if (await buildStatusElement.isVisible({ timeout: 5000 })) {
        console.log("🎯 Attempting to click Build Status element...");
        await buildStatusElement.click();
        await page.waitForTimeout(3000);
        console.log(`🌐 URL after clicking Build Status: ${page.url()}`);
        await page.screenshot({
          path: "debug-build-status-page.png",
          fullPage: true,
        });

        // Check if we're on the build status page
        const buildStatusHeading = page.locator(
          'h1:has-text("Build Status"), h2:has-text("Build Status"), h3:has-text("Build Status")'
        );
        if (await buildStatusHeading.isVisible({ timeout: 5000 })) {
          console.log("✅ Successfully navigated to Build Status page!");

          // Check for build cards or content
          const buildCards = page.locator(".card");
          const cardCount = await buildCards.count();
          console.log(`📊 Found ${cardCount} cards on Build Status page`);

          // Check for error messages
          const errorMessages = page.locator(
            ".alert-danger, .error, .text-danger"
          );
          const errorCount = await errorMessages.count();
          if (errorCount > 0) {
            for (let i = 0; i < errorCount; i++) {
              const errorText = await errorMessages.nth(i).textContent();
              console.log(`❌ Error message: ${errorText}`);
            }
          }

          // Check for API-related console errors
          page.on("response", (response) => {
            if (
              response.url().includes("/api/builds") &&
              response.status() >= 400
            ) {
              console.log(
                `❌ API Error: ${response.status()} ${response.url()}`
              );
            }
          });
        } else {
          console.log(
            "❌ Could not find Build Status page heading after navigation"
          );
        }
      }
    } catch (error) {
      console.log(
        `⚠️ Error trying to navigate to Build Status: ${error.message}`
      );
    }
  });
});
