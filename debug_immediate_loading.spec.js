const { test, expect } = require("@playwright/test");

test("debug immediate loading state", async ({ page }) => {
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

  // Start clicking and immediately check for changes
  const clickPromise = submitButton.click();

  // Check for loading state within 100ms intervals
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(50);
    const buttonText = await submitButton.textContent();
    const isDisabled = await submitButton.isDisabled();
    const spinnerCount = await page.locator("span.spinner-border").count();

    console.log(
      `Check ${
        i * 50
      }ms: text="${buttonText?.trim()}" disabled=${isDisabled} spinner=${spinnerCount}`
    );

    if (
      buttonText?.includes("Creating Account") ||
      isDisabled ||
      spinnerCount > 0
    ) {
      console.log("🎉 LOADING STATE DETECTED!");
      break;
    }
  }

  await clickPromise;
  console.log("Click completed");
});
