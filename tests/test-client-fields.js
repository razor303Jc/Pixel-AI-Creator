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

    console.log("📄 Navigating to dashboard...");
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForTimeout(2000);

    console.log("🔘 Clicking Add Client button...");
    await page.click('button:has-text("Add Client")');
    await page.waitForTimeout(2000);

    console.log("📝 Filling form fields with correct mapping...");

    // Fill name field
    console.log("  - Filling name: Razor 303");
    await page.fill('input[placeholder*="Enter client name"]', "Razor 303");
    await page.waitForTimeout(500);

    // Fill email field
    console.log("  - Filling email: jc@razorflow-ai.com");
    await page.fill(
      'input[placeholder*="Enter email address"]',
      "jc@razorflow-ai.com"
    );
    await page.waitForTimeout(500);

    // Fill company field
    console.log("  - Filling company: RazorFlow-AI");
    await page.fill('input[placeholder*="Enter company name"]', "RazorFlow-AI");
    await page.waitForTimeout(500);

    // Fill description
    console.log("  - Filling description...");
    await page.fill(
      'textarea[placeholder*="description"]',
      "Leading AI solutions company"
    );
    await page.waitForTimeout(1000);

    // Check field values
    console.log("🔍 Checking filled values...");
    const nameValue = await page.inputValue(
      'input[placeholder*="Enter client name"]'
    );
    const emailValue = await page.inputValue(
      'input[placeholder*="Enter email address"]'
    );
    const companyValue = await page.inputValue(
      'input[placeholder*="Enter company name"]'
    );

    console.log("  - Name field:", nameValue);
    console.log("  - Email field:", emailValue);
    console.log("  - Company field:", companyValue);

    // Check submit button
    const submitButton = page.locator('button:has-text("Create Client")');
    const isEnabled = await submitButton.isEnabled();
    console.log("🔘 Submit button enabled:", isEnabled);

    if (isEnabled) {
      console.log("✅ Form validation passed - clicking submit...");
      await submitButton.click();
      await page.waitForTimeout(3000);
      console.log("✅ Client creation completed!");
    } else {
      console.log("❌ Form validation failed - submit button disabled");
    }
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await browser.close();
  }
})();
