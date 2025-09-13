const { test, expect } = require("@playwright/test");

test("debug page content", async ({ page }) => {
  // Listen for console messages
  page.on("console", (msg) => {
    console.log(`BROWSER CONSOLE [${msg.type()}]:`, msg.text());
  });

  // Listen for page errors
  page.on("pageerror", (error) => {
    console.log("BROWSER ERROR:", error.message);
  });

  await page.goto("http://localhost:3002");

  // Wait for network to be idle
  await page.waitForLoadState("networkidle");

  // Wait for React to load by waiting for the app to render
  try {
    await page.waitForSelector("h3", { timeout: 10000 });
    console.log("✅ React app loaded");
  } catch (e) {
    console.log("❌ React app did not load:", e.message);
  }

  await page.waitForTimeout(2000);

  // Take a screenshot
  await page.screenshot({ path: "debug-page.png" });

  // Get all text content
  const bodyText = await page.textContent("body");
  console.log("=== PAGE TEXT CONTENT ===");
  console.log(bodyText);

  // Look for any links or buttons
  const links = await page.locator("a, button").allTextContents();
  console.log("=== LINKS AND BUTTONS ===");
  console.log(links);

  // Look for register-related text
  const signUpElements = await page
    .locator("text=/sign.*up/i")
    .allTextContents();
  console.log("=== SIGN UP ELEMENTS ===");
  console.log(signUpElements);
});
