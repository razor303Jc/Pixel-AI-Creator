const { test, expect } = require("@playwright/test");

// Test configuration
const BASE_URL = "http://localhost:3002";

test.describe("Dashboard Navigation Basic Test", () => {
  test("should load the application and check if navigation elements exist", async ({
    page,
  }) => {
    // Go directly to the app
    await page.goto(BASE_URL);

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Take a screenshot for debugging
    await page.screenshot({ path: "debug-homepage.png", fullPage: true });

    // Log what's on the page
    const pageContent = await page.content();
    console.log("Page title:", await page.title());
    console.log("Page URL:", page.url());

    // Check if we're on login page or dashboard
    const isLoginPage = await page
      .locator("text=Sign in")
      .isVisible()
      .catch(() => false);
    const isDashboard = await page
      .locator('[data-testid="nav-dashboard"]')
      .isVisible()
      .catch(() => false);

    console.log("Is login page:", isLoginPage);
    console.log("Is dashboard:", isDashboard);

    if (isLoginPage) {
      console.log("App is showing login page - need to authenticate first");

      // Try to find and fill login form
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const submitButton = page.locator(
        'button[type="submit"], button:has-text("Sign In")'
      );

      if ((await emailInput.isVisible()) && (await passwordInput.isVisible())) {
        await emailInput.fill("test@example.com");
        await passwordInput.fill("testpassword");
        await submitButton.click();

        // Wait for navigation
        await page.waitForLoadState("networkidle");
        await page.screenshot({
          path: "debug-after-login.png",
          fullPage: true,
        });
      }
    }

    // Now check for dashboard elements
    const navElements = await page.locator('[data-testid^="nav-"]').all();
    console.log(`Found ${navElements.length} navigation elements`);

    // Log all visible elements that might be navigation
    const possibleNavElements = await page
      .locator('nav a, .nav-link, [class*="nav"]')
      .all();
    for (let i = 0; i < Math.min(possibleNavElements.length, 10); i++) {
      const text = await possibleNavElements[i].textContent();
      console.log(`Nav element ${i}:`, text);
    }
  });

  test("should test templates page directly if accessible", async ({
    page,
  }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");

    // Check if Templates component is accessible
    const templatesTitle = await page
      .locator('[data-testid="templates-title"]')
      .isVisible()
      .catch(() => false);
    console.log("Templates title visible:", templatesTitle);

    if (templatesTitle) {
      // Test templates functionality
      const createButton = await page
        .locator('[data-testid="create-template-btn"]')
        .isVisible()
        .catch(() => false);
      console.log("Create template button visible:", createButton);
    }

    await page.screenshot({
      path: "debug-templates-check.png",
      fullPage: true,
    });
  });
});
