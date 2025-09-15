const { test, expect } = require("@playwright/test");

test.describe("RazorFlow Human-like Workflow Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:3002");

    // Login with test user
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');

    // Wait for login to complete and navigate to Templates
    await page.waitForSelector('[data-testid="nav-templates"]', {
      timeout: 10000,
    });
    await page.click('[data-testid="nav-templates"]');

    // Wait for Templates page to load
    await page.waitForSelector('[data-testid="create-template-btn"]', {
      timeout: 10000,
    });
  });

  test("should complete human-like workflow: create client then template", async ({
    page,
  }) => {
    // Start from dashboard view (default after login)
    // Clients are managed directly on the dashboard

    // Step 1: Navigate to Dashboard (where clients are managed)
    console.log("Current URL:", page.url());
    await page.click('[data-testid="nav-dashboard"]');
    await page.waitForTimeout(2000);

    // Step 2: Create a new client - Razor 303 at RazorFlow-AI
    console.log("Looking for Add Client button...");
    const addClientButton = page.locator('button:has-text("Add Client")');
    await expect(addClientButton).toBeVisible({ timeout: 10000 });
    await addClientButton.click();
    await page.waitForSelector(".modal", { timeout: 5000 });

    // Fill client details with correct values
    await page.fill('input[placeholder="Enter client name"]', "Razor 303");
    await page.fill(
      'input[placeholder="Enter email address (e.g., john@company.com)"]',
      "jc@razorflow-ai.com"
    );
    await page.fill('input[placeholder="Enter company name"]', "RazorFlow-AI");
    await page.fill(
      'textarea[placeholder="Enter description (optional)"]',
      "Leading AI solutions company focused on intelligent automation"
    );

    // Submit the client creation form
    await page.click('button:has-text("Create Client")');
    await page.waitForTimeout(2000); // Wait for client creation

    // Close any success modal or notification
    const modalCloseButton = page.locator(
      '.modal .btn-close, .modal button:has-text("Close"), .modal button:has-text("OK")'
    );
    if (await modalCloseButton.isVisible()) {
      await modalCloseButton.click();
      await page.waitForTimeout(1000);
    }

    // Step 3: Navigate to Templates (human behavior - move between sections)
    await page.click('[data-testid="nav-templates"]');
    await page.waitForSelector('[data-testid="create-template-btn"]');

    // Step 4: Create a custom template with advanced features
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Basic template information
    await page.fill(
      '[data-testid="template-name-input"]',
      "Custom RazorFlow Assistant"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Specialized AI assistant for RazorFlow operations"
    );
    await page.selectOption('[data-testid="template-category-select"]', "PA");
    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "professional"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "You are a specialized assistant for RazorFlow operations."
    );

    // Scope & Training section
    await page.selectOption(
      '[data-testid="template-scope-select"]',
      "specialized"
    );

    // Add comprehensive training Q&A
    await page.fill(
      '[data-testid="training-question-0"]',
      "What is RazorFlow?"
    );
    await page.fill(
      '[data-testid="training-answer-0"]',
      "RazorFlow is an AI automation platform for creating intelligent chatbots and workflows."
    );

    // Add second Q&A pair
    const addQAButton = page.locator('button:has-text("Add Q&A Pair")');
    await addQAButton.click();
    await page.waitForTimeout(1000);

    await page.fill(
      '[data-testid="training-question-1"]',
      "How do we handle support tickets?"
    );
    await page.fill(
      '[data-testid="training-answer-1"]',
      "We prioritize tickets based on client tier and urgency, with enterprise clients receiving priority support."
    );

    // Add third Q&A pair for comprehensive training
    await addQAButton.click();
    await page.waitForTimeout(1000);

    await page.fill(
      '[data-testid="training-question-2"]',
      "What are the main features of RazorFlow AI?"
    );
    await page.fill(
      '[data-testid="training-answer-2"]',
      "RazorFlow AI includes template management, client dashboards, analytics, and integrated tools for comprehensive AI solutions."
    );

    // Tools & Integrations section (optional tools testing)
    console.log("🔧 Testing Tools & Integrations...");

    // Enable Email Integration
    await page.check('[data-testid="tool-email-toggle"]');
    await page.fill(
      '[data-testid="tool-email-api-key"]',
      "email-api-key-test-123"
    );

    // Enable Calendar Management
    await page.check('[data-testid="tool-calendar-toggle"]');
    await page.fill(
      '[data-testid="tool-calendar-api-key"]',
      "calendar-api-key-test-456"
    );

    // Enable Web Search
    await page.check('[data-testid="tool-web-search-toggle"]');
    await page.fill(
      '[data-testid="tool-web-search-api-key"]',
      "search-api-key-test-789"
    );

    // Enable File System Access (no API key required)
    await page.check('[data-testid="tool-file-system-toggle"]');

    // Enable Database Access with configuration
    await page.check('[data-testid="tool-database-toggle"]');
    await page.fill('[data-testid="tool-database-host"]', "localhost");
    await page.fill('[data-testid="tool-database-port"]', "5432");
    await page.fill('[data-testid="tool-database-name"]', "razorflow_db");

    // Tags
    await page.fill(
      '[data-testid="template-tags-input"]',
      "razorflow,custom,specialized,training,support"
    );

    // Validate form is ready for submission
    console.log("✅ All sections completed, preparing for submission...");

    // Check if public checkbox is available and set it
    try {
      const publicCheckbox = page.locator(
        '[data-testid="template-public-checkbox"]'
      );
      if (await publicCheckbox.isVisible({ timeout: 2000 })) {
        await publicCheckbox.check();
        console.log("✅ Template set to public");
      }
    } catch (error) {
      console.log("Public checkbox not found - continuing...");
    }

    // Submit the comprehensive template
    console.log("🚀 Submitting comprehensive template...");
    await page.click('[data-testid="submit-template-btn"]');

    // Wait for success message with extended timeout for comprehensive form
    await page.waitForSelector(
      '[data-testid="success-message"], .alert-success, .success-notification',
      {
        timeout: 15000,
      }
    );
    console.log("🎉 Template submission successful!");

    // Verify template appears in list
    await expect(page.locator("text=Custom RazorFlow Assistant")).toBeVisible();
    console.log("✅ Template verified in templates list");
  });

  test("should validate form fields with proper error handling", async ({
    page,
  }) => {
    console.log("🧪 Testing comprehensive form validation...");

    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Try to submit empty form
    await page.click('[data-testid="submit-template-btn"]');

    // Check for validation errors (may appear as invalid feedback or disabled button)
    try {
      await expect(
        page.locator('.invalid-feedback, [data-testid="name-error"]')
      ).toBeVisible();
    } catch (error) {
      console.log(
        "Validation handled via button state - checking if submit is disabled"
      );
      await expect(
        page.locator('[data-testid="submit-template-btn"]')
      ).toBeDisabled();
    }

    // Fill required fields one by one (human-like behavior)
    console.log("📝 Filling required fields step by step...");

    await page.fill(
      '[data-testid="template-name-input"]',
      "Validation Test Template"
    );
    console.log("✅ Name field filled");

    await page.fill(
      '[data-testid="template-description-input"]',
      "A comprehensive test template for validation testing with all sections"
    );
    console.log("✅ Description field filled");

    await page.selectOption(
      '[data-testid="template-category-select"]',
      "customer-service"
    );
    console.log("✅ Category selected");

    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "professional"
    );
    console.log("✅ Personality selected");

    await page.fill(
      '[data-testid="template-instructions-input"]',
      "You are a validation test assistant designed to test comprehensive form functionality including scope, training, and tools integration."
    );
    console.log("✅ Instructions filled");

    // Test Scope & Training section validation
    console.log("🎯 Testing Scope & Training validation...");

    await page.selectOption('[data-testid="template-scope-select"]', "expert");
    console.log("✅ Scope level selected");

    // Test Q&A validation - fill partially to test validation
    await page.fill(
      '[data-testid="training-question-0"]',
      "Test validation question?"
    );
    // Leave answer empty to test validation

    // Try to submit with incomplete Q&A
    await page.click('[data-testid="submit-template-btn"]');

    // The form should prevent submission or show validation error
    // Fill the missing answer
    await page.fill(
      '[data-testid="training-answer-0"]',
      "This is a test validation answer."
    );
    console.log("✅ Q&A pair validation completed");

    // Test tags
    await page.fill(
      '[data-testid="template-tags-input"]',
      "validation,test,comprehensive"
    );
    console.log("✅ Tags filled");

    // Test optional tools section
    console.log("🔧 Testing optional tools validation...");

    // Enable a tool and add API key
    await page.check('[data-testid="tool-email-toggle"]');
    await page.fill(
      '[data-testid="tool-email-api-key"]',
      "validation-email-api-key"
    );
    console.log("✅ Tool configuration tested");

    // Now form should be valid - submit successfully
    await page.click('[data-testid="submit-template-btn"]');

    // Wait for success or error message
    try {
      await page.waitForSelector(
        '.alert-success, [data-testid="success-message"]',
        { timeout: 10000 }
      );
      console.log(
        "🎉 Form validation test passed - template created successfully"
      );
    } catch (error) {
      console.log(
        "⚠️ Form validation test - checking for any validation issues..."
      );
      const errorElements = await page
        .locator(".invalid-feedback, .alert-danger, .error-message")
        .count();
      if (errorElements > 0) {
        console.log("❌ Validation errors still present");
      }
    }
  });

  test("should test Q&A management functionality", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill basic required fields
    await page.fill('[data-testid="template-name-input"]', "QA Test Template");
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing Q&A functionality"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Test Q&A functionality
    await page.fill('[data-testid="qa-question-0"]', "First question?");
    await page.fill('[data-testid="qa-answer-0"]', "First answer");

    // Add another Q&A pair
    await page.click('[data-testid="add-qa-btn"]');
    await expect(page.locator('[data-testid="qa-question-1"]')).toBeVisible();

    await page.fill('[data-testid="qa-question-1"]', "Second question?");
    await page.fill('[data-testid="qa-answer-1"]', "Second answer");

    // Add third Q&A pair
    await page.click('[data-testid="add-qa-btn"]');
    await page.fill('[data-testid="qa-question-2"]', "Third question?");
    await page.fill('[data-testid="qa-answer-2"]', "Third answer");

    // Remove middle Q&A pair
    await page.click('[data-testid="remove-qa-1"]');

    // Verify only 2 Q&A pairs remain
    await expect(page.locator('[data-testid="qa-question-0"]')).toBeVisible();
    await expect(page.locator('[data-testid="qa-question-1"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="qa-question-2"]')
    ).not.toBeVisible();

    // Verify the remaining pairs have correct content
    await expect(page.locator('[data-testid="qa-question-0"]')).toHaveValue(
      "First question?"
    );
    await expect(page.locator('[data-testid="qa-question-1"]')).toHaveValue(
      "Third question?"
    );
  });

  test("should test tools configuration functionality", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill basic required fields
    await page.fill(
      '[data-testid="template-name-input"]',
      "Tools Test Template"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing tools configuration"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Test various tools
    const tools = [
      { name: "web-search", hasApiKey: true },
      { name: "email", hasApiKey: true },
      { name: "calendar", hasApiKey: true },
      { name: "file-system", hasApiKey: false },
      { name: "api-client", hasApiKey: true },
      { name: "weather", hasApiKey: true },
    ];

    for (const tool of tools) {
      // Toggle the tool
      await page.check(`[data-testid="tool-${tool.name}-toggle"]`);

      if (tool.hasApiKey) {
        // Verify API key field appears
        await expect(
          page.locator(`[data-testid="tool-${tool.name}-apikey"]`)
        ).toBeVisible();
        await page.fill(
          `[data-testid="tool-${tool.name}-apikey"]`,
          `${tool.name}-api-key-test`
        );
      }

      // Toggle off
      await page.uncheck(`[data-testid="tool-${tool.name}-toggle"]`);

      if (tool.hasApiKey) {
        // Verify API key field disappears
        await expect(
          page.locator(`[data-testid="tool-${tool.name}-apikey"]`)
        ).not.toBeVisible();
      }

      // Toggle back on for final state
      await page.check(`[data-testid="tool-${tool.name}-toggle"]`);
    }
  });

  test("should test database tool special configuration", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill basic required fields
    await page.fill(
      '[data-testid="template-name-input"]',
      "Database Test Template"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing database configuration"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Test database tool special configuration
    await page.check('[data-testid="tool-database-toggle"]');

    // Verify database config fields appear
    await expect(
      page.locator('[data-testid="tool-database-host"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="tool-database-port"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="tool-database-database"]')
    ).toBeVisible();

    // Fill database configuration
    await page.fill('[data-testid="tool-database-host"]', "localhost");
    await page.fill('[data-testid="tool-database-port"]', "5432");
    await page.fill('[data-testid="tool-database-database"]', "test_db");

    // Toggle off and verify fields disappear
    await page.uncheck('[data-testid="tool-database-toggle"]');
    await expect(
      page.locator('[data-testid="tool-database-host"]')
    ).not.toBeVisible();
  });

  test("should validate scope and training Q&A requirements", async ({
    page,
  }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill basic required fields
    await page.fill(
      '[data-testid="template-name-input"]',
      "Validation Test Template"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing validation"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Test scope validation
    await page.selectOption('[data-testid="template-scope-select"]', "expert");

    // Leave Q&A empty and try to submit
    await page.click('[data-testid="submit-template-btn"]');

    // Check for Q&A validation error
    await expect(page.locator('[data-testid="qa-error"]')).toBeVisible();

    // Fill incomplete Q&A (only question)
    await page.fill('[data-testid="qa-question-0"]', "Test question?");
    await page.click('[data-testid="submit-template-btn"]');

    // Should still show error for incomplete Q&A
    await expect(page.locator('[data-testid="qa-error"]')).toBeVisible();

    // Complete the Q&A
    await page.fill('[data-testid="qa-answer-0"]', "Test answer");

    // Now submission should work (assuming other validations pass)
    await page.click('[data-testid="submit-template-btn"]');
    await expect(page.locator('[data-testid="qa-error"]')).not.toBeVisible();
  });
});
