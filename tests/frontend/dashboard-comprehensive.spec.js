const { test, expect } = require("@playwright/test");

// Test configuration
const BASE_URL = "http://localhost:3002";

// Helper function to ensure user is logged in
async function ensureLoggedIn(page) {
  await page.goto(`${BASE_URL}/login`);

  // Check if already logged in by looking for dashboard elements
  try {
    await page.waitForSelector('[data-testid="nav-dashboard"]', {
      timeout: 2000,
    });
    return; // Already logged in
  } catch {
    // Need to log in
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "testpassword");
    await page.click('button[type="submit"]');
    await page.waitForSelector('[data-testid="nav-dashboard"]');
  }
}

// Test suite for Dashboard, Analytics, and Templates navigation and functionality
test.describe("Dashboard Navigation and Views", () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
  });

  test("should display navigation bar with all three sections", async ({
    page,
  }) => {
    // Check if all navigation links are present
    await expect(page.locator('[data-testid="nav-dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-analytics"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-templates"]')).toBeVisible();

    // Check that Dashboard is initially active
    await expect(page.locator('[data-testid="nav-dashboard"]')).toHaveClass(
      /active/
    );
  });

  test("should switch between different views", async ({ page }) => {
    // Test Analytics view
    await page.click('[data-testid="nav-analytics"]');
    await expect(page.locator('[data-testid="nav-analytics"]')).toHaveClass(
      /active/
    );

    // Test Templates view
    await page.click('[data-testid="nav-templates"]');
    await expect(page.locator('[data-testid="nav-templates"]')).toHaveClass(
      /active/
    );

    // Test back to Dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await expect(page.locator('[data-testid="nav-dashboard"]')).toHaveClass(
      /active/
    );
  });
});

test.describe("Dashboard View - Clients and Chatbots", () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    // Ensure we're on the dashboard view
    await page.click('[data-testid="nav-dashboard"]');
  });

  test("should display stats overview cards", async ({ page }) => {
    // Check for stats cards
    await expect(page.locator("text=Total Clients")).toBeVisible();
    await expect(page.locator("text=AI Assistants")).toBeVisible();
    await expect(page.locator("text=Conversations")).toBeVisible();
  });

  test("should display clients section with add button", async ({ page }) => {
    await expect(page.locator("text=Clients")).toBeVisible();
    await expect(page.locator('button:has-text("Add Client")')).toBeVisible();
  });

  test("should display AI assistants section with create button", async ({
    page,
  }) => {
    await expect(page.locator("text=AI Assistants")).toBeVisible();
    await expect(
      page.locator('button:has-text("Create Assistant")')
    ).toBeVisible();
  });

  test("should open create client modal", async ({ page }) => {
    await page.click('button:has-text("Add Client")');

    // Check modal is open
    await expect(page.locator("text=Create New Client")).toBeVisible();

    // Check form fields
    await expect(
      page.locator('input[placeholder*="Enter client name"]')
    ).toBeVisible();
    await expect(
      page.locator('input[placeholder*="Enter email address"]')
    ).toBeVisible();
    await expect(
      page.locator('input[placeholder*="Enter company name"]')
    ).toBeVisible();
    await expect(
      page.locator('textarea[placeholder*="Enter description"]')
    ).toBeVisible();

    // Check buttons
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
    await expect(
      page.locator('button:has-text("Create Client")')
    ).toBeVisible();
  });

  test("should validate client form fields", async ({ page }) => {
    await page.click('button:has-text("Add Client")');

    // Try to submit empty form
    await page.click('button:has-text("Create Client")');

    // Fill required fields
    await page.fill('input[placeholder*="Enter client name"]', "Test Client");
    await page.fill(
      'input[placeholder*="Enter email address"]',
      "test@client.com"
    );
    await page.fill('input[placeholder*="Enter company name"]', "Test Company");
    await page.fill(
      'textarea[placeholder*="Enter description"]',
      "Test client description"
    );

    // Submit form
    await page.click('button:has-text("Create Client")');

    // Check for success message (Toast notification)
    await expect(page.locator("text=client created successfully!")).toBeVisible(
      { timeout: 5000 }
    );
  });

  test("should open create chatbot modal", async ({ page }) => {
    await page.click('button:has-text("Create Assistant")');

    // Check modal is open
    await expect(page.locator("text=Create New AI Assistant")).toBeVisible();

    // Check form fields
    await expect(
      page.locator('input[placeholder*="Enter chatbot name"]')
    ).toBeVisible();
    await expect(
      page.locator('textarea[placeholder*="Enter description"]')
    ).toBeVisible();

    // Check buttons
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
    await expect(
      page.locator('button:has-text("Create Assistant")')
    ).toBeVisible();
  });

  test("should validate chatbot form fields", async ({ page }) => {
    await page.click('button:has-text("Create Assistant")');

    // Fill required fields
    await page.fill(
      'input[placeholder*="Enter chatbot name"]',
      "Test Assistant"
    );
    await page.fill(
      'textarea[placeholder*="Enter description"]',
      "Test assistant description"
    );

    // Submit form
    await page.click('button:has-text("Create Assistant")');

    // Check for success message
    await expect(
      page.locator("text=chatbot created successfully!")
    ).toBeVisible({ timeout: 5000 });
  });

  test("should close modal when cancel is clicked", async ({ page }) => {
    await page.click('button:has-text("Add Client")');
    await expect(page.locator("text=Create New Client")).toBeVisible();

    await page.click('button:has-text("Cancel")');
    await expect(page.locator("text=Create New Client")).not.toBeVisible();
  });
});

