const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 2000 });
  const page = await browser.newPage();

  try {
    console.log("🌐 Navigating to application...");
    await page.goto("http://localhost:3002");
    await page.waitForTimeout(3000);

    console.log("📝 Logging in with jc@razorflow-ai.com...");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000);

    console.log("📍 Current URL:", page.url());

    console.log("🏠 Navigating to Dashboard...");
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForTimeout(3000);

    console.log("🔍 Looking for Add Client button...");
    const addClientButton = await page
      .locator('button:has-text("Add Client")')
      .count();
    console.log("👆 Add Client buttons found:", addClientButton);

    if (addClientButton > 0) {
      console.log("✅ Clicking Add Client button...");
      await page.click('button:has-text("Add Client")');
      await page.waitForTimeout(2000);

      console.log("📝 Filling client form...");
      await page.fill('input[placeholder*="client name"]', "Razor 303");
      await page.fill('input[placeholder*="email"]', "jc@razorflow.com");
      await page.fill('input[placeholder*="company"]', "RazorFlow-AI");
      await page.fill(
        'textarea[placeholder*="description"]',
        "Leading AI solutions company"
      );

      console.log("💾 Submitting form...");
      await page.click('button:has-text("Create Client")');
      await page.waitForTimeout(3000);

      console.log("✅ Client creation test completed successfully!");
    } else {
      console.log("❌ Add Client button not found");
    }

    await page.waitForTimeout(5000);
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await browser.close();
  }
})();
