const { test, expect } = require("@playwright/test");

test.describe("Create Assistant Form Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Login with test credentials
    try {
      const signInButton = page.locator(
        'button:has-text("Sign In"), .btn:has-text("Sign In")'
      );

      if (await signInButton.isVisible({ timeout: 3000 })) {
        console.log("🔐 Logging in with test credentials...");

        const emailInput = page.locator(
          'input[type="email"], input[name="email"]'
        );
        const passwordInput = page.locator(
          'input[type="password"], input[name="password"]'
        );

        await emailInput.fill("jc@razorflow-ai.com");
        await passwordInput.fill("securepassword123");
        await signInButton.click();

        // Wait for navigation after login
        await page.waitForSelector(
          '[data-testid="nav-dashboard"], .nav-link, .dashboard, .sidebar, .navbar',
          { timeout: 15000 }
        );
        console.log("✅ Successfully logged in");
      } else {
        console.log("✅ Already logged in");
      }
    } catch (error) {
      console.log("⚠️ Login process - continuing with existing session");
    }

    // Ensure we're on the main dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForSelector('button:has-text("Create Assistant")', {
      timeout: 10000,
    });
  });

  test("should open assistant creation modal with all required fields", async ({
    page,
  }) => {
    console.log("🚀 Testing assistant creation modal opening...");

    // Click Create Assistant button
    await page.click('button:has-text("Create Assistant")');

    // Wait for modal to appear
    await page.waitForSelector(".modal.show", { timeout: 5000 });

    // Verify modal title
    await expect(page.locator(".modal-title")).toContainText(
      "Create New AI Assistant"
    );

    // Verify all required form fields are present
    await expect(
      page.locator(
        'input[placeholder*="assistant name"], input[placeholder*="name"]'
      )
    ).toBeVisible();
    await expect(page.locator('select[class*="form-select"]')).toHaveCount(3); // Personality, Template, Client
    await expect(
      page.locator('textarea[placeholder*="description"]')
    ).toBeVisible();

    // Verify auto-build checkbox is present
    await expect(page.locator("#auto-build-checkbox")).toBeVisible();
    await expect(
      page.locator('label[for="auto-build-checkbox"]')
    ).toContainText("Auto-build and deploy after creation");

    console.log(
      "✅ Assistant creation modal opened successfully with all fields"
    );
  });

  test("should validate required fields and show errors", async ({ page }) => {
    console.log("🚀 Testing form validation for required fields...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Try to submit without filling required fields
    await page.click('button:has-text("Create Assistant")');

    // Check for validation errors
    await expect(page.locator(".is-invalid")).toHaveCount(3); // Name, Personality, Template are required

    // Verify specific error messages or invalid classes
    const nameInput = page.locator(
      'input[placeholder*="assistant name"], input[placeholder*="name"]'
    );
    await expect(nameInput).toHaveClass(/is-invalid/);

    console.log("✅ Form validation working correctly");
  });

  test("should successfully create assistant with basic information", async ({
    page,
  }) => {
    console.log("🚀 Testing basic assistant creation...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Fill required fields
    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "Test Assistant"
    );

    // Select personality (first non-empty option)
    await page.selectOption('select:has(option[value="helpful"])', "helpful");

    // Select template (first available template)
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });

    // Fill description
    await page.fill(
      'textarea[placeholder*="description"]',
      "This is a test assistant for automated testing"
    );

    // Submit form
    await page.click('button:has-text("Create Assistant")');

    // Wait for success message or modal close
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Look for success toast/alert
    await expect(page.locator(".toast, .alert-success, .alert")).toContainText(
      "Assistant created successfully"
    );

    console.log("✅ Basic assistant created successfully");
  });

  test("should create assistant with auto-build enabled", async ({ page }) => {
    console.log("🚀 Testing assistant creation with auto-build...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Fill required fields
    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "Auto-Build Test Assistant"
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });
    await page.fill(
      'textarea[placeholder*="description"]',
      "Testing auto-build functionality"
    );

    // Enable auto-build
    await page.check("#auto-build-checkbox");
    await expect(page.locator("#auto-build-checkbox")).toBeChecked();

    // Submit form
    await page.click('button:has-text("Create Assistant")');

    // Wait for modal to close
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Look for build-specific success message
    await expect(page.locator(".toast, .alert")).toContainText(
      "Build job has been queued"
    );

    console.log("✅ Assistant with auto-build created successfully");
  });

  test("should show different personality options", async ({ page }) => {
    console.log("🚀 Testing personality dropdown options...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Check personality dropdown options
    const personalitySelect = page.locator(
      'select:has(option[value="helpful"])'
    );
    const options = await personalitySelect.locator("option").allTextContents();

    // Verify expected personality options exist
    expect(options).toContain("Helpful");
    expect(options).toContain("Professional");
    expect(options).toContain("Friendly");

    console.log("✅ Personality options loaded correctly");
  });

  test("should show template categories and options", async ({ page }) => {
    console.log("🚀 Testing template dropdown with categories...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Check template dropdown has optgroups
    const templateSelect = page.locator("select:has(optgroup)");
    await expect(templateSelect).toBeVisible();

    // Verify some expected categories exist
    await expect(
      page.locator('optgroup[label="Personal Assistant"]')
    ).toBeVisible();
    await expect(
      page.locator('optgroup[label="Customer Support"]')
    ).toBeVisible();
    await expect(
      page.locator('optgroup[label="Project Management"]')
    ).toBeVisible();

    console.log("✅ Template categories loaded correctly");
  });

  test("should handle client selection (optional field)", async ({ page }) => {
    console.log("🚀 Testing client selection functionality...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Check client dropdown exists and is optional
    const clientSelect = page.locator(
      'select:has(option:has-text("Select a client"))'
    );
    await expect(clientSelect).toBeVisible();

    // Verify "Select a client" option is present (indicating it's optional)
    await expect(
      page.locator('option:has-text("Select a client")')
    ).toBeVisible();

    // Fill required fields and create without selecting client
    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "No Client Assistant"
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });

    // Submit without client selection
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Should succeed without client
    await expect(page.locator(".toast, .alert")).toContainText(
      "Assistant created successfully"
    );

    console.log("✅ Client selection working correctly as optional field");
  });

  test("should update character count for description field", async ({
    page,
  }) => {
    console.log("🚀 Testing description character count...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    const description =
      "This is a test description for character counting functionality.";
    await page.fill('textarea[placeholder*="description"]', description);

    // Look for character count display
    const characterCount = page.locator("text=/\\d+\\/500/");
    await expect(characterCount).toBeVisible();
    await expect(characterCount).toContainText(`${description.length}/500`);

    console.log("✅ Character count working correctly");
  });

  test("should prevent submission when form has errors", async ({ page }) => {
    console.log("🚀 Testing form error prevention...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Fill name but leave required fields empty
    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "Incomplete Assistant"
    );

    // Try to submit
    await page.click('button:has-text("Create Assistant")');

    // Modal should remain open due to validation errors
    await expect(page.locator(".modal.show")).toBeVisible();

    // Submit button should be disabled or form should show errors
    const submitButton = page.locator('button:has-text("Create Assistant")');
    const isDisabled = await submitButton.isDisabled();
    const hasErrors = (await page.locator(".is-invalid").count()) > 0;

    expect(isDisabled || hasErrors).toBeTruthy();

    console.log("✅ Form error prevention working correctly");
  });

  test("should navigate to Build Status tab after auto-build creation", async ({
    page,
  }) => {
    console.log("🚀 Testing navigation to Build Status after auto-build...");

    // First create an assistant with auto-build
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "Build Status Test"
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });
    await page.check("#auto-build-checkbox");

    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Navigate to Build Status tab
    await page.click('[data-testid="nav-build-status"]');

    // Verify Build Status dashboard is visible
    await expect(
      page.locator('h2:has-text("Build Status Dashboard")')
    ).toBeVisible();

    // Should show the build we just created (might be in queue or building)
    await expect(page.locator('.card:has-text("Build")')).toBeVisible();

    console.log("✅ Build Status navigation working correctly");
  });

  test("should close modal when Cancel button is clicked", async ({ page }) => {
    console.log("🚀 Testing modal cancel functionality...");

    // Open modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Click Cancel button
    await page.click('button:has-text("Cancel")');

    // Modal should close
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 5000,
    });
    await expect(page.locator(".modal.show")).not.toBeVisible();

    console.log("✅ Modal cancel functionality working correctly");
  });

  test("should reset form when modal is reopened", async ({ page }) => {
    console.log("🚀 Testing form reset on modal reopen...");

    // Open modal and fill some fields
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      "Test Name"
    );
    await page.fill('textarea[placeholder*="description"]', "Test Description");
    await page.check("#auto-build-checkbox");

    // Close modal
    await page.click('button:has-text("Cancel")');
    await page.waitForSelector(".modal.show", { state: "hidden" });

    // Reopen modal
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    // Verify fields are reset
    await expect(
      page.locator(
        'input[placeholder*="assistant name"], input[placeholder*="name"]'
      )
    ).toHaveValue("");
    await expect(
      page.locator('textarea[placeholder*="description"]')
    ).toHaveValue("");
    await expect(page.locator("#auto-build-checkbox")).not.toBeChecked();

    console.log("✅ Form reset functionality working correctly");
  });
});
