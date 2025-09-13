const { test, expect } = require("@playwright/test");

test("debug form submission", async ({ page }) => {
  // Listen for ALL console messages
  page.on("console", (msg) => {
    console.log(`BROWSER ${msg.type().toUpperCase()}: ${msg.text()}`);
  });

  page.on("pageerror", (error) => {
    console.log("BROWSER PAGE ERROR:", error.message);
  });

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto("http://localhost:3002");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);

  // Wait for React app to load
  await page.waitForSelector("h3", { timeout: 10000 });

  // Click sign up
  await page.click('text="Sign up here"');
  await page.waitForTimeout(1000);

  // Verify we're on registration form
  await page.waitForSelector('text="Create Account"', { timeout: 5000 });

  console.log("=== BEFORE SUBMIT ===");

  // Find and click submit button
  const submitButton = page.locator('button[type="submit"]');
  console.log("Submit button found:", await submitButton.isVisible());

  await submitButton.click();
  console.log("Submit button clicked");

  // Wait and look for immediate console output
  await page.waitForTimeout(1000);

  // Try to click the submit button again to see if it works
  console.log("=== CLICKING SUBMIT AGAIN ===");
  await submitButton.click();

  await page.waitForTimeout(3000); // Wait longer

  console.log("=== AFTER SUBMIT ===");

  // Check for alert/error components specifically
  const alertDanger = await page.locator(".alert-danger").isVisible();
  console.log("Alert danger visible:", alertDanger);

  if (alertDanger) {
    const alertText = await page.locator(".alert-danger").textContent();
    console.log("Alert text:", alertText);
  }

  // Check if fields have is-invalid class
  const emailField = page.locator('input[type="email"]');
  const passwordField = page.locator('input[type="password"]').first();

  const emailClasses = await emailField.getAttribute("class");
  const passwordClasses = await passwordField.getAttribute("class");

  console.log("Email field classes:", emailClasses);
  console.log("Password field classes:", passwordClasses);

  // Check for any field validation messages
  const validationMessages = await page
    .locator(".invalid-feedback, .text-danger")
    .allTextContents();
  console.log("All validation messages:", validationMessages);

  // Check for specific validation messages
  const emailRequired = await page
    .locator('text="Email is required"')
    .isVisible();
  const passwordRequired = await page
    .locator('text="Password is required"')
    .isVisible();
  const firstNameRequired = await page
    .locator('text="First name is required"')
    .isVisible();

  console.log("Email required visible:", emailRequired);
  console.log("Password required visible:", passwordRequired);
  console.log("First name required visible:", firstNameRequired);

  // Check for form control feedback
  const invalidFeedback = await page
    .locator(".invalid-feedback")
    .allTextContents();
  console.log("Invalid feedback texts:", invalidFeedback);

  // Look for any text containing "required"
  const requiredTexts = await page
    .locator("text=/.*required.*/i")
    .allTextContents();
  console.log('All "required" texts:', requiredTexts);
});
