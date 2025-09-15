const { test, expect } = require("@playwright/test");

test.describe("Template Form Validation Tests", () => {
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

  test("should show validation errors for empty required fields", async ({
    page,
  }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Try to submit empty form
    await page.click('[data-testid="submit-template-btn"]');

    // Check for validation errors on required fields
    await expect(
      page.locator('[data-testid="template-name-input"]')
    ).toHaveClass(/is-invalid/);
    await expect(
      page.locator('[data-testid="template-description-input"]')
    ).toHaveClass(/is-invalid/);
    await expect(
      page.locator('[data-testid="template-instructions-input"]')
    ).toHaveClass(/is-invalid/);

    // Check for error messages
    await expect(page.locator(".invalid-feedback")).toHaveCount(3); // Should show 3 error messages
  });

  test("should validate character limits", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Test description character limit (500 chars)
    const longDescription = "A".repeat(501);
    await page.fill(
      '[data-testid="template-description-input"]',
      longDescription
    );
    await page.blur('[data-testid="template-description-input"]');

    await expect(
      page.locator('[data-testid="template-description-input"]')
    ).toHaveClass(/is-invalid/);

    // Test instructions character limit (2000 chars)
    const longInstructions = "B".repeat(2001);
    await page.fill(
      '[data-testid="template-instructions-input"]',
      longInstructions
    );
    await page.blur('[data-testid="template-instructions-input"]');

    await expect(
      page.locator('[data-testid="template-instructions-input"]')
    ).toHaveClass(/is-invalid/);
  });

  test("should validate tags limit (max 10)", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Try to add more than 10 tags
    const tooManyTags =
      "tag1,tag2,tag3,tag4,tag5,tag6,tag7,tag8,tag9,tag10,tag11";
    await page.fill('[data-testid="template-tags-input"]', tooManyTags);
    await page.blur('[data-testid="template-tags-input"]');

    await expect(
      page.locator('[data-testid="template-tags-input"]')
    ).toHaveClass(/is-invalid/);

    // Verify error message about tag limit
    await expect(page.locator("text=Maximum 10 tags allowed")).toBeVisible();
  });

  test("should validate Q&A pairs completeness", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill required basic fields
    await page.fill('[data-testid="template-name-input"]', "Test Template");
    await page.fill(
      '[data-testid="template-description-input"]',
      "Test description"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Fill only question without answer
    await page.fill('[data-testid="qa-question-0"]', "Test question?");
    // Leave answer empty

    await page.click('[data-testid="submit-template-btn"]');

    // Should show Q&A validation error
    await expect(page.locator('[data-testid="qa-answer-0"]')).toHaveClass(
      /is-invalid/
    );
  });

  test("should validate real-time character counting", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Test description character counter
    await page.fill(
      '[data-testid="template-description-input"]',
      "Test description"
    );
    await expect(
      page.locator('[data-testid="description-char-count"]')
    ).toContainText("16/500");

    // Test instructions character counter
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions for the AI assistant"
    );
    await expect(
      page.locator('[data-testid="instructions-char-count"]')
    ).toContainText("37/2000");

    // Test tags counter
    await page.fill(
      '[data-testid="template-tags-input"]',
      "test,validation,form"
    );
    await expect(page.locator('[data-testid="tags-count"]')).toContainText(
      "3/10"
    );
  });

  test("should validate field types and formats", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Test that name field doesn't accept only spaces
    await page.fill('[data-testid="template-name-input"]', "   ");
    await page.blur('[data-testid="template-name-input"]');
    await expect(
      page.locator('[data-testid="template-name-input"]')
    ).toHaveClass(/is-invalid/);

    // Test that tags are properly trimmed and validated
    await page.fill(
      '[data-testid="template-tags-input"]',
      " , , test, , validation, "
    );
    await page.blur('[data-testid="template-tags-input"]');
    // Should clean up to just valid tags
    await expect(page.locator('[data-testid="tags-count"]')).toContainText(
      "2/10"
    );
  });

  test("should validate tools configuration", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Enable a tool that requires API key
    await page.check('[data-testid="tool-web-search-toggle"]');

    // Leave API key empty and try to submit
    await page.fill('[data-testid="template-name-input"]', "Tool Test");
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing tool validation"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    await page.click('[data-testid="submit-template-btn"]');

    // Should show validation error for missing API key
    await expect(
      page.locator('[data-testid="tool-web-search-apikey"]')
    ).toHaveClass(/is-invalid/);
  });

  test("should validate database tool configuration", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Enable database tool
    await page.check('[data-testid="tool-database-toggle"]');

    // Fill basic fields
    await page.fill('[data-testid="template-name-input"]', "Database Test");
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing database validation"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );

    // Leave database config incomplete
    await page.fill('[data-testid="tool-database-host"]', "localhost");
    // Leave port and database name empty

    await page.click('[data-testid="submit-template-btn"]');

    // Should show validation errors for incomplete database config
    await expect(
      page.locator('[data-testid="tool-database-port"]')
    ).toHaveClass(/is-invalid/);
    await expect(
      page.locator('[data-testid="tool-database-database"]')
    ).toHaveClass(/is-invalid/);
  });

  test("should show success message on valid form submission", async ({
    page,
  }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill all required fields correctly
    await page.fill(
      '[data-testid="template-name-input"]',
      "Valid Test Template"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "A valid test template description"
    );
    await page.selectOption(
      '[data-testid="template-category-select"]',
      "general"
    );
    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "professional"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Valid test instructions for the AI assistant"
    );
    await page.fill(
      '[data-testid="template-tags-input"]',
      "test,valid,template"
    );

    // Fill Q&A properly
    await page.fill('[data-testid="qa-question-0"]', "Test question?");
    await page.fill('[data-testid="qa-answer-0"]', "Test answer");

    // Submit the form
    await page.click('[data-testid="submit-template-btn"]');

    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(
      page.locator("text=Template created successfully")
    ).toBeVisible();

    // Modal should close
    await expect(
      page.locator('[data-testid="create-template-modal"]')
    ).not.toBeVisible();
  });

  test("should prevent double submission", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');

    // Fill all required fields
    await page.fill(
      '[data-testid="template-name-input"]',
      "Double Submit Test"
    );
    await page.fill(
      '[data-testid="template-description-input"]',
      "Testing double submission prevention"
    );
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions"
    );
    await page.fill('[data-testid="qa-question-0"]', "Test question?");
    await page.fill('[data-testid="qa-answer-0"]', "Test answer");

    // Submit the form
    await page.click('[data-testid="submit-template-btn"]');

    // Button should become disabled with loading state
    await expect(
      page.locator('[data-testid="submit-template-btn"]')
    ).toBeDisabled();
    await expect(
      page.locator('[data-testid="submit-template-btn"] .spinner-border')
    ).toBeVisible();
  });
});
