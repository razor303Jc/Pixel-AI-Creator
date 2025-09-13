const { test, expect } = require("@playwright/test");

test("debug loading state", async ({ page }) => {
  await page.goto("http://localhost:3000/register");
  await page.waitForSelector("form");

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

  // Click submit button
  await submitButton.click();

  // Wait a bit for state changes
  await page.waitForTimeout(100);

  console.log("=== AFTER WAIT ===");
  const buttonTextAfter = await submitButton.textContent();
  console.log("Button text after:", buttonTextAfter?.trim());

  const spinnerElements = await page.locator("span.spinner-border").count();
  console.log("Spinner elements found:", spinnerElements);

  const buttonHTML = await submitButton.innerHTML();
  console.log("Button HTML:", buttonHTML);

  // Check if button is disabled
  const isDisabled = await submitButton.isDisabled();
  console.log("Button is disabled:", isDisabled);

  // Check for "Creating Account..." text
  const hasCreatingText = await page
    .locator("text=Creating Account...")
    .count();
  console.log("Creating Account text found:", hasCreatingText);
});
