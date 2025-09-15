const { test, expect } = require("@playwright/test");

test.describe("Template Page Content Analysis", () => {
  test("should analyze current Template page structure and content", async ({
    page,
  }) => {
    console.log("🔍 ANALYZING CURRENT TEMPLATE PAGE STRUCTURE");

    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Authentication
    try {
      const signInButton = page.locator('button:has-text("Sign In")');
      if (await signInButton.isVisible({ timeout: 3000 })) {
        await page.fill('input[type="email"]', "jc@razorflow-ai.com");
        await page.fill('input[type="password"]', "securepassword123");
        await signInButton.click();
        await page.waitForTimeout(3000);
        console.log("✅ Authenticated successfully");
      }
    } catch (error) {
      console.log("✅ Already authenticated");
    }

    // Navigate to Templates
    try {
      await page.click("text=Templates", { timeout: 5000 });
    } catch (error) {
      await page.goto("http://localhost:3002/#templates");
    }
    await page.waitForTimeout(2000);
    console.log("✅ Navigated to Templates section");

    // Take screenshot
    await page.screenshot({
      path: "current-template-page.png",
      fullPage: true,
    });
    console.log("📸 Screenshot saved: current-template-page.png");

    // === ANALYZE PAGE STRUCTURE ===
    console.log("\n📋 CURRENT PAGE STRUCTURE ANALYSIS:");

    // Get all headings
    const headings = await page
      .locator("h1, h2, h3, h4, h5, h6")
      .allTextContents();
    console.log("📝 Headings found:");
    headings.forEach((heading, index) => {
      console.log(`   ${index + 1}. "${heading}"`);
    });

    // Get all buttons
    const buttons = await page.locator("button").allTextContents();
    console.log("\n🔘 Buttons found:");
    buttons.forEach((button, index) => {
      if (button.trim()) {
        console.log(`   ${index + 1}. "${button.trim()}"`);
      }
    });

    // Get all inputs
    const inputs = page.locator("input");
    const inputCount = await inputs.count();
    console.log(`\n📝 Input fields found: ${inputCount}`);
    for (let i = 0; i < inputCount; i++) {
      const placeholder = await inputs.nth(i).getAttribute("placeholder");
      const type = await inputs.nth(i).getAttribute("type");
      const id = await inputs.nth(i).getAttribute("id");
      const className = await inputs.nth(i).getAttribute("class");
      console.log(
        `   ${
          i + 1
        }. Type: ${type}, Placeholder: "${placeholder}", ID: "${id}", Class: "${className}"`
      );
    }

    // Get all cards/items
    const cardSelectors = [
      ".card",
      ".template-card",
      ".item",
      ".list-item",
      '[class*="card"]',
      '[class*="item"]',
    ];
    for (const selector of cardSelectors) {
      const elements = await page.locator(selector).count();
      if (elements > 0) {
        console.log(
          `\n🎴 Found ${elements} elements with selector: ${selector}`
        );
        const texts = await page.locator(selector).allTextContents();
        texts.slice(0, 3).forEach((text, index) => {
          if (text.trim()) {
            console.log(
              `   ${index + 1}. "${text.trim().substring(0, 100)}..."`
            );
          }
        });
      }
    }

    // Get page text content to analyze
    const bodyText = await page.textContent("body");

    // Look for key terms
    const keyTerms = [
      "Template",
      "Search",
      "Filter",
      "Library",
      "Create",
      "New",
      "Assistant",
      "MCP",
      "Personal",
      "Manager",
      "Support",
      "DevOps",
      "Analytics",
    ];

    console.log("\n🔍 KEY TERMS ANALYSIS:");
    keyTerms.forEach((term) => {
      const count = (bodyText.match(new RegExp(term, "gi")) || []).length;
      if (count > 0) {
        console.log(`   ✅ "${term}": found ${count} times`);
      } else {
        console.log(`   ⚠️ "${term}": not found`);
      }
    });

    // Check for form elements
    const forms = await page.locator("form").count();
    console.log(`\n📝 Forms found: ${forms}`);

    // Check for navigation elements
    const navElements = await page.locator("nav, .nav, .navigation").count();
    console.log(`🧭 Navigation elements: ${navElements}`);

    // Check for specific template creation elements
    const templateElements = [
      "text=Create Template",
      "text=New Template",
      "text=Template Builder",
      'button:has-text("Create")',
      'button:has-text("New")',
      'input[placeholder*="template"]',
      'input[placeholder*="name"]',
    ];

    console.log("\n🔨 TEMPLATE CREATION ELEMENTS:");
    for (const selector of templateElements) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        console.log(`   ✅ Found: ${selector} (${count} elements)`);
      }
    }

    // Final summary
    console.log("\n📊 TEMPLATE PAGE ANALYSIS SUMMARY:");
    console.log(
      "══════════════════════════════════════════════════════════════"
    );
    console.log(`📄 Page URL: ${page.url()}`);
    console.log(`📝 Total text length: ${bodyText.length} characters`);
    console.log(`🎯 Headings: ${headings.length}`);
    console.log(`🔘 Buttons: ${buttons.filter((b) => b.trim()).length}`);
    console.log(`📝 Input fields: ${inputCount}`);
    console.log(`📝 Forms: ${forms}`);
    console.log(`🧭 Navigation: ${navElements}`);
    console.log(
      "══════════════════════════════════════════════════════════════"
    );
    console.log("🎉 TEMPLATE PAGE ANALYSIS COMPLETE!");
  });
});
