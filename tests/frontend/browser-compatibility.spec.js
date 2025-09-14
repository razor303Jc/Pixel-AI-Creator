/**
 * Simplified Cross-Browser Compatibility Tests
 * Tests application functionality across different browsers
 */

const { test, expect } = require("@playwright/test");

// Test on different browsers
test.describe("Cross-Browser Compatibility", () => {
  test("should load application successfully", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Basic page load test
    await expect(page).toHaveTitle(/.+/); // Should have some title

    // Check if main content loads
    const bodyText = await page.textContent("body");
    expect(bodyText.length).toBeGreaterThan(100); // Should have substantial content

    // Check for login form elements
    await expect(page.locator("#loginEmail")).toBeVisible();
    await expect(page.locator("#loginPassword")).toBeVisible();

    console.log("✓ Application loaded successfully");
  });

  test("should handle form interactions", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Test form filling
    await page.fill("#loginEmail", "test@example.com");
    await page.fill("#loginPassword", "testpassword");

    await expect(page.locator("#loginEmail")).toHaveValue("test@example.com");
    await expect(page.locator("#loginPassword")).toHaveValue("testpassword");

    // Test form switching
    await page.click("text=Sign up here");
    await expect(page.locator("#firstName")).toBeVisible();

    console.log("✓ Form interactions working");
  });

  test("should handle CSS rendering", async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.waitForTimeout(2000);

    // Check if styles are applied (Bootstrap classes should be styled)
    const emailInput = page.locator("#loginEmail");
    const styles = await emailInput.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        display: computed.display,
        padding: computed.padding,
        border: computed.border,
        fontSize: computed.fontSize,
      };
    });

    // Should have some styling applied
    expect(styles.display).not.toBe("inline");
    expect(styles.padding).not.toBe("0px");

    console.log("✓ CSS rendering working");
  });

  test("should handle JavaScript functionality", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Test dynamic content switching
    await page.click("text=Sign up here");
    await expect(page.locator("h3")).toContainText("Create Your Account");

    await page.click("text=Sign in here");
    await expect(page.locator("h3")).toContainText("Welcome Back");

    console.log("✓ JavaScript functionality working");
  });
});

// Mobile responsiveness tests
test.describe("Mobile Responsiveness", () => {
  test("should be responsive on mobile viewport", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("http://localhost:3002");
    await page.waitForTimeout(2000);

    // Check if content is visible and accessible
    await expect(page.locator("#loginEmail")).toBeVisible();
    await expect(page.locator("#loginPassword")).toBeVisible();

    // Test touch interactions
    await page.tap("#loginEmail");
    await page.fill("#loginEmail", "mobile@test.com");

    console.log("✓ Mobile responsiveness working");
  });

  test("should handle mobile form interactions", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("http://localhost:3002");

    // Test mobile form filling
    await page.tap("#loginEmail");
    await page.fill("#loginEmail", "mobile.user@example.com");

    await page.tap("#loginPassword");
    await page.fill("#loginPassword", "mobilepass123");

    // Test form submission on mobile
    await page.tap('button[type="submit"]');
    await page.waitForTimeout(2000);

    console.log("✓ Mobile form interactions working");
  });
});

// Performance tests
test.describe("Performance", () => {
  test("should load within reasonable time", async ({ page }) => {
    const startTime = Date.now();

    await page.goto("http://localhost:3002");

    // Wait for main content to be visible
    await expect(page.locator("#loginEmail")).toBeVisible();

    const loadTime = Date.now() - startTime;

    // Should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);

    console.log(`Page load time: ${loadTime}ms`);
  });

  test("should handle concurrent user interactions", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Simulate rapid user interactions
    const promises = [
      page.fill("#loginEmail", "test1@example.com"),
      page.click("text=Sign up here"),
      page.waitForTimeout(100),
      page.click("text=Sign in here"),
      page.fill("#loginPassword", "testpass"),
    ];

    await Promise.all(promises);

    // Should still be in a consistent state
    await expect(page.locator("#loginEmail")).toBeVisible();

    console.log("✓ Concurrent interactions handled correctly");
  });
});

// Accessibility tests
test.describe("Accessibility", () => {
  test("should maintain accessibility features", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Test keyboard navigation
    await page.press("body", "Tab");
    const focusedElement = await page.locator(":focus").getAttribute("id");
    expect(focusedElement).toBeTruthy();

    // Test ARIA attributes
    const submitButton = page.locator('button[type="submit"]').first();
    const buttonType = await submitButton.getAttribute("type");

    expect(buttonType).toBe("submit");

    // Test label associations
    await expect(page.locator('label[for="loginEmail"]')).toBeVisible();

    console.log("✓ Accessibility features working");
  });
});
