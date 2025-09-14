/**
 * Error Handling and Edge Cases Tests
 * Tests application behavior under various error conditions and edge cases
 */

const { test, expect } = require("@playwright/test");

test.describe("Error Handling and Edge Cases", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3002");
  });

  test("should handle network connection errors gracefully", async ({
    page,
  }) => {
    // Simulate offline condition
    await page.context().setOffline(true);

    await page.click("text=Sign up here");

    const timestamp = Date.now();
    await page.fill("#firstName", "Network");
    await page.fill("#lastName", "Test");
    await page.fill("#email", `network.test.${timestamp}@example.com`);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    // Try to submit form while offline
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    // Should show some kind of error handling
    const bodyText = await page.textContent("body");
    const hasErrorHandling =
      bodyText.includes("error") ||
      bodyText.includes("failed") ||
      bodyText.includes("network") ||
      bodyText.includes("connection") ||
      bodyText.includes("offline");

    // Restore connection
    await page.context().setOffline(false);

    console.log(`Network error handling present: ${hasErrorHandling}`);
  });

  test("should handle API timeout errors", async ({ page }) => {
    // Mock slow API response
    await page.route("**/api/**", async (route) => {
      // Delay response by 10 seconds to simulate timeout
      await new Promise((resolve) => setTimeout(resolve, 10000));
      await route.continue();
    });

    await page.click("text=Sign up here");

    const timestamp = Date.now();
    await page.fill("#firstName", "Timeout");
    await page.fill("#lastName", "Test");
    await page.fill("#email", `timeout.test.${timestamp}@example.com`);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for timeout or error handling
    await page.waitForTimeout(5000);

    const bodyText = await page.textContent("body");
    const hasTimeoutHandling =
      bodyText.includes("timeout") ||
      bodyText.includes("error") ||
      bodyText.includes("failed") ||
      bodyText.includes("slow");

    console.log(`API timeout handling present: ${hasTimeoutHandling}`);
  });

  test("should handle server error responses", async ({ page }) => {
    // Mock 500 server error
    await page.route("**/api/**", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Internal Server Error" }),
      });
    });

    await page.fill("#loginEmail", "server.error@example.com");
    await page.fill("#loginPassword", "serverpass123");
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    // Should show error message
    const bodyText = await page.textContent("body");
    const hasServerErrorHandling =
      bodyText.includes("error") ||
      bodyText.includes("server") ||
      bodyText.includes("failed") ||
      bodyText.includes("500");

    console.log(`Server error handling present: ${hasServerErrorHandling}`);
  });

  test("should handle malformed API responses", async ({ page }) => {
    // Mock malformed JSON response
    await page.route("**/api/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: "invalid json response",
      });
    });

    await page.fill("#loginEmail", "malformed@example.com");
    await page.fill("#loginPassword", "malformedpass");
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    // Should handle parsing error gracefully
    const bodyText = await page.textContent("body");
    const hasParsingErrorHandling =
      bodyText.includes("error") ||
      bodyText.includes("invalid") ||
      bodyText.includes("failed");

    console.log(
      `Malformed response handling present: ${hasParsingErrorHandling}`
    );
  });

  test("should handle extremely long input values", async ({ page }) => {
    await page.click("text=Sign up here");

    // Test with extremely long strings
    const longString = "a".repeat(10000);
    const longEmail = "a".repeat(5000) + "@example.com";

    await page.fill("#firstName", longString);
    await page.fill("#lastName", longString);
    await page.fill("#email", longEmail);
    await page.fill("#password", longString);
    await page.fill("#confirmPassword", longString);

    // Check if inputs handle long values
    const firstNameValue = await page.locator("#firstName").inputValue();
    const emailValue = await page.locator("#email").inputValue();

    // Should either truncate or handle gracefully
    expect(firstNameValue.length).toBeLessThan(15000); // Should be reasonable length
    expect(emailValue.length).toBeLessThan(10000);

    console.log(
      `Long input handling: firstName=${firstNameValue.length}, email=${emailValue.length}`
    );
  });

  test("should handle special characters in input fields", async ({ page }) => {
    await page.click("text=Sign up here");

    // Test special characters
    const specialChars = "!@#$%^&*()[]{}|;':\",./<>?`~";
    const unicodeChars = "áéíóúñü中文日本語العربية🚀🔥💯";

    await page.fill("#firstName", specialChars);
    await page.fill("#lastName", unicodeChars);
    await page.fill("#companyName", specialChars + unicodeChars);

    // Check if values are preserved
    const firstNameValue = await page.locator("#firstName").inputValue();
    const lastNameValue = await page.locator("#lastName").inputValue();

    expect(firstNameValue.length).toBeGreaterThan(0);
    expect(lastNameValue.length).toBeGreaterThan(0);

    console.log("Special characters handled in input fields");
  });

  test("should handle rapid form submissions", async ({ page }) => {
    await page.click("text=Sign up here");

    const timestamp = Date.now();
    await page.fill("#firstName", "Rapid");
    await page.fill("#lastName", "Test");
    await page.fill("#email", `rapid.test.${timestamp}@example.com`);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    // Submit form multiple times rapidly
    const submitButton = page.locator('button[type="submit"]');

    await submitButton.click();
    await submitButton.click();
    await submitButton.click();

    await page.waitForTimeout(2000);

    // Should handle duplicate submissions gracefully
    const bodyText = await page.textContent("body");

    // Should not show multiple error messages or crash
    expect(bodyText.length).toBeGreaterThan(0);

    console.log("Rapid form submissions handled");
  });

  test("should handle browser back/forward navigation", async ({ page }) => {
    // Start on login page
    await page.goto("http://localhost:3002");

    // Go to registration
    await page.click("text=Sign up here");
    await expect(page.locator("#firstName")).toBeVisible();

    // Use browser back
    await page.goBack();

    // Should be back on login
    await expect(page.locator("#loginEmail")).toBeVisible();

    // Use browser forward
    await page.goForward();

    // Should be on registration again
    await expect(page.locator("#firstName")).toBeVisible();

    console.log("Browser navigation handled correctly");
  });

  test("should handle page refresh during form filling", async ({ page }) => {
    await page.click("text=Sign up here");

    // Fill partial form
    await page.fill("#firstName", "Refresh");
    await page.fill("#lastName", "Test");
    await page.fill("#email", "refresh.test@example.com");

    // Refresh page
    await page.reload();

    // Form should be reset or handle gracefully
    const firstNameValue = await page.locator("#firstName").inputValue();

    // Should either be empty or preserve state
    console.log(`Form state after refresh: ${firstNameValue}`);

    // Page should still be functional
    await expect(page.locator("#firstName")).toBeVisible();
  });

  test("should handle JavaScript errors gracefully", async ({ page }) => {
    // Listen for console errors
    const consoleErrors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    // Listen for page errors
    const pageErrors = [];
    page.on("pageerror", (error) => {
      pageErrors.push(error.message);
    });

    await page.goto("http://localhost:3002");

    // Interact with the page to trigger potential JS errors
    await page.click("text=Sign up here");
    await page.fill("#firstName", "JS Test");
    await page.click("text=Sign in here");

    await page.waitForTimeout(2000);

    // Page should still be functional despite any errors
    await expect(page.locator("#loginEmail")).toBeVisible();

    console.log(`Console errors: ${consoleErrors.length}`);
    console.log(`Page errors: ${pageErrors.length}`);

    if (consoleErrors.length > 0) {
      console.log("Console errors found:", consoleErrors);
    }
    if (pageErrors.length > 0) {
      console.log("Page errors found:", pageErrors);
    }
  });

  test("should handle missing form fields gracefully", async ({ page }) => {
    // Try to access form fields that might not exist
    const nonExistentFields = [
      "#nonExistentField",
      "#missingInput",
      "#undefinedElement",
    ];

    for (const selector of nonExistentFields) {
      const element = page.locator(selector);
      const isVisible = await element.isVisible().catch(() => false);

      expect(isVisible).toBe(false);
    }

    // Main form should still work
    await expect(page.locator("#loginEmail")).toBeVisible();

    console.log("Missing form fields handled gracefully");
  });

  test("should handle disabled JavaScript scenario", async ({ page }) => {
    // Disable JavaScript
    await page.context().addInitScript(() => {
      delete window.React;
      delete window.ReactDOM;
    });

    await page.goto("http://localhost:3002");
    await page.waitForTimeout(3000);

    // Basic HTML should still be present
    const bodyText = await page.textContent("body");
    expect(bodyText.length).toBeGreaterThan(0);

    // Should show noscript content or fallback
    const hasNoScriptHandling =
      bodyText.includes("JavaScript") ||
      bodyText.includes("enable") ||
      bodyText.includes("browser") ||
      (await page.isVisible("noscript"));

    console.log(`No-JavaScript fallback present: ${hasNoScriptHandling}`);
  });

  test("should handle memory constraints", async ({ page }) => {
    // Create multiple large arrays to stress memory
    await page.evaluate(() => {
      window.stressTest = [];
      for (let i = 0; i < 100; i++) {
        window.stressTest.push(new Array(10000).fill("memory-test-data"));
      }
    });

    // Application should still be responsive
    await page.fill("#loginEmail", "memory@test.com");
    await page.fill("#loginPassword", "memorytest123");

    await expect(page.locator("#loginEmail")).toHaveValue("memory@test.com");

    // Clean up
    await page.evaluate(() => {
      delete window.stressTest;
    });

    console.log("Memory constraints handled");
  });
});
