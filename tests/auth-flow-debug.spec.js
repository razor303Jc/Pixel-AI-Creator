const { test, expect } = require("@playwright/test");

test.describe("Authentication Flow Debug", () => {
  test("should debug authentication and post-login navigation", async ({
    page,
  }) => {
    console.log("🔍 Debugging authentication flow...");

    // Listen to network requests
    page.on("request", (request) => {
      if (request.url().includes("/api/") || request.url().includes("/auth")) {
        console.log(`📡 Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on("response", (response) => {
      if (
        response.url().includes("/api/") ||
        response.url().includes("/auth")
      ) {
        console.log(`📡 Response: ${response.status()} ${response.url()}`);
      }
    });

    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    console.log(`🌐 Initial URL: ${page.url()}`);
    await page.screenshot({ path: "auth-debug-1-initial.png", fullPage: true });

    // Check what's on the initial page
    const pageText = await page.textContent("body");
    console.log(
      `📄 Page contains login form: ${
        pageText.includes("email") && pageText.includes("password")
      }`
    );

    // Try to log in
    console.log("\n🔐 Attempting login...");

    try {
      const emailField = page.locator(
        'input[type="email"], input[name="email"]'
      );
      const passwordField = page.locator(
        'input[type="password"], input[name="password"]'
      );
      const signInButton = page.locator('button:has-text("Sign In")');

      if (await emailField.isVisible({ timeout: 5000 })) {
        console.log("✅ Found email field");
        await emailField.fill("jc@razorflow-ai.com");

        if (await passwordField.isVisible()) {
          console.log("✅ Found password field");
          await passwordField.fill("securepassword123");

          if (await signInButton.isVisible()) {
            console.log("✅ Found sign in button, clicking...");
            await signInButton.click();

            // Wait for any navigation or response
            await page.waitForTimeout(5000);

            console.log(`🌐 URL after login attempt: ${page.url()}`);
            await page.screenshot({
              path: "auth-debug-2-after-login.png",
              fullPage: true,
            });

            // Check if we're redirected
            if (
              page.url() !== "http://localhost:3002" &&
              !page.url().includes("/login")
            ) {
              console.log("✅ Redirected after login");
            } else {
              console.log("⚠️ Still on login page or no redirect");

              // Check for error messages
              const errorMessages = await page
                .locator(".alert-danger, .error, .text-danger")
                .all();
              if (errorMessages.length > 0) {
                for (const error of errorMessages) {
                  const errorText = await error.textContent();
                  console.log(`❌ Login error: ${errorText}`);
                }
              }
            }

            // Check what navigation is available now
            const navElements = await page
              .locator("a, button, .nav-link")
              .all();
            console.log(
              `\n🧭 Available navigation after login (${navElements.length} elements):`
            );

            for (let i = 0; i < Math.min(navElements.length, 10); i++) {
              try {
                const text = await navElements[i].textContent();
                const href = await navElements[i].getAttribute("href");
                const tagName = await navElements[i].evaluate(
                  (el) => el.tagName
                );

                if (text && text.trim()) {
                  console.log(
                    `   ${i + 1}. ${tagName}: "${text.trim()}" ${
                      href ? `(href: ${href})` : ""
                    }`
                  );
                }
              } catch (e) {
                // Skip problematic elements
              }
            }

            // Try to navigate to different sections that might exist
            const sectionsToTry = [
              "Dashboard",
              "Build Status",
              "Assistants",
              "Projects",
              "Templates",
              "Settings",
            ];

            console.log("\n🎯 Trying to navigate to main sections...");
            for (const section of sectionsToTry) {
              try {
                const sectionElement = page.locator(`text="${section}"`);
                if (await sectionElement.isVisible({ timeout: 2000 })) {
                  console.log(`✅ Found ${section} navigation`);
                  await sectionElement.click();
                  await page.waitForTimeout(2000);

                  const newUrl = page.url();
                  const newPageText = await page.textContent("body");

                  console.log(`   URL: ${newUrl}`);
                  console.log(
                    `   Contains "Create Assistant": ${newPageText.includes(
                      "Create Assistant"
                    )}`
                  );
                  console.log(
                    `   Contains "Build Status": ${newPageText.includes(
                      "Build Status"
                    )}`
                  );

                  if (newPageText.includes("Create Assistant")) {
                    console.log(
                      "🎯 Found main dashboard with Create Assistant!"
                    );
                    await page.screenshot({
                      path: `auth-debug-3-found-${section.toLowerCase()}.png`,
                      fullPage: true,
                    });

                    // Now test creating an assistant with auto-build
                    await page.click('button:has-text("Create Assistant")');
                    await page.waitForSelector(".modal.show", {
                      timeout: 5000,
                    });

                    await page.screenshot({
                      path: "auth-debug-4-create-modal.png",
                      fullPage: true,
                    });

                    // Check if auto-build option exists
                    const autoBuildCheckbox = page.locator(
                      '#auto-build-checkbox, input[type="checkbox"]'
                    );
                    const checkboxCount = await autoBuildCheckbox.count();
                    console.log(
                      `🔘 Found ${checkboxCount} checkboxes in create form`
                    );

                    for (let i = 0; i < checkboxCount; i++) {
                      const label = await page
                        .locator("label")
                        .nth(i)
                        .textContent();
                      console.log(`   Checkbox ${i + 1}: ${label}`);
                    }

                    break;
                  }
                } else {
                  console.log(`❌ ${section} navigation not found`);
                }
              } catch (e) {
                console.log(`⚠️ Error testing ${section}: ${e.message}`);
              }
            }
          } else {
            console.log("❌ Sign in button not found");
          }
        } else {
          console.log("❌ Password field not found");
        }
      } else {
        console.log("❌ Email field not found");
      }
    } catch (error) {
      console.log(`❌ Login error: ${error.message}`);
    }

    // Final state
    await page.screenshot({
      path: "auth-debug-5-final-state.png",
      fullPage: true,
    });
    console.log(`🌐 Final URL: ${page.url()}`);
  });
});
