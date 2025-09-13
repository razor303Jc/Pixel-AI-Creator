const { test, expect } = require("@playwright/test");

test("debug detailed loading state", async ({ page }) => {
  await page.goto("http://localhost:3002");
  await page.waitForLoadState("domcontentloaded");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);

  // Navigate to registration form
  await page.click('text="Sign up here"');
  await page.waitForTimeout(1000);
  await page.waitForSelector('text="Create Account"', { timeout: 5000 });

  // Fill in valid form data
  await page.fill('input[name="email"]', "test@example.com");
  await page.fill('input[name="password"]', "ValidPassword123!");
  await page.fill('input[name="confirmPassword"]', "ValidPassword123!");
  await page.fill('input[name="firstName"]', "John");
  await page.fill('input[name="lastName"]', "Doe");

  const submitButton = page.locator('button[type="submit"]');

  console.log("=== BEFORE SUBMIT ===");
  const buttonTextBefore = await submitButton.textContent();
  console.log("Button text before:", buttonTextBefore?.trim());
  const isDisabledBefore = await submitButton.isDisabled();
  console.log("Button disabled before:", isDisabledBefore);

  // Click submit button
  await submitButton.click();

  // Check immediately after click
  console.log("=== IMMEDIATE CHECK ===");
  const buttonTextImmediate = await submitButton.textContent();
  console.log("Button text immediate:", buttonTextImmediate?.trim());
  const isDisabledImmediate = await submitButton.isDisabled();
  console.log("Button disabled immediate:", isDisabledImmediate);

  // Wait a bit for state changes
  await page.waitForTimeout(200);

  console.log("=== AFTER 200ms ===");
  const buttonTextAfter = await submitButton.textContent();
  console.log("Button text after 200ms:", buttonTextAfter?.trim());
  const isDisabledAfter = await submitButton.isDisabled();
  console.log("Button disabled after:", isDisabledAfter);

  const spinnerElements = await page.locator("span.spinner-border").count();
  console.log("Spinner elements found:", spinnerElements);

  // Check for "Creating Account..." text specifically
  const creatingAccountText = await page
    .locator("text=Creating Account...")
    .count();
  console.log("Creating Account text found:", creatingAccountText);

  // Check for "Processing..." text
  const processingText = await page.locator("text=Processing...").count();
  console.log("Processing text found:", processingText);

  // Wait longer to see what happens
  await page.waitForTimeout(2000);

  console.log("=== AFTER 2 SECONDS ===");
  const buttonTextFinal = await submitButton.textContent();
  console.log("Button text final:", buttonTextFinal?.trim());
  const isDisabledFinal = await submitButton.isDisabled();
  console.log("Button disabled final:", isDisabledFinal);
});