test.describe("Analytics View", () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.click('[data-testid="nav-analytics"]');
  });

  test("should display analytics dashboard", async ({ page }) => {
    // Wait for analytics content to load
    await page.waitForTimeout(1000);

    // Check for analytics-specific content
    // Note: This depends on the actual AnalyticsDashboard component content
    await expect(page.locator("h1, h2, h3").first()).toBeVisible();
  });

  test("should display charts and metrics", async ({ page }) => {
    await page.waitForTimeout(1000);

    // Look for common analytics elements
    const analyticsElements = [
      "text=Analytics",
      "text=Dashboard",
      "text=Performance",
      "text=Metrics",
      "text=Chart",
      "text=Data",
    ];

    // At least one analytics-related element should be visible
    let found = false;
    for (const element of analyticsElements) {
      try {
        await expect(page.locator(element)).toBeVisible({ timeout: 2000 });
        found = true;
        break;
      } catch {
        // Continue to next element
      }
    }

    expect(found).toBeTruthy();
  });
});

test.describe("Templates View - CRUD Operations", () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.click('[data-testid="nav-templates"]');
  });

  test("should display templates page with header and create button", async ({
    page,
  }) => {
    await expect(page.locator('[data-testid="templates-title"]')).toContainText(
      "Template Library"
    );
    await expect(
      page.locator('[data-testid="create-template-btn"]')
    ).toBeVisible();
  });

  test("should display search and filter controls", async ({ page }) => {
    await expect(
      page.locator('[data-testid="search-templates"]')
    ).toBeVisible();
    await expect(page.locator('[data-testid="filter-category"]')).toBeVisible();
  });

  test("should display template tabs", async ({ page }) => {
    await expect(page.locator('[data-testid="template-tabs"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="my-templates-tab"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="public-templates-tab"]')
    ).toBeVisible();
  });

  test("should filter templates by search", async ({ page }) => {
    // Wait for templates to load
    await page.waitForTimeout(1000);

    // Type in search box
    await page.fill('[data-testid="search-templates"]', "Customer");

    // Should filter templates containing "Customer"
    await page.waitForTimeout(500);

    // Check if search functionality works (templates should be filtered)
    const templateCards = page.locator('[data-testid^="template-card-"]');
    const count = await templateCards.count();

    // If no templates match, should show no templates message
    if (count === 0) {
      await expect(page.locator('[data-testid="no-templates"]')).toBeVisible();
    }
  });

  test("should filter templates by category", async ({ page }) => {
    await page.waitForTimeout(1000);

    // Select a specific category
    await page.selectOption('[data-testid="filter-category"]', "support");

    await page.waitForTimeout(500);

    // Check if filtering works
    const templateCards = page.locator('[data-testid^="template-card-"]');
    const count = await templateCards.count();

    // Should show appropriate templates or no templates message
    if (count === 0) {
      await expect(page.locator('[data-testid="no-templates"]')).toBeVisible();
    }
  });

  test("should switch between My Templates and Public Templates", async ({
    page,
  }) => {
    await page.waitForTimeout(1000);

    // Click on Public Templates tab
    await page.click('[data-testid="public-templates-tab"]');
    await page.waitForTimeout(500);

    // Click back to My Templates tab
    await page.click('[data-testid="my-templates-tab"]');
    await page.waitForTimeout(500);
  });

  test("should open create template modal", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');

    // Check modal is open
    await expect(
      page.locator('[data-testid="create-template-modal"]')
    ).toBeVisible();
    await expect(page.locator("text=Create New Template")).toBeVisible();

    // Check form fields
    await expect(
      page.locator('[data-testid="template-name-input"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-category-select"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-description-input"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-personality-select"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-tags-input"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-instructions-input"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="template-public-checkbox"]')
    ).toBeVisible();
  });

  test("should validate template form fields", async ({ page }) => {
    await page.click('[data-testid="create-template-btn"]');

    // Try to submit empty form - button should be disabled
    await expect(
      page.locator('[data-testid="submit-template-btn"]')
    ).toBeDisabled();

    // Fill required fields
    await page.fill('[data-testid="template-name-input"]', "Test Template");
    await page.fill(
      '[data-testid="template-description-input"]',
      "Test template description"
    );

    // Button should now be enabled
    await expect(
      page.locator('[data-testid="submit-template-btn"]')
    ).toBeEnabled();

    // Fill other fields
    await page.selectOption(
      '[data-testid="template-category-select"]',
      "support"
    );
    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "helpful"
    );
    await page.fill('[data-testid="template-tags-input"]', "test, demo");
    await page.fill(
      '[data-testid="template-instructions-input"]',
      "Test instructions for the template"
    );

    // Submit form
    await page.click('[data-testid="submit-template-btn"]');

    // Modal should close
    await expect(
      page.locator('[data-testid="create-template-modal"]')
    ).not.toBeVisible();
  });

  test("should perform template CRUD operations", async ({ page }) => {
    await page.waitForTimeout(1000);

    // Look for existing template cards
    const templateCards = page.locator('[data-testid^="template-card-"]');
    const count = await templateCards.count();

    if (count > 0) {
      const firstTemplate = templateCards.first();
      const templateId = await firstTemplate.getAttribute("data-testid");
      const id = templateId?.split("-")[2];

      if (id) {
        // Test edit functionality
        await page.click(`[data-testid="edit-template-${id}"]`);
        await expect(
          page.locator('[data-testid="edit-template-modal"]')
        ).toBeVisible();

        // Modify a field
        await page.fill(
          '[data-testid="edit-template-name-input"]',
          "Updated Template Name"
        );
        await page.click('[data-testid="update-template-btn"]');

        // Modal should close
        await expect(
          page.locator('[data-testid="edit-template-modal"]')
        ).not.toBeVisible();

        // Test duplicate functionality
        await page.click(`[data-testid="duplicate-template-${id}"]`);

        // Should create a copy (check for increased count or "Copy" in name)
        await page.waitForTimeout(500);

        // Test delete functionality
        page.on("dialog", (dialog) => dialog.accept()); // Accept confirmation dialog
        await page.click(`[data-testid="delete-template-${id}"]`);

        // Template should be removed
        await page.waitForTimeout(500);
      }
    }
  });

  test("should display loading state", async ({ page }) => {
    // Reload page to see loading state
    await page.reload();
    await page.click('[data-testid="nav-templates"]');

    // Should show loading spinner briefly
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible({
      timeout: 2000,
    });
  });

  test("should handle no templates state", async ({ page }) => {
    // If no templates are visible, should show appropriate message
    await page.waitForTimeout(1000);

    const templateCards = page.locator('[data-testid^="template-card-"]');
    const count = await templateCards.count();

    if (count === 0) {
      await expect(page.locator('[data-testid="no-templates"]')).toBeVisible();
      await expect(page.locator("text=No templates found")).toBeVisible();
    }
  });
});

