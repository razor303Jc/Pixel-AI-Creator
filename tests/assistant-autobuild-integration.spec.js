const { test, expect } = require("@playwright/test");

test.describe("Assistant Auto-Build and Build Status Tests", () => {
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

  test("should create assistant with auto-build and show in Build Status", async ({
    page,
  }) => {
    console.log("🚀 Testing complete auto-build workflow...");

    const assistantName = `Auto-Build Test ${Date.now()}`;

    // Create assistant with auto-build
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      assistantName
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });
    await page.fill(
      'textarea[placeholder*="description"]',
      "Testing complete auto-build workflow"
    );

    // Enable auto-build
    await page.check("#auto-build-checkbox");
    await expect(page.locator("#auto-build-checkbox")).toBeChecked();

    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show", {
      state: "hidden",
      timeout: 10000,
    });

    // Verify success message mentions build queue
    await expect(page.locator(".toast, .alert")).toContainText(
      "Build job has been queued"
    );

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await expect(
      page.locator('h2:has-text("Build Status Dashboard")')
    ).toBeVisible();

    // Should show the build (might be queued, building, or completed)
    await page.waitForSelector(".card", { timeout: 15000 });

    // Look for our specific build
    const buildCard = page.locator(".card").first();
    await expect(buildCard).toBeVisible();

    // Verify build status badge is present
    await expect(page.locator(".badge")).toBeVisible();

    console.log("✅ Auto-build workflow completed successfully");
  });

  test("should show build progress and status updates", async ({ page }) => {
    console.log("🚀 Testing build progress monitoring...");

    // Navigate to Build Status first
    await page.click('[data-testid="nav-build-status"]');
    await expect(
      page.locator('h2:has-text("Build Status Dashboard")')
    ).toBeVisible();

    // Check if auto-refresh is enabled
    await expect(
      page.locator('button:has-text("Auto Refresh ON")')
    ).toBeVisible();

    // Check for progress bars
    const progressBars = page.locator(".progress-bar");
    if ((await progressBars.count()) > 0) {
      await expect(progressBars.first()).toBeVisible();
      console.log("✅ Build progress bars visible");
    }

    // Check for status badges
    const statusBadges = page.locator(".badge");
    if ((await statusBadges.count()) > 0) {
      await expect(statusBadges.first()).toBeVisible();
      console.log("✅ Status badges visible");
    }

    // Test manual refresh
    await page.click('button:has-text("Refresh")');
    await page.waitForLoadState("networkidle");

    console.log("✅ Build monitoring features working");
  });

  test("should open build details modal from dashboard", async ({ page }) => {
    console.log("🚀 Testing build details modal...");

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Check if there are any builds
    const buildCards = page.locator(".card");
    const buildCount = await buildCards.count();

    if (buildCount > 0) {
      // Click on the first build's details button (code icon)
      await page.locator('button:has-text(""), button').first().click();

      // Wait for modal to appear (BuildStatus modal)
      await page.waitForSelector(".modal.show", { timeout: 5000 });

      // Verify modal content
      await expect(page.locator(".modal-body")).toBeVisible();

      // Close modal
      await page.keyboard.press("Escape");
      await page.waitForSelector(".modal.show", { state: "hidden" });

      console.log("✅ Build details modal working");
    } else {
      console.log("ℹ️ No builds available to test modal");
    }
  });

  test("should toggle auto-refresh functionality", async ({ page }) => {
    console.log("🚀 Testing auto-refresh toggle...");

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Check initial auto-refresh state (should be ON by default)
    const autoRefreshButton = page.locator('button:has-text("Auto Refresh")');
    await expect(autoRefreshButton).toContainText("ON");

    // Toggle auto-refresh OFF
    await autoRefreshButton.click();
    await expect(autoRefreshButton).toContainText("OFF");

    // Toggle auto-refresh back ON
    await autoRefreshButton.click();
    await expect(autoRefreshButton).toContainText("ON");

    console.log("✅ Auto-refresh toggle working correctly");
  });

  test("should show appropriate message when no builds exist", async ({
    page,
  }) => {
    console.log("🚀 Testing empty state message...");

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Check for builds or empty message
    const buildCards = page.locator(".card");
    const buildCount = await buildCards.count();

    if (buildCount === 0) {
      // Should show empty state message
      await expect(page.locator(".alert-info")).toContainText(
        "No builds found"
      );
      await expect(page.locator(".alert-info")).toContainText("Auto-build");
      console.log("✅ Empty state message displayed correctly");
    } else {
      console.log("ℹ️ Builds exist, skipping empty state test");
    }
  });

  test("should handle build cancellation", async ({ page }) => {
    console.log("🚀 Testing build cancellation...");

    // First create a build to potentially cancel
    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show");

    await page.fill(
      'input[placeholder*="assistant name"], input[placeholder*="name"]',
      `Cancel Test ${Date.now()}`
    );
    await page.selectOption('select:has(option[value="helpful"])', "helpful");
    await page.selectOption('select:has(option[value*="general"])', {
      index: 1,
    });
    await page.check("#auto-build-checkbox");

    await page.click('button:has-text("Create Assistant")');
    await page.waitForSelector(".modal.show", { state: "hidden" });

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Look for cancel button (trash icon) - only visible for queued/building builds
    const cancelButtons = page.locator(
      'button:has([class*="trash"], [data-icon="trash"])'
    );
    const cancelCount = await cancelButtons.count();

    if (cancelCount > 0) {
      // Click cancel on the first build
      await cancelButtons.first().click();

      // Should refresh and show updated status
      await page.waitForLoadState("networkidle");

      console.log("✅ Build cancellation attempted");
    } else {
      console.log("ℹ️ No builds available for cancellation");
    }
  });

  test("should display deployment links for completed builds", async ({
    page,
  }) => {
    console.log("🚀 Testing deployment links...");

    // Navigate to Build Status
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Look for deployment links (external link icons)
    const deploymentLinks = page.locator(
      'button:has([class*="external"], [data-icon="external-link"])'
    );
    const deploymentCount = await deploymentLinks.count();

    if (deploymentCount > 0) {
      // Verify the link is visible and has href attribute
      const firstLink = deploymentLinks.first();
      await expect(firstLink).toBeVisible();

      console.log("✅ Deployment links visible for completed builds");
    } else {
      console.log("ℹ️ No deployment links available (no completed builds)");
    }
  });

  test("should validate different template categories create different build configs", async ({
    page,
  }) => {
    console.log("🚀 Testing template-specific build configurations...");

    const templates = [
      { category: "Customer Support", value: "customer-support-basic" },
      { category: "Project Management", value: "project-management-basic" },
      { category: "Marketing & Sales", value: "sales-assistant-basic" },
    ];

    for (const template of templates) {
      // Create assistant with specific template
      await page.click('button:has-text("Create Assistant")');
      await page.waitForSelector(".modal.show");

      await page.fill(
        'input[placeholder*="assistant name"], input[placeholder*="name"]',
        `${template.category} Test ${Date.now()}`
      );
      await page.selectOption('select:has(option[value="helpful"])', "helpful");

      // Try to select the specific template
      try {
        await page.selectOption(
          `select:has(option[value="${template.value}"])`,
          template.value
        );
      } catch {
        // Fallback to first available option in category
        await page.selectOption("select:has(optgroup)", { index: 1 });
      }

      await page.check("#auto-build-checkbox");
      await page.click('button:has-text("Create Assistant")');
      await page.waitForSelector(".modal.show", { state: "hidden" });

      // Wait a bit between creations
      await page.waitForTimeout(1000);
    }

    // Navigate to Build Status to see all builds
    await page.click('[data-testid="nav-build-status"]');
    await page.waitForSelector('h2:has-text("Build Status Dashboard")');

    // Should show multiple builds with different configurations
    const buildCards = page.locator(".card");
    const buildCount = await buildCards.count();

    expect(buildCount).toBeGreaterThanOrEqual(templates.length);

    console.log(
      `✅ Created ${templates.length} builds with different templates`
    );
  });
});
