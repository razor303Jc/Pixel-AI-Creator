const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const page = await browser.newPage();

  try {
    console.log("🌐 Navigating to application...");
    await page.goto("http://localhost:3002");
    await page.waitForTimeout(3000);

    console.log("📝 Logging in...");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000);

    console.log("📄 Current page URL:", page.url());
    console.log("📄 Page title:", await page.title());

    // Check for Add Client button
    const addClientButtons = await page
      .locator('button:has-text("Add Client")')
      .count();
    console.log("🔍 Add Client buttons found:", addClientButtons);

    if (addClientButtons === 0) {
      // Check for other client-related buttons
      const clientButtons = await page
        .locator("button")
        .filter({ hasText: /client/i })
        .count();
      console.log("🔍 Client-related buttons found:", clientButtons);

      // Check all button texts
      const buttons = await page.locator("button").all();
      console.log("🔘 All buttons on page:");
      for (let i = 0; i < Math.min(buttons.length, 10); i++) {
        const text = await buttons[i].textContent();
        if (text && text.trim()) {
          console.log(`  - "${text.trim()}"`);
        }
      }
    }

    await page.waitForTimeout(5000);
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await browser.close();
  }
})();
