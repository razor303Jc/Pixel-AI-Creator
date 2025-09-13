const { test } = require("@playwright/test");

test("debug loading state with empty form", async ({ page }) => {
  await page.goto("http://localhost:3002");
  await page.waitForSelector("h3", { timeout: 10000 });
  await page.click('text="Sign up here"');
  await page.waitForSelector('button[type="submit"]', { timeout: 5000 });

  console.log("=== TESTING WITH EMPTY FORM ===");

  // Check button text before submit (should show Create Account)
  const buttonTextBefore = await page
    .locator('button[type="submit"]')
    .textContent();
  console.log("Button text before:", buttonTextBefore);

  // Submit empty form
  await page.locator('button[type="submit"]').click();

  // Check immediately after
  await page.waitForTimeout(100);
  const buttonTextAfter = await page
    .locator('button[type="submit"]')
    .textContent();
  console.log("Button text after empty form submit:", buttonTextAfter);

  // Check for spinner
  const spinnerCount = await page.locator('span[role="status"]').count();
  console.log("Spinner elements after empty submit:", spinnerCount);

  await page.waitForTimeout(1000);
});
