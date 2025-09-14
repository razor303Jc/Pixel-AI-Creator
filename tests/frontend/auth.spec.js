/**
 * Authentication Flow Tests
 * Tests registration, login, logout, and authentication states
 */

const { test, expect } = require("@playwright/test");

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.goto("http://localhost:3002");
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
  });

  test("should display login form by default", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Check login form elements
    await expect(page.locator("h3")).toContainText("Welcome Back");
    await expect(page.locator("#loginEmail")).toBeVisible();
    await expect(page.locator("#loginPassword")).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText(
      "Sign In"
    );

    // Check switch to register link
    await expect(page.locator("text=Sign up here")).toBeVisible();
  });

  test("should switch between login and registration forms", async ({
    page,
  }) => {
    await page.goto("http://localhost:3002");

    // Switch to registration
    await page.click("text=Sign up here");
    await expect(page.locator("h3")).toContainText("Create Your Account");

    // Check registration form elements
    await expect(page.locator("#firstName")).toBeVisible();
    await expect(page.locator("#lastName")).toBeVisible();
    await expect(page.locator("#email")).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
    await expect(page.locator("#confirmPassword")).toBeVisible();

    // Switch back to login
    await page.click("text=Sign in here");
    await expect(page.locator("h3")).toContainText("Welcome Back");
  });

  test("should validate required fields in registration form", async ({
    page,
  }) => {
    await page.goto("http://localhost:3002");
    await page.click("text=Sign up here");

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // Check HTML5 validation (required attributes)
    const firstName = page.locator("#firstName");
    const lastName = page.locator("#lastName");
    const email = page.locator("#email");
    const password = page.locator("#password");

    await expect(firstName).toHaveAttribute("required");
    await expect(lastName).toHaveAttribute("required");
    await expect(email).toHaveAttribute("required");
    await expect(password).toHaveAttribute("required");
  });

  test("should validate email format", async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.click("text=Sign up here");

    // Fill form with invalid email
    await page.fill("#firstName", "Test");
    await page.fill("#lastName", "User");
    await page.fill("#email", "invalid-email");
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    await page.click('button[type="submit"]');

    // Check email validation
    const emailField = page.locator("#email");
    await expect(emailField).toHaveAttribute("type", "email");
  });

  test("should register a new user successfully", async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.click("text=Sign up here");

    const timestamp = Date.now();
    const testEmail = `test.user.${timestamp}@example.com`;

    // Fill registration form
    await page.fill("#firstName", "Test");
    await page.fill("#lastName", "User");
    await page.fill("#email", testEmail);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");
    await page.fill("#companyName", "Test Company");

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for success (should redirect to dashboard or show success)
    await page.waitForTimeout(3000); // Wait for API call

    // Check if redirected to dashboard or success state
    const currentUrl = page.url();
    const bodyText = await page.textContent("body");

    // Should either be on dashboard or show success message
    expect(
      currentUrl === "http://localhost:3002/" ||
        bodyText.includes("Dashboard") ||
        bodyText.includes("Welcome")
    ).toBeTruthy();
  });

  test("should login with valid credentials", async ({ page }) => {
    // First register a user
    await page.goto("http://localhost:3002");
    await page.click("text=Sign up here");

    const timestamp = Date.now();
    const testEmail = `login.test.${timestamp}@example.com`;

    await page.fill("#firstName", "Login");
    await page.fill("#lastName", "Test");
    await page.fill("#email", testEmail);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");
    await page.click('button[type="submit"]');

    await page.waitForTimeout(2000);

    // Logout if logged in
    if (
      page.url().includes("dashboard") ||
      (await page.isVisible("text=Logout"))
    ) {
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      await page.reload();
    }

    // Now test login
    await page.goto("http://localhost:3002");
    await page.fill("#loginEmail", testEmail);
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    // Should be logged in (check for dashboard or user content)
    const bodyText = await page.textContent("body");
    expect(
      bodyText.includes("Dashboard") ||
        bodyText.includes("Welcome") ||
        !bodyText.includes("Sign In")
    ).toBeTruthy();
  });

  test("should show error for invalid login credentials", async ({ page }) => {
    await page.goto("http://localhost:3002");

    await page.fill("#loginEmail", "nonexistent@example.com");
    await page.fill("#loginPassword", "wrongpassword");
    await page.click('button[type="submit"]');

    await page.waitForTimeout(2000);

    // Should show error message
    const bodyText = await page.textContent("body");
    expect(
      bodyText.includes("failed") ||
        bodyText.includes("invalid") ||
        bodyText.includes("error")
    ).toBeTruthy();
  });

  test("should validate password confirmation", async ({ page }) => {
    await page.goto("http://localhost:3002");
    await page.click("text=Sign up here");

    await page.fill("#firstName", "Test");
    await page.fill("#lastName", "User");
    await page.fill("#email", "test@example.com");
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "DifferentPassword123!");

    await page.click('button[type="submit"]');

    // Should show validation error for password mismatch
    await page.waitForTimeout(1000);
    const bodyText = await page.textContent("body");
    expect(
      bodyText.includes("match") || bodyText.includes("confirm")
    ).toBeTruthy();
  });

  test("should toggle password visibility", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Test login form password toggle
    await page.fill("#loginPassword", "testpassword");

    // Password should be hidden by default
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "type",
      "password"
    );

    // Click eye icon to show password (if visible)
    const eyeButton = page
      .locator(
        'button:has([data-testid="eye-icon"], .eye-icon, [class*="eye"])'
      )
      .first();
    if (await eyeButton.isVisible()) {
      await eyeButton.click();
      await expect(page.locator("#loginPassword")).toHaveAttribute(
        "type",
        "text"
      );
    }
  });

  test("should have proper form accessibility attributes", async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Check login form accessibility
    await expect(page.locator("#loginEmail")).toHaveAttribute("name", "email");
    await expect(page.locator("#loginEmail")).toHaveAttribute(
      "autocomplete",
      "email"
    );
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "name",
      "password"
    );
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "autocomplete",
      "current-password"
    );

    // Check registration form
    await page.click("text=Sign up here");

    await expect(page.locator("#firstName")).toHaveAttribute(
      "autocomplete",
      "given-name"
    );
    await expect(page.locator("#lastName")).toHaveAttribute(
      "autocomplete",
      "family-name"
    );
    await expect(page.locator("#email")).toHaveAttribute(
      "autocomplete",
      "email"
    );
    await expect(page.locator("#password")).toHaveAttribute(
      "autocomplete",
      "new-password"
    );
    await expect(page.locator("#confirmPassword")).toHaveAttribute(
      "autocomplete",
      "new-password"
    );
  });
});
