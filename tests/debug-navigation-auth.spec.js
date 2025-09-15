const { test, expect } = require("@playwright/test");

test.describe("Detailed Navigation and Authentication Test", () => {
  test("should debug navigation and authentication flow", async ({ page }) => {
    console.log("🔍 DETAILED NAVIGATION AND AUTHENTICATION DEBUG");

    // Step 1: Go to homepage
    console.log("\n📍 STEP 1: Navigate to homepage");
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    let currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);

    // Take initial screenshot
    await page.screenshot({ path: "debug-1-homepage.png", fullPage: true });
    console.log("   📸 Screenshot: debug-1-homepage.png");

    // Check what's on the page initially
    const pageTitle = await page.title();
    console.log(`   Page title: "${pageTitle}"`);

    const bodyText = await page.textContent("body");
    const hasSignIn = bodyText?.includes("Sign In");
    const hasDashboard = bodyText?.includes("Dashboard");
    console.log(`   Has "Sign In": ${hasSignIn}`);
    console.log(`   Has "Dashboard": ${hasDashboard}`);

    // Step 2: Attempt authentication
    console.log("\n🔐 STEP 2: Authentication process");

    try {
      const signInButton = page.locator('button:has-text("Sign In")');
      const isSignInVisible = await signInButton.isVisible({ timeout: 3000 });
      console.log(`   Sign In button visible: ${isSignInVisible}`);

      if (isSignInVisible) {
        console.log("   Attempting to sign in...");

        // Fill credentials
        await page.fill('input[type="email"]', "jc@razorflow-ai.com");
        await page.fill('input[type="password"]', "securepassword123");
        console.log("   ✅ Credentials entered");

        // Click sign in
        await signInButton.click();
        await page.waitForTimeout(3000);
        await page.waitForLoadState("networkidle");
        console.log("   ✅ Sign in button clicked");

        // Check new URL and content
        currentUrl = page.url();
        console.log(`   New URL after sign in: ${currentUrl}`);

        await page.screenshot({
          path: "debug-2-after-signin.png",
          fullPage: true,
        });
        console.log("   📸 Screenshot: debug-2-after-signin.png");

        const newBodyText = await page.textContent("body");
        const newHasSignIn = newBodyText?.includes("Sign In");
        const newHasDashboard = newBodyText?.includes("Dashboard");
        const hasTemplates = newBodyText?.includes("Templates");
        console.log(`   Still has "Sign In": ${newHasSignIn}`);
        console.log(`   Now has "Dashboard": ${newHasDashboard}`);
        console.log(`   Has "Templates": ${hasTemplates}`);
      } else {
        console.log(
          "   Sign In button not visible - user may already be authenticated"
        );
      }
    } catch (error) {
      console.log(`   Authentication error: ${error.message}`);
    }

    // Step 3: Check navigation options
    console.log("\n🧭 STEP 3: Navigation options analysis");

    // Look for navigation links
    const navLinks = await page.locator("a, button").allTextContents();
    console.log("   Available navigation options:");
    navLinks.forEach((text, index) => {
      if (text.trim() && text.length < 50) {
        console.log(`      ${index + 1}. "${text.trim()}"`);
      }
    });

    // Look specifically for Dashboard or Templates links
    const dashboardLink = page.locator("text=Dashboard");
    const templatesLink = page.locator("text=Templates");
    const dashboardCount = await dashboardLink.count();
    const templatesCount = await templatesLink.count();

    console.log(`   Dashboard links found: ${dashboardCount}`);
    console.log(`   Templates links found: ${templatesCount}`);

    // Step 4: Try to navigate to templates
    console.log("\n📚 STEP 4: Navigate to Templates");

    let templatesAccessible = false;

    // Method 1: Click Templates link if available
    if (templatesCount > 0) {
      try {
        await templatesLink.first().click();
        await page.waitForTimeout(2000);
        templatesAccessible = true;
        console.log("   ✅ Clicked Templates link");
      } catch (error) {
        console.log(`   ❌ Error clicking Templates link: ${error.message}`);
      }
    }

    // Method 2: Try direct URL navigation
    if (!templatesAccessible) {
      try {
        await page.goto("http://localhost:3002/#templates");
        await page.waitForTimeout(2000);
        templatesAccessible = true;
        console.log("   ✅ Direct navigation to templates");
      } catch (error) {
        console.log(`   ❌ Error with direct navigation: ${error.message}`);
      }
    }

    // Method 3: Try dashboard first, then templates
    if (!templatesAccessible && dashboardCount > 0) {
      try {
        await dashboardLink.first().click();
        await page.waitForTimeout(2000);

        // Now look for templates from dashboard
        const templatesFromDash = page.locator("text=Templates");
        if ((await templatesFromDash.count()) > 0) {
          await templatesFromDash.first().click();
          await page.waitForTimeout(2000);
          templatesAccessible = true;
          console.log("   ✅ Accessed Templates via Dashboard");
        }
      } catch (error) {
        console.log(`   ❌ Error accessing via Dashboard: ${error.message}`);
      }
    }

    // Step 5: Analyze final state
    console.log("\n📊 STEP 5: Final state analysis");

    currentUrl = page.url();
    console.log(`   Final URL: ${currentUrl}`);

    await page.screenshot({ path: "debug-3-final-state.png", fullPage: true });
    console.log("   📸 Final screenshot: debug-3-final-state.png");

    const finalBodyText = await page.textContent("body");
    const hasCreateTemplate = finalBodyText
      ?.toLowerCase()
      .includes("create template");
    const hasTemplateContent = finalBodyText
      ?.toLowerCase()
      .includes("template");
    const hasWelcomeBack = finalBodyText?.includes("Welcome Back");

    console.log(`   Has "Create Template": ${hasCreateTemplate}`);
    console.log(`   Has template content: ${hasTemplateContent}`);
    console.log(`   Has "Welcome Back": ${hasWelcomeBack}`);

    // Check all buttons in final state
    const finalButtons = await page.locator("button").allTextContents();
    console.log("   Final buttons available:");
    finalButtons.forEach((text, index) => {
      if (text.trim()) {
        console.log(`      ${index + 1}. "${text.trim()}"`);
      }
    });

    // Step 6: Summary and recommendations
    console.log("\n🏁 STEP 6: Summary and recommendations");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    if (templatesAccessible) {
      console.log("✅ TEMPLATES SECTION: ACCESSIBLE");
      if (hasCreateTemplate) {
        console.log("✅ CREATE TEMPLATE FUNCTIONALITY: AVAILABLE");
      } else {
        console.log("⚠️ CREATE TEMPLATE FUNCTIONALITY: NOT VISIBLE");
        console.log("   💡 Possible solutions:");
        console.log("      • Check user permissions");
        console.log("      • Look for different template creation method");
        console.log("      • Verify authentication level");
      }
    } else {
      console.log("❌ TEMPLATES SECTION: NOT ACCESSIBLE");
      console.log("   💡 Possible solutions:");
      console.log("      • Verify authentication is working");
      console.log("      • Check if user has template access permissions");
      console.log("      • Try alternative navigation paths");
    }

    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });
});
