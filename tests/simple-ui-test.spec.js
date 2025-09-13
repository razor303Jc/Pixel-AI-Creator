/**
 * SIMPLE UI DEMONSTRATION TEST
 * Pixel AI Creator - Basic Interface Testing
 */

const { test, expect } = require("@playwright/test");

test.describe("Pixel AI Creator - UI Demo", () => {
  test("Basic Interface Test", async ({ page }) => {
    console.log("🚀 Starting UI Demo Test...");

    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("domcontentloaded");

    // Check title
    await expect(page).toHaveTitle(/Pixel AI Creator/i);
    console.log("✅ Page title verified");

    // Take a screenshot
    await page.screenshot({
      path: "test-results/ui-demo.png",
      fullPage: true,
    });
    console.log("📸 Screenshot captured");

    // Look for main elements
    const body = page.locator("body");
    await expect(body).toBeVisible();
    console.log("✅ Page body visible");

    console.log("🎉 UI Demo Test Complete!");
  });
});
