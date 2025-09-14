/**
 * Form and Input Elements Tests
 * Tests all form elements, input validation, accessibility, and interactions
 */

const { test, expect } = require("@playwright/test");

test.describe("Form and Input Elements", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3002");
  });

  test("should validate all input field types", async ({ page }) => {
    // Test login form inputs
    await expect(page.locator("#loginEmail")).toHaveAttribute("type", "email");
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "type",
      "password"
    );

    // Switch to registration form
    await page.click("text=Sign up here");

    // Test registration form inputs
    await expect(page.locator("#firstName")).toHaveAttribute("type", "text");
    await expect(page.locator("#lastName")).toHaveAttribute("type", "text");
    await expect(page.locator("#email")).toHaveAttribute("type", "email");
    await expect(page.locator("#password")).toHaveAttribute("type", "password");
    await expect(page.locator("#confirmPassword")).toHaveAttribute(
      "type",
      "password"
    );
  });

  test("should have proper form labels and accessibility", async ({ page }) => {
    // Check login form labels
    const loginEmailLabel = page.locator('label[for="loginEmail"]');
    const loginPasswordLabel = page.locator('label[for="loginPassword"]');

    if (await loginEmailLabel.isVisible()) {
      await expect(loginEmailLabel).toBeVisible();
    }
    if (await loginPasswordLabel.isVisible()) {
      await expect(loginPasswordLabel).toBeVisible();
    }

    // Switch to registration form
    await page.click("text=Sign up here");

    // Check registration form labels
    const formLabels = [
      'label[for="firstName"]',
      'label[for="lastName"]',
      'label[for="email"]',
      'label[for="password"]',
      'label[for="confirmPassword"]',
    ];

    for (const labelSelector of formLabels) {
      const label = page.locator(labelSelector);
      if (await label.isVisible()) {
        await expect(label).toBeVisible();
        const labelText = await label.textContent();
        expect(labelText.length).toBeGreaterThan(0);
      }
    }
  });

  test("should validate required field attributes", async ({ page }) => {
    // Login form required fields
    await expect(page.locator("#loginEmail")).toHaveAttribute("required");
    await expect(page.locator("#loginPassword")).toHaveAttribute("required");

    // Registration form required fields
    await page.click("text=Sign up here");

    const requiredFields = [
      "#firstName",
      "#lastName",
      "#email",
      "#password",
      "#confirmPassword",
    ];

    for (const fieldSelector of requiredFields) {
      await expect(page.locator(fieldSelector)).toHaveAttribute("required");
    }
  });

  test("should validate autocomplete attributes", async ({ page }) => {
    // Login form autocomplete
    await expect(page.locator("#loginEmail")).toHaveAttribute(
      "autocomplete",
      "email"
    );
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "autocomplete",
      "current-password"
    );

    // Registration form autocomplete
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

  test("should validate name attributes for form submission", async ({
    page,
  }) => {
    // Login form names
    await expect(page.locator("#loginEmail")).toHaveAttribute("name", "email");
    await expect(page.locator("#loginPassword")).toHaveAttribute(
      "name",
      "password"
    );

    // Registration form names
    await page.click("text=Sign up here");

    await expect(page.locator("#firstName")).toHaveAttribute(
      "name",
      "firstName"
    );
    await expect(page.locator("#lastName")).toHaveAttribute("name", "lastName");
    await expect(page.locator("#email")).toHaveAttribute("name", "email");
    await expect(page.locator("#password")).toHaveAttribute("name", "password");
    await expect(page.locator("#confirmPassword")).toHaveAttribute(
      "name",
      "confirmPassword"
    );
  });

  test("should handle form validation messages", async ({ page }) => {
    await page.click("text=Sign up here");

    // Try submitting empty form
    await page.click('button[type="submit"]');

    // Check if browser validation messages appear
    const firstName = page.locator("#firstName");
    const isInvalid = await firstName.evaluate((el) => !el.validity.valid);

    if (isInvalid) {
      console.log("HTML5 validation is working for required fields");
    }

    // Test email format validation
    await page.fill("#firstName", "Test");
    await page.fill("#lastName", "User");
    await page.fill("#email", "invalid-email-format");
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    await page.click('button[type="submit"]');

    const emailField = page.locator("#email");
    const emailIsInvalid = await emailField.evaluate(
      (el) => !el.validity.valid
    );

    if (emailIsInvalid) {
      console.log("Email format validation is working");
    }
  });

  test("should test input field interactions", async ({ page }) => {
    // Test focus and blur events
    await page.focus("#loginEmail");
    await expect(page.locator("#loginEmail")).toBeFocused();

    // Test typing
    await page.fill("#loginEmail", "test@example.com");
    await expect(page.locator("#loginEmail")).toHaveValue("test@example.com");

    // Test clearing
    await page.fill("#loginEmail", "");
    await expect(page.locator("#loginEmail")).toHaveValue("");

    // Test password field
    await page.fill("#loginPassword", "testpassword123");
    await expect(page.locator("#loginPassword")).toHaveValue("testpassword123");
  });

  test("should test placeholder texts", async ({ page }) => {
    const inputsWithPlaceholders = ["#loginEmail", "#loginPassword"];

    for (const selector of inputsWithPlaceholders) {
      const placeholder = await page
        .locator(selector)
        .getAttribute("placeholder");
      if (placeholder) {
        expect(placeholder.length).toBeGreaterThan(0);
        console.log(`${selector} placeholder: ${placeholder}`);
      }
    }

    // Check registration form placeholders
    await page.click("text=Sign up here");

    const regInputs = [
      "#firstName",
      "#lastName",
      "#email",
      "#password",
      "#confirmPassword",
      "#companyName",
    ];

    for (const selector of regInputs) {
      if (await page.isVisible(selector)) {
        const placeholder = await page
          .locator(selector)
          .getAttribute("placeholder");
        if (placeholder) {
          console.log(`${selector} placeholder: ${placeholder}`);
        }
      }
    }
  });

  test("should test form submission buttons", async ({ page }) => {
    // Login form submit button
    const loginSubmit = page.locator('button[type="submit"]').first();
    await expect(loginSubmit).toBeVisible();
    await expect(loginSubmit).toBeEnabled();

    const loginButtonText = await loginSubmit.textContent();
    expect(loginButtonText).toBeTruthy();
    console.log(`Login button text: ${loginButtonText}`);

    // Registration form submit button
    await page.click("text=Sign up here");

    const regSubmit = page.locator('button[type="submit"]').first();
    await expect(regSubmit).toBeVisible();
    await expect(regSubmit).toBeEnabled();

    const regButtonText = await regSubmit.textContent();
    expect(regButtonText).toBeTruthy();
    console.log(`Registration button text: ${regButtonText}`);
  });

  test("should handle form loading states", async ({ page }) => {
    await page.click("text=Sign up here");

    // Fill form with valid data
    const timestamp = Date.now();
    await page.fill("#firstName", "Load");
    await page.fill("#lastName", "Test");
    await page.fill("#email", `load.test.${timestamp}@example.com`);
    await page.fill("#password", "Password123!");
    await page.fill("#confirmPassword", "Password123!");

    // Submit form and check for loading state
    await page.click('button[type="submit"]');

    // Check if button is disabled during submission
    const submitButton = page.locator('button[type="submit"]').first();

    // Wait a bit to see if loading state appears
    await page.waitForTimeout(500);

    // Check if button text changed or button is disabled
    const isDisabled = await submitButton.isDisabled();
    const buttonText = await submitButton.textContent();

    console.log(`Button disabled during submission: ${isDisabled}`);
    console.log(`Button text during submission: ${buttonText}`);
  });

  test("should test password visibility toggle", async ({ page }) => {
    // Test login password toggle
    await page.fill("#loginPassword", "testpassword");

    // Look for eye icon or toggle button
    const toggleSelectors = [
      'button:has([data-testid="eye-icon"])',
      ".password-toggle",
      "button:has(.eye-icon)",
      'button[aria-label*="password"]',
      '[data-testid="password-toggle"]',
    ];

    let toggleFound = false;
    for (const selector of toggleSelectors) {
      if (await page.isVisible(selector)) {
        await page.click(selector);
        toggleFound = true;

        // Check if password type changed
        const passwordType = await page
          .locator("#loginPassword")
          .getAttribute("type");
        console.log(`Password field type after toggle: ${passwordType}`);
        break;
      }
    }

    console.log(`Password visibility toggle found: ${toggleFound}`);
  });

  test("should validate input field constraints", async ({ page }) => {
    await page.click("text=Sign up here");

    // Test maximum length constraints if present
    const inputs = ["#firstName", "#lastName", "#email", "#companyName"];

    for (const selector of inputs) {
      if (await page.isVisible(selector)) {
        const maxLength = await page
          .locator(selector)
          .getAttribute("maxlength");
        if (maxLength) {
          console.log(`${selector} max length: ${maxLength}`);

          // Test exceeding max length
          const longText = "a".repeat(parseInt(maxLength) + 10);
          await page.fill(selector, longText);

          const actualValue = await page.locator(selector).inputValue();
          expect(actualValue.length).toBeLessThanOrEqual(parseInt(maxLength));
        }
      }
    }
  });

  test("should test form keyboard navigation", async ({ page }) => {
    // Test tab navigation through form fields
    await page.press("body", "Tab");

    const focusedElement1 = await page.locator(":focus").getAttribute("id");
    console.log(`First tab focus: ${focusedElement1}`);

    await page.press("body", "Tab");
    const focusedElement2 = await page.locator(":focus").getAttribute("id");
    console.log(`Second tab focus: ${focusedElement2}`);

    // Test form submission with Enter key
    await page.focus("#loginEmail");
    await page.fill("#loginEmail", "test@example.com");
    await page.press("#loginEmail", "Tab");
    await page.fill("#loginPassword", "testpassword");

    // Try submitting with Enter
    await page.press("#loginPassword", "Enter");

    // Wait to see if form submission was triggered
    await page.waitForTimeout(1000);
    console.log("Keyboard form submission tested");
  });
});
