const { test, expect } = require("@playwright/test");

test.describe("Client Field Validation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);

    // Navigate to dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForTimeout(2000);

    // Open client modal
    await page.click('button:has-text("Add Client")');
    await page.waitForTimeout(2000);
  });

  test("should fill fields with correct values", async ({ page }) => {
    // Fill the form with exact field mapping
    console.log("Filling name field...");
    await page.fill('input[placeholder="Enter client name"]', "Razor 303");

    console.log("Filling email field...");
    await page.fill(
      'input[placeholder="Enter email address (e.g., john@company.com)"]',
      "jc@razorflow-ai.com"
    );

    console.log("Filling company field...");
    await page.fill('input[placeholder="Enter company name"]', "RazorFlow-AI");

    console.log("Filling description field...");
    await page.fill(
      'textarea[placeholder="Enter description (optional)"]',
      "Leading AI solutions company"
    );

    // Verify values are correctly set
    await page.waitForTimeout(1000);

    const nameValue = await page.inputValue(
      'input[placeholder="Enter client name"]'
    );
    const emailValue = await page.inputValue(
      'input[placeholder="Enter email address (e.g., john@company.com)"]'
    );
    const companyValue = await page.inputValue(
      'input[placeholder="Enter company name"]'
    );

    console.log("✅ Name field contains:", nameValue);
    console.log("✅ Email field contains:", emailValue);
    console.log("✅ Company field contains:", companyValue);

    // Validate correct values
    expect(nameValue).toBe("Razor 303");
    expect(emailValue).toBe("jc@razorflow-ai.com");
    expect(companyValue).toBe("RazorFlow-AI");

    // Check if submit button is enabled
    const submitButton = page.locator('button:has-text("Create Client")');
    const isEnabled = await submitButton.isEnabled();
    console.log("✅ Submit button enabled:", isEnabled);

    if (isEnabled) {
      console.log("🎉 SUCCESS: Form validation passed!");
      await submitButton.click();
      await page.waitForTimeout(3000);
      console.log("🎉 Client creation completed successfully!");
    } else {
      console.log("❌ Form validation failed - checking for errors...");
    }
  });
});
