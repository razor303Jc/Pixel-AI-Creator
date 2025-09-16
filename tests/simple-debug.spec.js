const { test, expect } = require("@playwright/test");

test.describe("Simple Debug Test", () => {
  test("check page after login", async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.waitForTimeout(2000);

    // Login
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);

    // Take screenshot and log page info
    await page.screenshot({ path: "debug-page.png" });
    console.log("Current URL:", page.url());
    console.log("Page title:", await page.title());

    // Count all buttons
    const buttonCount = await page.locator("button").count();
    console.log("Total buttons found:", buttonCount);

    // Get first 10 button texts
    const buttons = await page.locator("button").all();
    for (let i = 0; i < Math.min(buttons.length, 10); i++) {
      const text = await buttons[i].textContent();
      console.log(`Button ${i}: "${text?.trim() || "empty"}"`);
    }

    expect(buttonCount).toBeGreaterThan(0);
  });
});
