import { test, expect } from "@playwright/test";

/**
 * Debug Test - Check what's on the page
 */

test.describe("Debug Templates Page", () => {
  test("take screenshot and debug page content", async ({ page }) => {
    console.log("🔍 Starting debug test...");

    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Take initial screenshot
    await page.screenshot({
      path: "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/debug-initial-page.png",
      fullPage: true,
    });
    console.log("📸 Initial page screenshot saved");

    // Log page title and URL
    const title = await page.title();
    const url = page.url();
    console.log(`📄 Page title: ${title}`);
    console.log(`🔗 Current URL: ${url}`);

    // Log all visible text on the page
    const pageText = await page.textContent("body");
    console.log(`📝 Page content preview: ${pageText?.substring(0, 500)}...`);

    // Check for login/register buttons
    const loginVisible = await page
      .locator(
        'button:has-text("Login"), a:has-text("Login"), .btn:has-text("Login")'
      )
      .isVisible();
    const signUpVisible = await page
      .locator(
        'button:has-text("Sign Up"), a:has-text("Sign Up"), .btn:has-text("Sign Up")'
      )
      .isVisible();

    console.log(`🔐 Login button visible: ${loginVisible}`);
    console.log(`📝 Sign Up button visible: ${signUpVisible}`);

    // Check for dashboard/navigation elements
    const navElements = await page
      .locator("nav, .navbar, .nav-tabs, .tab-pane")
      .count();
    console.log(`🧭 Navigation elements found: ${navElements}`);

    // Check for any tabs or links that might be templates
    const allLinks = await page.locator("a, button").all();
    for (let i = 0; i < Math.min(allLinks.length, 10); i++) {
      const linkText = await allLinks[i].textContent();
      console.log(`🔗 Link ${i}: "${linkText}"`);
    }

    // Try to find any elements that might contain templates
    const cardElements = await page
      .locator(".card, .template, .item, .content")
      .count();
    console.log(`🃏 Card-like elements found: ${cardElements}`);

    // Take final screenshot
    await page.screenshot({
      path: "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/debug-final-page.png",
      fullPage: true,
    });
    console.log("📸 Final debug screenshot saved");
  });
});
