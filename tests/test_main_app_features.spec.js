/**
 * Comprehensive Playwright Tests for Main App Features
 * Tests core functionality without authentication (bypassed)
 * Visual tests that you can watch in action
 */

import { test, expect } from "@playwright/test";

// Test configuration
const BASE_URL = "http://localhost:3002";
const VIEWPORT_SIZE = { width: 1280, height: 720 };

test.describe("Main App Features - Visual Testing Suite", () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport for consistent testing
    await page.setViewportSize(VIEWPORT_SIZE);

    // Navigate to the main app (auth bypassed)
    await page.goto(BASE_URL);

    // Wait for the main dashboard to load
    await page.waitForSelector('[data-testid="dashboard-container"]', {
      timeout: 10000,
    });

    // Add a small delay for visual effect
    await page.waitForTimeout(1000);
  });

  test("Dashboard Loading and Navigation", async ({ page }) => {
    console.log("🚀 Testing Dashboard Loading and Navigation...");

    // Check if dashboard loads properly
    await expect(page.locator("h1")).toContainText("Pixel AI Creator");

    // Check navigation elements
    await expect(page.locator("nav")).toBeVisible();
    await expect(page.getByText("Dashboard")).toBeVisible();
    await expect(page.getByText("Analytics")).toBeVisible();
    await expect(page.getByText("Templates")).toBeVisible();

    // Test navigation clicks with visual delays
    console.log("📊 Clicking Analytics...");
    await page.getByText("Analytics").click();
    await page.waitForTimeout(1500);

    console.log("📋 Clicking Templates...");
    await page.getByText("Templates").click();
    await page.waitForTimeout(1500);

    console.log("🏠 Returning to Dashboard...");
    await page.getByText("Dashboard").click();
    await page.waitForTimeout(1500);

    console.log("✅ Navigation test completed!");
  });

  test("Client Management Features", async ({ page }) => {
    console.log("👥 Testing Client Management Features...");

    // Look for client section
    await expect(page.getByText("Clients")).toBeVisible();

    // Find and click "Create Client" button
    const createClientBtn = page
      .locator("button")
      .filter({ hasText: /Create.*Client|Add.*Client|\+.*Client/i })
      .first();

    if (await createClientBtn.isVisible()) {
      console.log("➕ Opening Create Client modal...");
      await createClientBtn.click();
      await page.waitForTimeout(2000);

      // Check if modal opened
      const modal = page.locator(".modal");
      if (await modal.isVisible()) {
        console.log("📝 Filling client form...");

        // Fill out client form
        await page.fill(
          'input[placeholder*="name" i], input[name*="name" i]',
          "Test Client Company"
        );
        await page.waitForTimeout(500);

        await page.fill(
          'input[placeholder*="email" i], input[name*="email" i]',
          "test@client.com"
        );
        await page.waitForTimeout(500);

        await page.fill(
          'input[placeholder*="company" i], input[name*="company" i]',
          "Test Corporation"
        );
        await page.waitForTimeout(500);

        // Look for description field
        const descField = page
          .locator('textarea, input[placeholder*="description" i]')
          .first();
        if (await descField.isVisible()) {
          await descField.fill("A test client for demonstration purposes");
          await page.waitForTimeout(500);
        }

        console.log("💾 Attempting to save client...");

        // Try to submit (might fail due to backend, but we can see the UI)
        const submitBtn = page
          .locator("button")
          .filter({ hasText: /save|create|submit/i })
          .first();
        if (await submitBtn.isVisible()) {
          await submitBtn.click();
          await page.waitForTimeout(2000);
        }

        // Close modal if still open
        const closeBtn = page
          .locator("button")
          .filter({ hasText: /close|cancel/i })
          .first();
        if (await closeBtn.isVisible()) {
          await closeBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    }

    console.log("✅ Client management test completed!");
  });

  test("Chatbot Creation Features", async ({ page }) => {
    console.log("🤖 Testing Chatbot Creation Features...");

    // Look for chatbot section
    await expect(page.getByText("Chatbots")).toBeVisible();

    // Find and click "Create Chatbot" button
    const createBotBtn = page
      .locator("button")
      .filter({ hasText: /Create.*Bot|Add.*Bot|\+.*Bot|New.*Bot/i })
      .first();

    if (await createBotBtn.isVisible()) {
      console.log("➕ Opening Create Chatbot modal...");
      await createBotBtn.click();
      await page.waitForTimeout(2000);

      // Check if modal opened
      const modal = page.locator(".modal");
      if (await modal.isVisible()) {
        console.log("📝 Filling chatbot form...");

        // Fill out chatbot form
        await page.fill(
          'input[placeholder*="name" i], input[name*="name" i]',
          "Demo Support Bot"
        );
        await page.waitForTimeout(500);

        // Look for type/purpose field
        const typeField = page
          .locator('select, input[placeholder*="type" i]')
          .first();
        if (await typeField.isVisible()) {
          if ((await typeField.locator("option").count()) > 0) {
            await typeField.selectOption({ index: 1 });
          } else {
            await typeField.fill("Customer Support");
          }
          await page.waitForTimeout(500);
        }

        // Look for description field
        const descField = page
          .locator('textarea, input[placeholder*="description" i]')
          .first();
        if (await descField.isVisible()) {
          await descField.fill(
            "A demonstration chatbot for customer support tasks"
          );
          await page.waitForTimeout(500);
        }

        // Look for complexity/features selection
        const complexityField = page
          .locator(
            'select[name*="complexity" i], input[placeholder*="complexity" i]'
          )
          .first();
        if (await complexityField.isVisible()) {
          if ((await complexityField.locator("option").count()) > 0) {
            await complexityField.selectOption({ index: 1 });
          }
          await page.waitForTimeout(500);
        }

        console.log("💾 Attempting to create chatbot...");

        // Try to submit
        const submitBtn = page
          .locator("button")
          .filter({ hasText: /save|create|submit/i })
          .first();
        if (await submitBtn.isVisible()) {
          await submitBtn.click();
          await page.waitForTimeout(2000);
        }

        // Close modal if still open
        const closeBtn = page
          .locator("button")
          .filter({ hasText: /close|cancel/i })
          .first();
        if (await closeBtn.isVisible()) {
          await closeBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    }

    console.log("✅ Chatbot creation test completed!");
  });

  test("Dashboard Statistics and Cards", async ({ page }) => {
    console.log("📊 Testing Dashboard Statistics and Cards...");

    // Look for stat cards
    const cards = page.locator(".card");
    const cardCount = await cards.count();

    console.log(`📋 Found ${cardCount} dashboard cards`);

    // Test each visible card
    for (let i = 0; i < Math.min(cardCount, 6); i++) {
      const card = cards.nth(i);
      if (await card.isVisible()) {
        console.log(`🔍 Examining card ${i + 1}...`);

        // Highlight the card
        await card.hover();
        await page.waitForTimeout(500);

        // Check for interactive elements
        const buttons = card.locator("button");
        const buttonCount = await buttons.count();

        if (buttonCount > 0) {
          console.log(
            `🖱️ Found ${buttonCount} interactive buttons in card ${i + 1}`
          );

          // Click first button if safe (view, more info, etc.)
          const firstBtn = buttons.first();
          const btnText = await firstBtn.textContent();

          if (btnText && !btnText.toLowerCase().includes("delete")) {
            await firstBtn.click();
            await page.waitForTimeout(1000);

            // If a modal opened, close it
            const modal = page.locator(".modal");
            if (await modal.isVisible()) {
              const closeBtn = modal
                .locator("button")
                .filter({ hasText: /close|cancel/i })
                .first();
              if (await closeBtn.isVisible()) {
                await closeBtn.click();
                await page.waitForTimeout(500);
              }
            }
          }
        }
      }
    }

    console.log("✅ Dashboard statistics test completed!");
  });

  test("Responsive Design and Mobile View", async ({ page }) => {
    console.log("📱 Testing Responsive Design...");

    // Test tablet view
    console.log("📱 Switching to tablet view...");
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(2000);

    // Check if navigation collapses
    await expect(page.locator("nav")).toBeVisible();

    // Test mobile view
    console.log("📱 Switching to mobile view...");
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(2000);

    // Check if content is still accessible
    await expect(page.locator("h1")).toBeVisible();

    // Test hamburger menu if present
    const hamburger = page.locator(
      'button[data-bs-toggle="collapse"], .navbar-toggler'
    );
    if (await hamburger.isVisible()) {
      console.log("🍔 Testing hamburger menu...");
      await hamburger.click();
      await page.waitForTimeout(1000);
    }

    // Return to desktop view
    console.log("🖥️ Returning to desktop view...");
    await page.setViewportSize(VIEWPORT_SIZE);
    await page.waitForTimeout(1000);

    console.log("✅ Responsive design test completed!");
  });

  test("Search and Filter Functionality", async ({ page }) => {
    console.log("🔍 Testing Search and Filter Functionality...");

    // Look for search inputs
    const searchInputs = page.locator(
      'input[placeholder*="search" i], input[type="search"]'
    );
    const searchCount = await searchInputs.count();

    if (searchCount > 0) {
      console.log(`🔍 Found ${searchCount} search inputs`);

      for (let i = 0; i < searchCount; i++) {
        const searchInput = searchInputs.nth(i);
        if (await searchInput.isVisible()) {
          console.log(`🔍 Testing search input ${i + 1}...`);

          await searchInput.click();
          await searchInput.fill("test");
          await page.waitForTimeout(1000);

          await searchInput.clear();
          await page.waitForTimeout(500);
        }
      }
    }

    // Look for filter dropdowns
    const filterSelects = page.locator("select, .dropdown-toggle");
    const filterCount = await filterSelects.count();

    if (filterCount > 0) {
      console.log(`🎛️ Found ${filterCount} filter controls`);

      for (let i = 0; i < Math.min(filterCount, 3); i++) {
        const filter = filterSelects.nth(i);
        if (await filter.isVisible()) {
          console.log(`🎛️ Testing filter ${i + 1}...`);

          await filter.click();
          await page.waitForTimeout(1000);

          // If it's a select, try selecting an option
          if ((await filter.locator("option").count()) > 0) {
            await filter.selectOption({ index: 1 });
            await page.waitForTimeout(1000);
          }
        }
      }
    }

    console.log("✅ Search and filter test completed!");
  });

  test("Data Loading and Error States", async ({ page }) => {
    console.log("⏳ Testing Data Loading States...");

    // Refresh page to see loading states
    await page.reload();

    // Look for loading spinners
    const spinners = page.locator(
      '.spinner-border, .spinner-grow, [data-testid*="loading"]'
    );
    if (await spinners.first().isVisible({ timeout: 2000 })) {
      console.log("⏳ Loading spinners detected");
      await page.waitForTimeout(2000);
    }

    // Wait for content to load
    await page.waitForSelector(
      '[data-testid="dashboard-container"], .container',
      {
        timeout: 10000,
      }
    );

    // Look for error states or empty states
    const errorMessages = page.locator(
      '.alert-danger, .error, [data-testid*="error"]'
    );
    const emptyStates = page.locator('[data-testid*="empty"], .empty-state');

    if (await errorMessages.first().isVisible({ timeout: 1000 })) {
      console.log("⚠️ Error states detected");
    }

    if (await emptyStates.first().isVisible({ timeout: 1000 })) {
      console.log("📭 Empty states detected");
    }

    console.log("✅ Loading states test completed!");
  });

  test("UI Component Interactions", async ({ page }) => {
    console.log("🖱️ Testing UI Component Interactions...");

    // Test button hovers and clicks
    const buttons = page.locator("button:visible");
    const buttonCount = await buttons.count();

    console.log(`🔘 Found ${buttonCount} visible buttons`);

    // Test first few buttons
    for (let i = 0; i < Math.min(buttonCount, 5); i++) {
      const button = buttons.nth(i);
      const btnText = await button.textContent();

      // Skip dangerous buttons
      if (
        btnText &&
        !btnText.toLowerCase().includes("delete") &&
        !btnText.toLowerCase().includes("remove")
      ) {
        console.log(`🖱️ Testing button: "${btnText?.slice(0, 20)}..."`);

        await button.hover();
        await page.waitForTimeout(300);

        await button.click();
        await page.waitForTimeout(500);

        // Handle any modals that open
        const modal = page.locator(".modal:visible");
        if (await modal.isVisible({ timeout: 1000 })) {
          const closeBtn = modal
            .locator("button")
            .filter({ hasText: /close|cancel/i })
            .first();
          if (await closeBtn.isVisible()) {
            await closeBtn.click();
            await page.waitForTimeout(500);
          }
        }
      }
    }

    console.log("✅ UI interaction test completed!");
  });

  test("Toast Notifications and Feedback", async ({ page }) => {
    console.log("🍞 Testing Toast Notifications and Feedback...");

    // Try to trigger some actions that might show toasts
    const actionButtons = page.locator("button").filter({
      hasText: /save|create|update|submit/i,
    });

    const actionCount = await actionButtons.count();

    if (actionCount > 0) {
      console.log(`⚡ Found ${actionCount} action buttons`);

      // Click first action button
      const firstAction = actionButtons.first();
      await firstAction.click();
      await page.waitForTimeout(2000);

      // Look for toast notifications
      const toasts = page.locator('.toast, .alert, [data-testid*="toast"]');
      if (await toasts.first().isVisible({ timeout: 3000 })) {
        console.log("🍞 Toast notification appeared!");
        await page.waitForTimeout(2000);
      }
    }

    console.log("✅ Toast notification test completed!");
  });
});

// Utility test for taking screenshots
test.describe("Visual Documentation", () => {
  test("Capture Main App Screenshots", async ({ page }) => {
    console.log("📸 Capturing visual documentation...");

    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await page.waitForSelector(
      '[data-testid="dashboard-container"], .container'
    );
    await page.waitForTimeout(2000);

    // Main dashboard screenshot
    await page.screenshot({
      path: "test-reports/screenshots/main-dashboard.png",
      fullPage: true,
    });

    console.log("📸 Screenshots saved to test-reports/screenshots/");
  });
});
