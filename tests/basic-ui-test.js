const { chromium } = require("playwright");

async function testFrontendUI() {
  console.log("🚀 Starting Frontend UI Test...");

  // Launch browser
  const browser = await chromium.launch({
    headless: false,
    slowMo: 1000, // Slow down actions for demo
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to frontend
    console.log("📍 Navigating to http://localhost:3002");
    await page.goto("http://localhost:3002");

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Get page title
    const title = await page.title();
    console.log(`📄 Page Title: ${title}`);

    // Check if this is the Pixel AI Creator
    if (title.includes("Pixel AI Creator")) {
      console.log("✅ Frontend is loading correctly!");
    } else {
      console.log("❌ Unexpected page title");
    }

    // Take a screenshot
    await page.screenshot({ path: "frontend-test.png", fullPage: true });
    console.log("📸 Screenshot saved as frontend-test.png");

    // Look for key elements
    const bodyText = await page.textContent("body");

    if (bodyText.includes("Pixel AI Creator")) {
      console.log("✅ Main heading found");
    }

    // Check for forms or input elements
    const inputs = await page.$$("input");
    console.log(`🔍 Found ${inputs.length} input elements`);

    const buttons = await page.$$("button");
    console.log(`🔘 Found ${buttons.length} button elements`);

    // Wait a bit to see the page
    console.log("⏳ Displaying page for 5 seconds...");
    await page.waitForTimeout(5000);

    console.log("✅ Frontend UI Test Completed Successfully!");
  } catch (error) {
    console.error("❌ Test Error:", error.message);
  } finally {
    await browser.close();
  }
}

// Run the test
testFrontendUI().catch(console.error);
