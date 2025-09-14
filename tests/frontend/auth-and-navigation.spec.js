const { test, expect } = require("@playwright/test");

// Test configuration
const BASE_URL = "http://localhost:3002";

test.describe("Dashboard Navigation Tests", () => {
  test("should authenticate and access dashboard navigation", async ({
    page,
  }) => {
    // Go to the application
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");

    // Check if we need to log in
    const isLoginPage = await page.locator("form").isVisible();

    if (isLoginPage) {
      console.log("Login page detected, attempting to authenticate...");

      // Try to find and fill the login form
      const emailInput = await page
        .locator(
          'input[type="email"], input[name="email"], input[placeholder*="email" i]'
        )
        .first();
      const passwordInput = await page
        .locator('input[type="password"], input[name="password"]')
        .first();

      if ((await emailInput.isVisible()) && (await passwordInput.isVisible())) {
        // Try common test credentials
        await emailInput.fill("admin@example.com");
        await passwordInput.fill("admin123");

        // Find and click submit button
        const submitButton = await page
          .locator(
            'button[type="submit"], button:has-text("Sign In"), button:has-text("Login"), .btn-primary'
          )
          .first();
        await submitButton.click();

        // Wait for potential redirect or loading
        await page.waitForTimeout(3000);
        await page.waitForLoadState("networkidle");
      }
    }

    // Check if we're now authenticated by looking for dashboard elements
    await page.screenshot({ path: "dashboard-state.png", fullPage: true });

    // Look for navigation elements
    const navDashboard = await page
      .locator('[data-testid="nav-dashboard"]')
      .isVisible()
      .catch(() => false);
    const navAnalytics = await page
      .locator('[data-testid="nav-analytics"]')
      .isVisible()
      .catch(() => false);
    const navTemplates = await page
      .locator('[data-testid="nav-templates"]')
      .isVisible()
      .catch(() => false);

    console.log("Navigation elements found:");
    console.log("Dashboard nav:", navDashboard);
    console.log("Analytics nav:", navAnalytics);
    console.log("Templates nav:", navTemplates);

    if (navDashboard || navAnalytics || navTemplates) {
      console.log("SUCCESS: Dashboard navigation elements found!");

      // Test navigation functionality
      if (navAnalytics) {
        await page.locator('[data-testid="nav-analytics"]').click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: "analytics-view.png", fullPage: true });
      }

      if (navTemplates) {
        await page.locator('[data-testid="nav-templates"]').click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: "templates-view.png", fullPage: true });

        // Check for templates functionality
        const templatesTitle = await page
          .locator('[data-testid="templates-title"]')
          .isVisible()
          .catch(() => false);
        const createButton = await page
          .locator('[data-testid="create-template-btn"]')
          .isVisible()
          .catch(() => false);
        console.log("Templates title visible:", templatesTitle);
        console.log("Create template button visible:", createButton);
      }

      if (navDashboard) {
        await page.locator('[data-testid="nav-dashboard"]').click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: "dashboard-view.png", fullPage: true });
      }
    } else {
      console.log("No navigation elements found. Current page content:");
      const bodyText = await page.locator("body").textContent();
      console.log(bodyText.substring(0, 500) + "...");
    }
  });

  test("should handle mock authentication if needed", async ({ page }) => {
    // Mock the authentication state by injecting localStorage
    await page.goto(BASE_URL);

    // Try to mock authentication by setting localStorage
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token-for-testing");
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: 1,
          email: "test@example.com",
          name: "Test User",
        })
      );
    });

    // Reload the page to trigger auth check
    await page.reload();
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    await page.screenshot({ path: "mock-auth-state.png", fullPage: true });

    // Check for dashboard navigation
    const hasNavigation = await page.locator('[data-testid^="nav-"]').count();
    console.log("Navigation elements with mock auth:", hasNavigation);

    if (hasNavigation > 0) {
      console.log("SUCCESS: Mock authentication worked!");
    }
  });
});
