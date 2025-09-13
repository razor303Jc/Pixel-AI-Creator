const { test, expect } = require("@playwright/test");

test("debug button click", async ({ page }) => {
  // Enable console logging
  page.on("console", (msg) => console.log("PAGE LOG:", msg.text()));

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

  console.log("=== ABOUT TO CLICK BUTTON ===");

  // Click the button and see what happens
  await submitButton.click();
  console.log("=== BUTTON CLICKED ===");

  // Wait to see logs
  await page.waitForTimeout(3000);
});
