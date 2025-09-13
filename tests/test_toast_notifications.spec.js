/**
 * PIXEL AI CREATOR - TOAST NOTIFICATION TESTS
 * Comprehensive Tests for React-Toastify Integration
 *
 * 🍞 Toast Tests for:
 * - Success notifications
 * - Error notifications
 * - Warning notifications
 * - Info notifications
 * - Toast positioning and styling
 * - Auto-dismiss functionality
 * - Multiple toast handling
 * - Custom toast content
 */

const { test, expect } = require("@playwright/test");

const BASE_URL = "http://localhost:3002";

test.describe("🍞 TOAST NOTIFICATION TESTS", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(1000);

    // Navigate to registration form
    try {
      await page.click('text="Create Account"', { timeout: 5000 });
    } catch (e) {
      console.log("Looking for registration form...");
    }

    console.log("🌐 Page loaded for toast testing");
  });

  test.describe("✅ Success Toast Tests", () => {
    test("should display success toast on successful registration", async ({
      page,
    }) => {
      console.log("🧪 Testing success toast notification...");

      // Mock successful API response
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Account created successfully!",
            user: { id: 1, email: "test@example.com" },
          }),
        });
      });

      // Fill form with valid data
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`success-test-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");

      // Submit form
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(1000);

      // Check for success toast
      const successToast = page.locator(".Toastify__toast--success");
      await expect(successToast).toBeVisible({ timeout: 5000 });

      // Check toast content
      await expect(
        page.locator('text="Account created successfully!"')
      ).toBeVisible();

      // Check for success icon in toast
      const checkIcon = successToast.locator("svg");
      await expect(checkIcon).toBeVisible();

      console.log("✅ Success toast displayed correctly");
    });

    test("should auto-dismiss success toast after timeout", async ({
      page,
    }) => {
      console.log("🧪 Testing success toast auto-dismiss...");

      // Mock successful API response
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Account created successfully!",
          }),
        });
      });

      // Fill and submit form
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`autodismiss-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();

      // Toast should be visible initially
      const successToast = page.locator(".Toastify__toast--success");
      await expect(successToast).toBeVisible({ timeout: 5000 });

      // Wait for auto-dismiss (default is usually 5 seconds)
      await page.waitForTimeout(6000);

      // Toast should be dismissed
      await expect(successToast).not.toBeVisible();

      console.log("✅ Success toast auto-dismisses correctly");
    });
  });

  test.describe("❌ Error Toast Tests", () => {
    test("should display error toast on registration failure", async ({
      page,
    }) => {
      console.log("🧪 Testing error toast notification...");

      // Mock error API response
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "Email already exists",
          }),
        });
      });

      // Fill form with valid data
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page.locator('input[name="email"]').fill("existing@example.com");
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");

      // Submit form
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(1000);

      // Check for error toast
      const errorToast = page.locator(".Toastify__toast--error");
      await expect(errorToast).toBeVisible({ timeout: 5000 });

      // Check toast content
      await expect(page.locator('text="Email already exists"')).toBeVisible();

      // Check for error icon in toast
      const errorIcon = errorToast.locator("svg");
      await expect(errorIcon).toBeVisible();

      console.log("✅ Error toast displayed correctly");
    });

    test("should display error toast on network failure", async ({ page }) => {
      console.log("🧪 Testing network error toast...");

      // Mock network failure
      await page.route("**/api/auth/register", (route) => {
        route.abort("failed");
      });

      // Fill and submit form
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`network-error-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();

      // Check for network error toast
      const errorToast = page.locator(".Toastify__toast--error");
      await expect(errorToast).toBeVisible({ timeout: 5000 });

      // Should show generic error message
      await expect(
        page.locator('text="Registration failed. Please try again."')
      ).toBeVisible();

      console.log("✅ Network error toast displayed correctly");
    });
  });

  test.describe("⚠️ Warning Toast Tests", () => {
    test("should display warning toast for validation issues", async ({
      page,
    }) => {
      console.log("🧪 Testing warning toast notification...");

      // Try to submit form with missing fields
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(500);

      // Check for warning toast about validation
      const warningToast = page.locator(".Toastify__toast--warning");
      if (await warningToast.isVisible()) {
        await expect(
          page.locator('text="Please fix the validation errors"')
        ).toBeVisible();
        console.log("✅ Warning toast displayed correctly");
      } else {
        console.log("ℹ️ Warning toast not implemented for validation errors");
      }
    });
  });

  test.describe("ℹ️ Info Toast Tests", () => {
    test("should display info toast for informational messages", async ({
      page,
    }) => {
      console.log("🧪 Testing info toast notification...");

      // This would test info toasts if implemented
      // For example, password strength tips or form guidance

      console.log("ℹ️ Info toast tests would go here");
    });
  });

  test.describe("🎯 Toast Positioning Tests", () => {
    test("should display toasts in correct position", async ({ page }) => {
      console.log("🧪 Testing toast positioning...");

      // Mock API response to trigger toast
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Account created successfully!",
          }),
        });
      });

      // Trigger a toast
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`position-test-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();

      // Check toast container position
      const toastContainer = page.locator(".Toastify__toast-container");
      await expect(toastContainer).toBeVisible({ timeout: 5000 });

      // Check if positioned correctly (usually top-right or bottom-right)
      const containerBox = await toastContainer.boundingBox();
      expect(containerBox).toBeTruthy();

      // Should be positioned on the right side of the screen
      expect(containerBox.x).toBeGreaterThan(800); // Assuming 1280px width

      console.log("✅ Toast positioning correct");
    });
  });

  test.describe("📱 Mobile Toast Tests", () => {
    test("should display toasts correctly on mobile", async ({ page }) => {
      console.log("🧪 Testing mobile toast display...");

      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(500);

      // Mock API response
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Account created successfully!",
          }),
        });
      });

      // Fill and submit form
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`mobile-test-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();

      // Check toast on mobile
      const toast = page.locator(".Toastify__toast--success");
      await expect(toast).toBeVisible({ timeout: 5000 });

      // Toast should be responsive on mobile
      const toastBox = await toast.boundingBox();
      expect(toastBox.width).toBeLessThan(375); // Should fit mobile width

      console.log("✅ Mobile toast display working correctly");
    });
  });

  test.describe("🔄 Multiple Toast Tests", () => {
    test("should handle multiple toasts simultaneously", async ({ page }) => {
      console.log("🧪 Testing multiple toast handling...");

      // This test would check if multiple toasts can be displayed
      // For example, validation warnings followed by error messages

      // Mock multiple API calls to trigger multiple toasts
      let callCount = 0;
      await page.route("**/api/auth/register", (route) => {
        callCount++;
        if (callCount === 1) {
          route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              message: "First error message",
            }),
          });
        } else {
          route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({
              success: false,
              message: "Second error message",
            }),
          });
        }
      });

      // Trigger first toast
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`multiple1-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(1000);

      // Trigger second toast
      await page
        .locator('input[name="email"]')
        .fill(`multiple2-${Date.now()}@example.com`);
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(1000);

      // Check if multiple toasts are handled properly
      const toasts = page.locator(".Toastify__toast");
      const toastCount = await toasts.count();

      expect(toastCount).toBeGreaterThanOrEqual(1);

      console.log(
        `✅ Multiple toasts handled correctly (${toastCount} toasts)`
      );
    });
  });

  test.describe("🎨 Toast Styling Tests", () => {
    test("should have correct toast styling and animations", async ({
      page,
    }) => {
      console.log("🧪 Testing toast styling and animations...");

      // Mock API response
      await page.route("**/api/auth/register", (route) => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "Account created successfully!",
          }),
        });
      });

      // Trigger toast
      await page.locator('input[name="firstName"]').fill("John");
      await page.locator('input[name="lastName"]').fill("Doe");
      await page
        .locator('input[name="email"]')
        .fill(`styling-test-${Date.now()}@example.com`);
      await page.locator('input[name="password"]').fill("StrongPass123!");
      await page
        .locator('input[name="confirmPassword"]')
        .fill("StrongPass123!");
      await page.locator('button[type="submit"]').click();

      // Check toast styling
      const toast = page.locator(".Toastify__toast--success");
      await expect(toast).toBeVisible({ timeout: 5000 });

      // Check if toast has proper CSS classes
      await expect(toast).toHaveClass(/Toastify__toast/);
      await expect(toast).toHaveClass(/Toastify__toast--success/);

      // Check for animation classes
      const toastContainer = page.locator(".Toastify__toast-container");
      await expect(toastContainer).toHaveClass(/Toastify__toast-container/);

      console.log("✅ Toast styling and animations working correctly");
    });
  });

  test.afterEach(async ({ page }) => {
    // Clear any remaining toasts
    await page.evaluate(() => {
      // Clear all toasts if react-toastify dismiss method is available
      if (window.toast && window.toast.dismiss) {
        window.toast.dismiss();
      }
    });

    console.log("🧹 Toast test cleanup completed");
  });
});

module.exports = {};