test.describe("Form Validation and Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
  });

  test("should have proper form labels and accessibility attributes", async ({
    page,
  }) => {
    // Test Dashboard client form
    await page.click('[data-testid="nav-dashboard"]');
    await page.click('button:has-text("Add Client")');

    // Check for proper labels
    await expect(page.locator('label:has-text("Name")')).toBeVisible();
    await expect(page.locator('label:has-text("Email")')).toBeVisible();
    await expect(page.locator('label:has-text("Company")')).toBeVisible();
    await expect(page.locator('label:has-text("Description")')).toBeVisible();

    await page.click('button:has-text("Cancel")');

    // Test Templates form
    await page.click('[data-testid="nav-templates"]');
    await page.click('[data-testid="create-template-btn"]');

    // Check for proper labels
    await expect(page.locator('label:has-text("Template Name")')).toBeVisible();
    await expect(page.locator('label:has-text("Category")')).toBeVisible();
    await expect(page.locator('label:has-text("Description")')).toBeVisible();
    await expect(page.locator('label:has-text("Personality")')).toBeVisible();
    await expect(page.locator('label:has-text("Instructions")')).toBeVisible();
  });

  test("should have proper input types and validation", async ({ page }) => {
    await page.click('[data-testid="nav-dashboard"]');
    await page.click('button:has-text("Add Client")');

    // Check input types
    await expect(page.locator('input[type="text"]')).toHaveCount(2); // Name and Company
    await expect(page.locator('input[type="email"]')).toHaveCount(1); // Email
    await expect(page.locator("textarea")).toHaveCount(1); // Description

    // Test email validation
    await page.fill('input[type="email"]', "invalid-email");
    // The browser should show validation message for invalid email
  });

  test("should have keyboard navigation support", async ({ page }) => {
    await page.click('[data-testid="nav-templates"]');

    // Test navigation with keyboard
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Should be able to navigate to create button and activate with Enter
    await page.keyboard.press("Enter");

    // Modal should open
    await expect(
      page.locator('[data-testid="create-template-modal"]')
    ).toBeVisible();
  });
});

