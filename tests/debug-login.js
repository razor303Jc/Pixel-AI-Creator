const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // Navigate to the application
    console.log("Navigating to http://localhost:3002");
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    console.log("Current URL:", page.url());
    console.log("Page title:", await page.title());

    // Check if login form is present
    const emailField = await page.locator("#loginEmail").isVisible();
    const passwordField = await page.locator("#loginPassword").isVisible();
    console.log("Email field visible:", emailField);
    console.log("Password field visible:", passwordField);

    if (emailField && passwordField) {
      console.log("Attempting login...");

      // Login with test user
      await page.fill("#loginEmail", "jc@razorflow-ai.com");
      await page.fill("#loginPassword", "Password123!");
      await page.click('button[type="submit"]');

      // Wait for page to load after login
      await page.waitForTimeout(5000);

      console.log("After login URL:", page.url());
      console.log("After login title:", await page.title());

      // Check if there are any error messages
      const errorAlerts = await page
        .locator(".alert-danger, .alert-error")
        .all();
      if (errorAlerts.length > 0) {
        console.log("Found error alerts:");
        for (let alert of errorAlerts) {
          const text = await alert.textContent();
          console.log("- Error:", text);
        }
      }

      // Check if we're redirected to dashboard
      const isDashboard =
        page.url().includes("dashboard") ||
        (await page.locator('[data-testid*="dashboard"]').isVisible());
      console.log("Is dashboard visible:", isDashboard);
    } else {
      console.log("Login form not found - checking if already logged in");
    }

    // Take a screenshot
    await page.screenshot({ path: "current-page.png", fullPage: true });

    // Log all visible elements with text
    const allElements = await page.locator("*").all();
    console.log(`Found ${allElements.length} total elements`);

    // Log navigation elements specifically
    const navElements = await page
      .locator('nav, .navbar, [class*="nav"]')
      .all();
    console.log(`Found ${navElements.length} navigation elements`);

    for (let i = 0; i < navElements.length; i++) {
      const text = await navElements[i].textContent();
      const className = await navElements[i].getAttribute("class");
      console.log(`Nav ${i}: "${text}" (class: ${className})`);
    }

    // Log all visible text content
    const bodyText = await page.locator("body").textContent();
    if (bodyText) {
      console.log("Page content preview:", bodyText.substring(0, 500));
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    await browser.close();
  }
})();
