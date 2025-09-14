const { test, expect } = require("@playwright/test");

const BASE_URL = "http://localhost:3002";

test.describe("🐛 Debug Form Submission", () => {
  test("debug form validation error display", async ({ page }) => {
    // Enable console logging
    page.on("console", (msg) => console.log("PAGE LOG:", msg.text()));

    await page.goto(BASE_URL);
    await page.waitForLoadState("domcontentloaded");

    console.log("✅ React app loaded successfully");

    // Switch to registration form
    await page.click('text="Sign up here"');
    console.log("🔄 Switched to registration form");

    await page.waitForTimeout(1000);

    // Try to submit empty form
    const submitButton = page.locator('button[type="submit"]');
    console.log("🔄 Clicking submit button...");

    // Check if button exists and is visible
    const buttonCount = await submitButton.count();
    console.log("🔍 Number of submit buttons found:", buttonCount);

    if (buttonCount > 0) {
      const isVisible = await submitButton.isVisible();
      const isEnabled = await submitButton.isEnabled();
      console.log("🔍 Submit button visible:", isVisible);
      console.log("🔍 Submit button enabled:", isEnabled);

      // Try clicking the button
      await submitButton.click();
      console.log("✅ Button click completed");
    } else {
      console.log("❌ No submit button found!");
    }

    // Check form structure
    const forms = await page.locator("form").count();
    console.log("🔍 Number of forms on page:", forms);

    if (forms > 0) {
      const formHTML = await page.locator("form").first().innerHTML();
      console.log(
        "📄 Form HTML structure (first 500 chars):",
        formHTML.substring(0, 500)
      );
    }

    // Check for any JavaScript errors
    const errors = [];
    page.on("pageerror", (error) => {
      errors.push(error.message);
      console.log("❌ Page error:", error.message);
    });

    // Wait a bit and check what's in the DOM
    await page.waitForTimeout(2000);

    console.log("📄 Current page title:", await page.title());
    console.log("📄 Current URL:", page.url());

    // Check if any error elements exist
    const errorAlerts = await page.locator(".alert-danger").count();
    console.log("🔍 Number of .alert-danger elements:", errorAlerts);

    const alerts = await page.locator(".alert").count();
    console.log("🔍 Number of .alert elements:", alerts);

    // Check for any text containing "Please fix"
    const pleaseFixText = await page.locator('text="Please fix"').count();
    console.log("🔍 Number of 'Please fix' text elements:", pleaseFixText);

    // Try different selectors for the validation error text
    const exactText = await page
      .locator('text="Please fix the validation errors below"')
      .count();
    console.log("🔍 Exact text match count:", exactText);

    const containsText = await page
      .locator(':has-text("Please fix the validation errors below")')
      .count();
    console.log("🔍 Contains text match count:", containsText);

    const partialText = await page.locator(':has-text("Please fix")').count();
    console.log("🔍 Partial text match count:", partialText);

    // Get all text content on page
    const bodyText = await page.locator("body").textContent();
    console.log(
      "📄 Does page contain 'Please fix':",
      bodyText.includes("Please fix")
    );
    console.log(
      "📄 Does page contain 'validation':",
      bodyText.includes("validation")
    );

    // Check if button shows loading state
    const buttonText = await submitButton.textContent();
    console.log("🔘 Button text:", buttonText);

    // Take a screenshot for debugging
    await page.screenshot({ path: "debug-form-submission.png" });
    console.log("📸 Screenshot taken: debug-form-submission.png");
  });
});
