const { test, expect } = require("@playwright/test");

test.describe("Working Build Status Navigation", () => {
  test("should properly navigate to Build Status and test functionality", async ({
    page,
  }) => {
    console.log("🔍 Testing Build Status with working navigation patterns...");

    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // === AUTHENTICATION (using working pattern) ===
    console.log("\n🔐 STEP 1: Authentication");
    try {
      const signInButton = page.locator('button:has-text("Sign In")');
      if (await signInButton.isVisible({ timeout: 3000 })) {
        await page.fill('input[type="email"]', "jc@razorflow-ai.com");
        await page.fill('input[type="password"]', "securepassword123");
        await signInButton.click();
        await page.waitForTimeout(3000);
        console.log("✅ User authenticated successfully");
      } else {
        console.log("✅ User already authenticated");
      }
    } catch (error) {
      console.log("✅ User already authenticated - continuing");
    }

    // Take screenshot to see current state
    await page.screenshot({
      path: "working-test-after-login.png",
      fullPage: true,
    });

    // === TRY VARIOUS NAVIGATION METHODS ===
    console.log("\n🧭 STEP 2: Attempting to navigate to Build Status");

    const navigationAttempts = [
      { method: 'text="Build Status"', description: "Text-based navigation" },
      {
        method: '[data-testid="nav-build-status"]',
        description: "Data testid navigation",
      },
      { method: 'text="Build"', description: "Partial text navigation" },
      { method: 'a:has-text("Build Status")', description: "Link with text" },
      {
        method: 'button:has-text("Build Status")',
        description: "Button with text",
      },
      {
        method: '.nav-link:has-text("Build")',
        description: "Nav link with Build text",
      },
      {
        method: 'text="Dashboard"',
        description: "Navigate to Dashboard first",
      },
    ];

    let buildStatusFound = false;

    for (const attempt of navigationAttempts) {
      try {
        const element = page.locator(attempt.method);
        if (await element.isVisible({ timeout: 2000 })) {
          console.log(`✅ Found element: ${attempt.description}`);
          await element.click();
          await page.waitForTimeout(2000);

          // Check if we're on a build-related page
          const pageContent = await page.textContent("body");
          if (
            pageContent.includes("Build Status") ||
            pageContent.includes("Build Dashboard")
          ) {
            console.log(
              `🎯 Successfully navigated using: ${attempt.description}`
            );
            buildStatusFound = true;
            break;
          } else if (pageContent.includes("Dashboard")) {
            console.log(
              `📋 On Dashboard page, looking for Build Status from here...`
            );

            // From dashboard, try to find Build Status
            const buildStatusFromDashboard = [
              'text="Build Status"',
              '[data-testid="nav-build-status"]',
              'button:has-text("Build")',
              '.nav-link:has-text("Build")',
              '.tab:has-text("Build")',
              '.nav-item:has-text("Build")',
            ];

            for (const dashboardAttempt of buildStatusFromDashboard) {
              try {
                const dashElement = page.locator(dashboardAttempt);
                if (await dashElement.isVisible({ timeout: 2000 })) {
                  console.log(
                    `✅ Found Build Status from Dashboard: ${dashboardAttempt}`
                  );
                  await dashElement.click();
                  await page.waitForTimeout(2000);

                  const newPageContent = await page.textContent("body");
                  if (
                    newPageContent.includes("Build Status") ||
                    newPageContent.includes("Build Dashboard")
                  ) {
                    console.log(
                      `🎯 Successfully found Build Status from Dashboard!`
                    );
                    buildStatusFound = true;
                    break;
                  }
                }
              } catch (e) {
                // Continue to next attempt
              }
            }

            if (buildStatusFound) break;
          }
        }
      } catch (error) {
        // Continue to next attempt
      }
    }

    if (!buildStatusFound) {
      // Check all available navigation options
      console.log("\n🔍 STEP 3: Analyzing available navigation options");

      // Look for all clickable elements that might be navigation
      const clickableElements = await page
        .locator('a, button, .nav-link, .nav-item, [role="tab"]')
        .all();
      console.log(`Found ${clickableElements.length} clickable elements`);

      const navigationOptions = [];
      for (let i = 0; i < Math.min(clickableElements.length, 20); i++) {
        try {
          const text = await clickableElements[i].textContent();
          const tagName = await clickableElements[i].evaluate(
            (el) => el.tagName
          );
          const className = await clickableElements[i].evaluate(
            (el) => el.className
          );

          if (text && text.trim().length > 0 && text.length < 50) {
            navigationOptions.push(`${tagName}.${className}: "${text.trim()}"`);
          }
        } catch (e) {
          // Skip elements that can't be accessed
        }
      }

      console.log("📋 Available navigation options:");
      navigationOptions.forEach((option, index) => {
        console.log(`   ${index + 1}. ${option}`);
      });

      // Try to create an assistant with auto-build to test the feature
      console.log(
        "\n🤖 STEP 4: Testing assistant creation with auto-build (alternate approach)"
      );

      try {
        // Look for Create Assistant button
        const createButton = page.locator(
          'button:has-text("Create Assistant"), button:has-text("Create")'
        );
        if (await createButton.isVisible({ timeout: 5000 })) {
          console.log("✅ Found Create Assistant button");
          await createButton.click();
          await page.waitForSelector(".modal.show", { timeout: 5000 });

          // Fill out the form
          const assistantName = `Build Test ${Date.now()}`;
          await page.fill(
            'input[placeholder*="name"], input[name="name"]',
            assistantName
          );
          await page.fill(
            'textarea[placeholder*="description"], textarea[name="description"]',
            "Testing build functionality"
          );

          // Look for auto-build checkbox
          const autoBuildCheckbox = page.locator(
            '#auto-build-checkbox, input[type="checkbox"]:has-text("auto"), input[type="checkbox"]:has-text("build")'
          );
          if (await autoBuildCheckbox.isVisible({ timeout: 3000 })) {
            console.log("✅ Found auto-build checkbox");
            await autoBuildCheckbox.check();
            console.log("✅ Auto-build enabled");
          } else {
            console.log("⚠️ Auto-build checkbox not found");
          }

          // Submit the form
          const submitButton = page.locator(
            'button:has-text("Create"), button[type="submit"]'
          );
          await submitButton.click();
          await page.waitForSelector(".modal.show", {
            state: "hidden",
            timeout: 10000,
          });

          console.log("✅ Assistant creation attempted");

          // Wait for success message
          await page.waitForTimeout(3000);

          // Take screenshot
          await page.screenshot({
            path: "assistant-created-for-build-test.png",
            fullPage: true,
          });

          // Check for success/error messages
          const messages = await page.locator(".toast, .alert, .message").all();
          for (const message of messages) {
            const text = await message.textContent();
            if (text && text.trim()) {
              console.log(`📢 Message: ${text.trim()}`);
            }
          }
        } else {
          console.log("❌ Create Assistant button not found");
        }
      } catch (error) {
        console.log(`⚠️ Error creating assistant: ${error.message}`);
      }
    }

    // === FINAL ANALYSIS ===
    console.log("\n📊 STEP 5: Final Build Status Analysis");

    if (buildStatusFound) {
      console.log("🎯 Build Status page accessed successfully!");

      // Take screenshot of Build Status page
      await page.screenshot({
        path: "build-status-page-found.png",
        fullPage: true,
      });

      // Check for build content
      const buildCards = await page.locator(".card").count();
      console.log(`📊 Found ${buildCards} build cards`);

      // Check for error messages
      const errorMessages = await page.locator(".alert-danger").count();
      if (errorMessages > 0) {
        console.log(
          `❌ Found ${errorMessages} error messages on Build Status page`
        );
        const firstError = await page
          .locator(".alert-danger")
          .first()
          .textContent();
        console.log(`   Error: ${firstError}`);
      }

      // Check for empty state
      const emptyState = await page.locator(".alert-info").count();
      if (emptyState > 0) {
        const emptyMessage = await page
          .locator(".alert-info")
          .first()
          .textContent();
        console.log(`ℹ️ Empty state message: ${emptyMessage}`);
      }
    } else {
      console.log(
        "❌ Build Status page not accessible through standard navigation"
      );
      console.log(
        "💡 This suggests the Build Status feature may not be properly integrated into the navigation"
      );
    }

    // Final screenshot
    await page.screenshot({
      path: "final-build-status-investigation.png",
      fullPage: true,
    });
  });
});
