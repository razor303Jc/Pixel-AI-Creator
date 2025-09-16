const { test, expect } = require("@playwright/test");

test.describe("Client Creation Quick Test", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
  });

  test("should fill client form correctly", async ({ page }) => {
    // Navigate to dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForTimeout(2000);

    // Click Add Client
    const addClientButton = page.locator('button:has-text("Add Client")');
    await expect(addClientButton).toBeVisible({ timeout: 10000 });
    await addClientButton.click();
    await page.waitForSelector(".modal", { timeout: 5000 });

    // Fill form with correct values
    console.log("Filling name field...");
    await page.fill('input[placeholder*="client name"]', "Razor 303");

    console.log("Filling email field...");
    await page.fill('input[placeholder*="email"]', "jc@razorflow-ai.com");

    console.log("Filling company field...");
    await page.fill('input[placeholder*="company"]', "RazorFlow-AI");

    console.log("Filling description field...");
    await page.fill(
      'textarea[placeholder*="description"]',
      "Leading AI solutions company"
    );

    // Wait and check if submit button is enabled
    await page.waitForTimeout(1000);
    const submitButton = page.locator('button:has-text("Create Client")');
    const isEnabled = await submitButton.isEnabled();
    console.log("Submit button enabled:", isEnabled);

    if (isEnabled) {
      await submitButton.click();
      console.log("Client creation submitted successfully!");
    } else {
      console.log("Submit button is still disabled after filling form");
    }

    await page.waitForTimeout(3000);
  });
});
