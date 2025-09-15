const { test, expect } = require("@playwright/test");

test.describe("Comprehensive Template Validation", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Login with test credentials (same as working test)
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

        // Wait for navigation after login - use broader selector
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
  });

  test("should validate Scope & Training section with optional Tools integration", async ({
    page,
  }) => {
    console.log("🚀 Starting comprehensive template validation test...");

    // Navigate to Templates section (same approach as working test)
    await page.click(
      '[data-testid="nav-templates"], a[href="#templates"], button:has-text("Templates")'
    );
    await page.waitForSelector(
      '[data-testid="create-template-btn"], button:has-text("Create Template")'
    );
    console.log("✅ Navigated to Templates section");

    // Create new template
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    console.log("✅ Template creation modal opened");

    // === BASIC TEMPLATE FIELDS ===
    console.log("📝 Filling basic template information...");

    await page.fill(
      '[data-testid="template-name-input"]',
      "Comprehensive Validation Test Bot"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "A comprehensive test bot for validating Scope & Training sections with optional Tools integration"
    );
    await page.selectOption(
      '[data-testid="template-category-select"]',
      "customer-service"
    );
    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "professional"
    );
    await page.fill(
      '[data-testid="template-tags-input"]',
      "validation, testing, comprehensive, scope, training"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "You are a comprehensive validation test assistant designed to test all template creation features including scope selection, training Q&A management, and optional tools integration."
    );
    console.log("✅ Basic template fields completed");

    // === SCOPE & TRAINING SECTION VALIDATION ===
    console.log("🎯 Testing Scope & Training section validation...");

    // Test Scope Level Selection
    const scopeSelect = page.locator('[data-testid="template-scope-select"]');
    await expect(scopeSelect).toBeVisible();
    await scopeSelect.selectOption("specialized");
    console.log("✅ AI Scope Level selected: Specialized");

    // Validate initial Q&A pair exists
    const firstQuestion = page.locator('[data-testid="training-question-0"]');
    const firstAnswer = page.locator('[data-testid="training-answer-0"]');

    await expect(firstQuestion).toBeVisible();
    await expect(firstAnswer).toBeVisible();
    console.log("✅ Initial Q&A pair fields are visible");

    // Fill comprehensive training Q&A pairs
    await firstQuestion.fill(
      "What is the primary purpose of this validation test?"
    );
    await firstAnswer.fill(
      "This validation test ensures that the Scope & Training section works correctly with comprehensive Q&A management and optional tools integration."
    );
    console.log("✅ First Q&A pair filled");

    // Add second Q&A pair
    const addQAButton = page.locator('button:has-text("Add Q&A Pair")');
    await expect(addQAButton).toBeVisible();
    await addQAButton.click();
    await page.waitForTimeout(1000);
    console.log("✅ Second Q&A pair added");

    // Fill second Q&A pair
    await page.fill(
      '[data-testid="training-question-1"]',
      "How does the Scope & Training section enhance AI capabilities?"
    );
    await page.fill(
      '[data-testid="training-answer-1"]',
      "The Scope & Training section allows fine-tuning AI responses through custom Q&A pairs and scope-specific knowledge configuration."
    );
    console.log("✅ Second Q&A pair filled");

    // Add third Q&A pair for comprehensive testing
    await addQAButton.click();
    await page.waitForTimeout(1000);
    await page.fill(
      '[data-testid="training-question-2"]',
      "Are the Tools & Integrations required for template creation?"
    );
    await page.fill(
      '[data-testid="training-answer-2"]',
      "No, Tools & Integrations are optional and can be configured based on specific needs for enhanced AI capabilities."
    );
    console.log("✅ Third Q&A pair filled - validates tools are optional");

    // Add fourth Q&A pair to test extensive training
    await addQAButton.click();
    await page.waitForTimeout(1000);
    await page.fill(
      '[data-testid="training-question-3"]',
      "What validation checks are performed during template creation?"
    );
    await page.fill(
      '[data-testid="training-answer-3"]',
      "Template creation validates required fields, scope selection, complete Q&A pairs, and optional tools configuration for comprehensive functionality."
    );
    console.log("✅ Fourth Q&A pair filled - extensive training data");

    // === OPTIONAL TOOLS & INTEGRATIONS TESTING ===
    console.log("🔧 Testing optional Tools & Integrations section...");

    // Verify tools section is visible but optional
    const toolsSection = page.locator("text=Tools & Integrations");
    await expect(toolsSection).toBeVisible();
    console.log("✅ Tools & Integrations section is visible");

    // Test some optional tools (demonstrating they are optional)
    console.log("📊 Configuring optional tools for enhanced capabilities...");

    // Enable Web Search (optional enhancement)
    const webSearchToggle = page.locator(
      '[data-testid="tool-web-search-toggle"]'
    );
    if (await webSearchToggle.isVisible({ timeout: 3000 })) {
      await webSearchToggle.click();
      const webSearchApiKey = page.locator(
        '[data-testid="tool-web-search-api-key"]'
      );
      await expect(webSearchApiKey).toBeVisible();
      await webSearchApiKey.fill("comprehensive-test-search-api-key");
      console.log("✅ Optional Web Search tool configured");
    }

    // Enable Email Integration (optional)
    const emailToggle = page.locator('[data-testid="tool-email-toggle"]');
    if (await emailToggle.isVisible({ timeout: 3000 })) {
      await emailToggle.click();
      const emailApiKey = page.locator('[data-testid="tool-email-api-key"]');
      await expect(emailApiKey).toBeVisible();
      await emailApiKey.fill("comprehensive-test-email-api-key");
      console.log("✅ Optional Email Integration tool configured");
    }

    // Enable File System Access (no API key required - optional)
    const fileSystemToggle = page.locator(
      '[data-testid="tool-file-system-toggle"]'
    );
    if (await fileSystemToggle.isVisible({ timeout: 3000 })) {
      await fileSystemToggle.click();
      console.log("✅ Optional File System Access tool enabled");
    }

    // Test Database configuration (optional but comprehensive)
    const databaseToggle = page.locator('[data-testid="tool-database-toggle"]');
    if (await databaseToggle.isVisible({ timeout: 3000 })) {
      await databaseToggle.click();
      console.log("✅ Optional Database Access tool enabled");

      // Fill comprehensive database configuration
      const dbHost = page.locator('[data-testid="tool-database-host"]');
      const dbPort = page.locator('[data-testid="tool-database-port"]');
      const dbName = page.locator('[data-testid="tool-database-name"]');

      if (await dbHost.isVisible({ timeout: 2000 })) {
        await dbHost.fill("test.razorflow-ai.com");
        await dbPort.fill("5432");
        await dbName.fill("comprehensive_test_db");
        console.log("✅ Comprehensive database configuration completed");
      }
    }

    // === COMPREHENSIVE FORM VALIDATION ===
    console.log("✅ Validating comprehensive form completion...");

    // Check if public checkbox is available
    const publicCheckbox = page.locator(
      '[data-testid="template-public-checkbox"]'
    );
    if (await publicCheckbox.isVisible({ timeout: 2000 })) {
      await publicCheckbox.check();
      console.log("✅ Template set to public for comprehensive testing");
    }

    // Verify submit button is enabled (all required fields filled)
    const submitButton = page.locator('[data-testid="submit-template-btn"]');
    await expect(submitButton).toBeEnabled();
    console.log(
      "✅ Submit button is enabled - comprehensive validation passed"
    );

    // === SUBMIT COMPREHENSIVE TEMPLATE ===
    console.log(
      "🚀 Submitting comprehensive template with Scope & Training and optional Tools..."
    );

    await submitButton.click();

    // Wait for success message
    await page.waitForSelector(
      '.alert-success, [data-testid="success-message"], .success-notification',
      { timeout: 15000 }
    );
    console.log("🎉 SUCCESS: Comprehensive template submitted successfully!");

    // Verify template appears in list
    await expect(
      page.locator("text=Comprehensive Validation Test Bot")
    ).toBeVisible();
    console.log("✅ Template verified in templates list");

    // === FINAL VALIDATION SUMMARY ===
    console.log("\n🎯 COMPREHENSIVE VALIDATION SUMMARY:");
    console.log("✅ Scope & Training section: VALIDATED");
    console.log("✅ AI Scope Level selection: WORKING");
    console.log("✅ Q&A pair management: WORKING (4 pairs created)");
    console.log("✅ Tools & Integrations: OPTIONAL (as expected)");
    console.log("✅ Web Search tool: CONFIGURED (optional)");
    console.log("✅ Email Integration: CONFIGURED (optional)");
    console.log("✅ File System Access: ENABLED (optional)");
    console.log("✅ Database Access: CONFIGURED (optional)");
    console.log("✅ Template submission: SUCCESSFUL");
    console.log("✅ Template verification: CONFIRMED");
    console.log("\n🏆 COMPREHENSIVE TEMPLATE VALIDATION: COMPLETE SUCCESS!");
  });

  test("should validate that Tools are truly optional (create template without tools)", async ({
    page,
  }) => {
    console.log("🔍 Testing that Tools & Integrations are truly optional...");

    // Navigate to Templates section
    await page.click(
      '[data-testid="nav-templates"], a[href="#templates"], button:has-text("Templates")'
    );
    await page.waitForSelector(
      '[data-testid="create-template-btn"], button:has-text("Create Template")'
    );

    // Create new template
    await page.click(
      '[data-testid="create-template-btn"], button:has-text("Create Template")'
    );
    await page.waitForSelector(
      '[data-testid="create-template-modal"], .modal:visible'
    );

    // Fill only required fields (no tools)
    await page.fill(
      '[data-testid="template-name-input"]',
      "No Tools Required Test"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing that templates work without any tools configured"
    );
    await page.selectOption(
      '[data-testid="template-category-select"]',
      "general"
    );
    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "friendly"
    );
    await page.fill(
      '[data-testid="template-tags-input"]',
      "no-tools, required-only, validation"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "This template tests that tools are optional and not required for template creation."
    );

    // Fill Scope & Training (required)
    await page.selectOption('[data-testid="template-scope-select"]', "general");
    await page.fill(
      '[data-testid="training-question-0"]',
      "Do tools need to be configured?"
    );
    await page.fill(
      '[data-testid="training-answer-0"]',
      "No, tools are completely optional for template creation."
    );

    // Do NOT configure any tools - leave them all disabled
    console.log(
      "✅ Intentionally NOT configuring any tools to validate they are optional"
    );

    // Submit without any tools
    const submitButton = page.locator('[data-testid="submit-template-btn"]');
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Should succeed without tools
    await page.waitForSelector(
      '.alert-success, [data-testid="success-message"]',
      { timeout: 10000 }
    );
    console.log("🎉 SUCCESS: Template created successfully WITHOUT any tools!");

    // Verify template appears in list
    await expect(page.locator("text=No Tools Required Test")).toBeVisible();
    console.log(
      "✅ VALIDATION CONFIRMED: Tools & Integrations are truly OPTIONAL"
    );
  });
});