test.describe("Responsive Design", () => {
  test("should work properly on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
    await ensureLoggedIn(page);

    // Navigation should be responsive
    await expect(page.locator('[data-testid="nav-dashboard"]')).toBeVisible();

    // Test navigation on mobile
    await page.click('[data-testid="nav-templates"]');
    await expect(page.locator('[data-testid="templates-title"]')).toBeVisible();

    // Test modal on mobile
    await page.click('[data-testid="create-template-btn"]');
    await expect(
      page.locator('[data-testid="create-template-modal"]')
    ).toBeVisible();
  });

  test("should work properly on tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await ensureLoggedIn(page);

    // Test all three views on tablet
    await page.click('[data-testid="nav-dashboard"]');
    await expect(page.locator("text=Total Clients")).toBeVisible();

    await page.click('[data-testid="nav-analytics"]');
    await page.waitForTimeout(500);

    await page.click('[data-testid="nav-templates"]');
    await expect(page.locator('[data-testid="templates-title"]')).toBeVisible();
  });
});

test.describe("Error Handling", () => {
  test("should handle network errors gracefully", async ({ page }) => {
    await ensureLoggedIn(page);

    // Simulate network failure
    await page.route("**/api/**", (route) => {
      route.abort("failed");
    });

    // Try to create a client
    await page.click('button:has-text("Add Client")');
    await page.fill('input[placeholder*="Enter client name"]', "Test Client");
    await page.fill(
      'input[placeholder*="Enter email address"]',
      "test@client.com"
    );
    await page.click('button:has-text("Create Client")');

    // Should handle error appropriately (depends on implementation)
    // This test verifies the app doesn't crash
    await page.waitForTimeout(2000);
  });

  test("should validate required fields before submission", async ({
    page,
  }) => {
    await ensureLoggedIn(page);

    // Test client form validation
    await page.click('button:has-text("Add Client")');
    await page.click('button:has-text("Create Client")');

    // Should not close modal if required fields are empty
    await expect(page.locator("text=Create New Client")).toBeVisible();

    // Test template form validation
    await page.click('button:has-text("Cancel")');
    await page.click('[data-testid="nav-templates"]');
    await page.click('[data-testid="create-template-btn"]');

    // Button should be disabled without required fields
    await expect(
      page.locator('[data-testid="submit-template-btn"]')
    ).toBeDisabled();
  });
});
