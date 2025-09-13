const { chromium } = require("playwright");

async function comprehensiveFrontendUITest() {
  console.log("🚀 Starting Comprehensive Frontend UI Flow Test...");
  console.log("📋 This test will demonstrate:");
  console.log("   - Page loading and navigation");
  console.log("   - Form interactions");
  console.log("   - Button clicks");
  console.log("   - Input field testing");
  console.log("   - UI responsiveness");
  console.log("");

  // Launch browser with visible UI
  const browser = await chromium.launch({
    headless: false,
    slowMo: 1500, // Slow down for demo
    args: ["--start-maximized"],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const page = await context.newPage();

  try {
    console.log("🌐 Step 1: Loading Frontend Application");
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Verify page loaded
    const title = await page.title();
    console.log(`   ✅ Page loaded: ${title}`);

    console.log("");
    console.log("🔍 Step 2: Analyzing Page Structure");

    // Check main elements
    const headings = await page.$$("h1, h2, h3, h4, h5, h6");
    console.log(`   📝 Found ${headings.length} headings`);

    const inputs = await page.$$("input");
    console.log(`   📝 Found ${inputs.length} input fields`);

    const buttons = await page.$$("button");
    console.log(`   📝 Found ${buttons.length} buttons`);

    const forms = await page.$$("form");
    console.log(`   📝 Found ${forms.length} forms`);

    // Take initial screenshot
    await page.screenshot({
      path: "ui-test-step1-initial.png",
      fullPage: true,
    });
    console.log("   📸 Screenshot saved: ui-test-step1-initial.png");

    console.log("");
    console.log("🖱️  Step 3: Testing Interactive Elements");

    // Find and test inputs
    const allInputs = await page.$$("input");
    for (let i = 0; i < Math.min(allInputs.length, 3); i++) {
      try {
        const input = allInputs[i];
        const inputType = (await input.getAttribute("type")) || "text";
        const placeholder = (await input.getAttribute("placeholder")) || "";

        console.log(
          `   🔤 Testing input ${
            i + 1
          }: type="${inputType}", placeholder="${placeholder}"`
        );

        await input.click();
        await page.waitForTimeout(500);

        if (inputType === "text" || inputType === "email" || !inputType) {
          await input.fill("Test input data");
          console.log(`      ✅ Successfully filled input ${i + 1}`);
        } else if (inputType === "password") {
          await input.fill("testpassword123");
          console.log(`      ✅ Successfully filled password input ${i + 1}`);
        }

        await page.waitForTimeout(500);
      } catch (error) {
        console.log(
          `      ⚠️  Could not interact with input ${i + 1}: ${error.message}`
        );
      }
    }

    // Take screenshot after input testing
    await page.screenshot({ path: "ui-test-step2-inputs.png", fullPage: true });
    console.log("   📸 Screenshot saved: ui-test-step2-inputs.png");

    console.log("");
    console.log("🔘 Step 4: Testing Button Interactions");

    // Test buttons
    const allButtons = await page.$$("button");
    for (let i = 0; i < Math.min(allButtons.length, 3); i++) {
      try {
        const button = allButtons[i];
        const buttonText = await button.textContent();
        const isVisible = await button.isVisible();
        const isEnabled = await button.isEnabled();

        console.log(
          `   🔘 Button ${
            i + 1
          }: "${buttonText?.trim()}" - Visible: ${isVisible}, Enabled: ${isEnabled}`
        );

        if (isVisible && isEnabled) {
          // Hover over button first
          await button.hover();
          await page.waitForTimeout(500);

          // Click button (but be careful not to submit forms)
          if (
            !buttonText?.toLowerCase().includes("submit") &&
            !buttonText?.toLowerCase().includes("send") &&
            !buttonText?.toLowerCase().includes("create")
          ) {
            await button.click();
            console.log(
              `      ✅ Successfully clicked button: "${buttonText?.trim()}"`
            );
            await page.waitForTimeout(1000);
          } else {
            console.log(
              `      ⚠️  Skipped clicking submit/send button: "${buttonText?.trim()}"`
            );
          }
        }
      } catch (error) {
        console.log(
          `      ⚠️  Could not interact with button ${i + 1}: ${error.message}`
        );
      }
    }

    // Take screenshot after button testing
    await page.screenshot({
      path: "ui-test-step3-buttons.png",
      fullPage: true,
    });
    console.log("   📸 Screenshot saved: ui-test-step3-buttons.png");

    console.log("");
    console.log("📱 Step 5: Testing Responsive Design");

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    console.log("   📱 Switched to mobile viewport (375x667)");

    await page.screenshot({ path: "ui-test-step4-mobile.png", fullPage: true });
    console.log("   📸 Mobile screenshot saved: ui-test-step4-mobile.png");

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    console.log("   📱 Switched to tablet viewport (768x1024)");

    await page.screenshot({ path: "ui-test-step5-tablet.png", fullPage: true });
    console.log("   📸 Tablet screenshot saved: ui-test-step5-tablet.png");

    // Back to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    console.log("   🖥️  Switched back to desktop viewport");

    console.log("");
    console.log("🔍 Step 6: Content Analysis");

    // Analyze page content
    const bodyText = await page.textContent("body");
    const wordCount = bodyText.split(/\s+/).length;
    console.log(`   📊 Page contains approximately ${wordCount} words`);

    // Check for common UI patterns
    const navElements = await page.$$("nav, .nav, .navbar, .navigation");
    console.log(`   🧭 Found ${navElements.length} navigation elements`);

    const linkElements = await page.$$("a");
    console.log(`   🔗 Found ${linkElements.length} links`);

    const imgElements = await page.$$("img");
    console.log(`   🖼️  Found ${imgElements.length} images`);

    console.log("");
    console.log("⏱️  Step 7: Performance Check");

    // Measure page load performance
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType("navigation")[0];
      return {
        domContentLoaded: Math.round(
          navigation.domContentLoadedEventEnd -
            navigation.domContentLoadedEventStart
        ),
        loadComplete: Math.round(
          navigation.loadEventEnd - navigation.loadEventStart
        ),
        totalLoadTime: Math.round(
          navigation.loadEventEnd - navigation.fetchStart
        ),
      };
    });

    console.log(
      `   ⚡ DOM Content Loaded: ${performanceMetrics.domContentLoaded}ms`
    );
    console.log(`   ⚡ Load Complete: ${performanceMetrics.loadComplete}ms`);
    console.log(`   ⚡ Total Load Time: ${performanceMetrics.totalLoadTime}ms`);

    // Final screenshot
    await page.screenshot({ path: "ui-test-final.png", fullPage: true });
    console.log("   📸 Final screenshot saved: ui-test-final.png");

    console.log("");
    console.log("⏳ Displaying final state for 3 seconds...");
    await page.waitForTimeout(3000);

    console.log("");
    console.log("🎉 COMPREHENSIVE UI FLOW TEST COMPLETED SUCCESSFULLY!");
    console.log("");
    console.log("📊 Test Summary:");
    console.log(`   ✅ Page loaded successfully: ${title}`);
    console.log(`   ✅ Found ${inputs.length} input fields`);
    console.log(`   ✅ Found ${buttons.length} buttons`);
    console.log(`   ✅ Tested responsive design (mobile/tablet/desktop)`);
    console.log(`   ✅ Performance metrics captured`);
    console.log(`   ✅ 6 screenshots saved for visual verification`);
    console.log("");
    console.log("🖼️  Screenshots saved:");
    console.log("   - ui-test-step1-initial.png (Initial page load)");
    console.log("   - ui-test-step2-inputs.png (After input testing)");
    console.log("   - ui-test-step3-buttons.png (After button testing)");
    console.log("   - ui-test-step4-mobile.png (Mobile view)");
    console.log("   - ui-test-step5-tablet.png (Tablet view)");
    console.log("   - ui-test-final.png (Final desktop view)");
  } catch (error) {
    console.error("❌ Test Error:", error.message);
    console.error("Stack trace:", error.stack);
  } finally {
    await browser.close();
    console.log("🏁 Browser closed. Test complete.");
  }
}

// Run the comprehensive test
comprehensiveFrontendUITest().catch(console.error);
