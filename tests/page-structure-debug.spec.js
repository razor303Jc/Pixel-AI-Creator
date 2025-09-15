const { test, expect } = require("@playwright/test");

test.describe("Page Structure Investigation", () => {
  test("should investigate current page structure", async ({ page }) => {
    console.log("🔍 Investigating page structure...");

    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Take a screenshot to see what we're working with
    await page.screenshot({ path: "debug-current-page.png", fullPage: true });
    console.log("📸 Screenshot saved as debug-current-page.png");

    // Log the page title
    const title = await page.title();
    console.log(`📄 Page title: ${title}`);

    // Check for various navigation patterns
    const navSelectors = [
      '[data-testid="nav-dashboard"]',
      '[data-testid="nav-build-status"]',
      ".nav-link",
      ".navbar-nav a",
      "nav a",
      'button:has-text("Dashboard")',
      'button:has-text("Build Status")',
      'a:has-text("Dashboard")',
      'a:has-text("Build Status")',
      ".sidebar a",
      ".navigation a",
      ".menu a",
    ];

    console.log("🔍 Checking for navigation elements...");
    for (const selector of navSelectors) {
      const elements = page.locator(selector);
      const count = await elements.count();
      if (count > 0) {
        console.log(`✅ Found ${count} elements with selector: ${selector}`);
        for (let i = 0; i < Math.min(count, 3); i++) {
          const text = await elements.nth(i).textContent();
          console.log(`   ${i + 1}. "${text}"`);
        }
      }
    }

    // Check for any buttons or links
    const allButtons = page.locator("button");
    const buttonCount = await allButtons.count();
    console.log(`🔘 Found ${buttonCount} buttons on page`);

    const allLinks = page.locator("a");
    const linkCount = await allLinks.count();
    console.log(`🔗 Found ${linkCount} links on page`);

    // Check if we need to login first
    const signInButtons = page.locator(
      'button:has-text("Sign In"), .btn:has-text("Sign In")'
    );
    const signInCount = await signInButtons.count();

    if (signInCount > 0) {
      console.log("🔐 Found sign-in button, attempting login...");

      const emailInput = page.locator(
        'input[type="email"], input[name="email"]'
      );
      const passwordInput = page.locator(
        'input[type="password"], input[name="password"]'
      );

      if (await emailInput.isVisible({ timeout: 3000 })) {
        await emailInput.fill("jc@razorflow-ai.com");
        await passwordInput.fill("securepassword123");
        await signInButtons.first().click();

        // Wait for page to load after login
        await page.waitForLoadState("networkidle");

        // Take another screenshot after login
        await page.screenshot({
          path: "debug-after-login.png",
          fullPage: true,
        });
        console.log("📸 Screenshot after login saved as debug-after-login.png");

        // Check navigation again after login
        console.log("🔍 Checking navigation after login...");
        for (const selector of navSelectors) {
          const elements = page.locator(selector);
          const count = await elements.count();
          if (count > 0) {
            console.log(
              `✅ Found ${count} elements with selector: ${selector}`
            );
            for (let i = 0; i < Math.min(count, 3); i++) {
              const text = await elements.nth(i).textContent();
              console.log(`   ${i + 1}. "${text}"`);
            }
          }
        }
      }
    } else {
      console.log("ℹ️ No sign-in button found, might already be logged in");
    }

    // Look for any content that mentions "Build Status" or "Dashboard"
    const pageContent = await page.textContent("body");
    if (pageContent.includes("Build Status")) {
      console.log("✅ Found 'Build Status' text on page");
    }
    if (pageContent.includes("Dashboard")) {
      console.log("✅ Found 'Dashboard' text on page");
    }

    // Check current URL
    const currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);
  });
});
