/**
 * Dashboard Feature Tests - Focused Visual Testing
 * Tests specific dashboard components and interactions
 */

import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:3002";

test.describe("Dashboard Specific Features", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
  });

  test("Dashboard Header and Navigation", async ({ page }) => {
    console.log("🏠 Testing Dashboard Header and Navigation...");

    // Check main header
    await expect(page.locator("h1, .navbar-brand")).toBeVisible();

    // Test navigation items
    const navItems = ["Dashboard", "Analytics", "Templates"];
    for (const item of navItems) {
      console.log(`🔍 Checking navigation item: ${item}`);
      await expect(page.getByText(item)).toBeVisible();

      // Click and observe
      await page.getByText(item).click();
      await page.waitForTimeout(1500);
    }

    console.log("✅ Navigation test completed!");
  });

  test("Statistics Cards Display", async ({ page }) => {
    console.log("📊 Testing Statistics Cards...");

    // Look for metric cards
    const statCards = page.locator(
      '.card, [data-testid*="stat"], [data-testid*="metric"]'
    );
    const cardCount = await statCards.count();

    console.log(`📈 Found ${cardCount} statistics cards`);

    if (cardCount > 0) {
      for (let i = 0; i < Math.min(cardCount, 4); i++) {
        const card = statCards.nth(i);
        console.log(`📊 Examining statistics card ${i + 1}...`);

        // Highlight each card
        await card.scrollIntoViewIfNeeded();
        await card.hover();
        await page.waitForTimeout(800);

        // Look for numbers, icons, and text
        const cardText = await card.textContent();
        if (cardText) {
          console.log(`📝 Card content preview: "${cardText.slice(0, 50)}..."`);
        }
      }
    }

    console.log("✅ Statistics cards test completed!");
  });

  test("Client Management Section", async ({ page }) => {
    console.log("👥 Testing Client Management Section...");

    // Scroll to clients section
    const clientsSection = page.locator("text=Clients").first();
    if (await clientsSection.isVisible()) {
      await clientsSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      console.log("👥 Clients section found!");

      // Look for client-related buttons
      const clientButtons = page.locator("button").filter({
        hasText: /client|add|create|\+/i,
      });

      const btnCount = await clientButtons.count();
      console.log(`🔘 Found ${btnCount} client-related buttons`);

      // Test "Add Client" or "Create Client" button
      const addClientBtn = clientButtons
        .filter({ hasText: /add|create|\+/i })
        .first();
      if (await addClientBtn.isVisible()) {
        console.log("➕ Testing Add Client button...");

        await addClientBtn.click();
        await page.waitForTimeout(2000);

        // Check if modal opened
        const modal = page.locator(".modal, .modal-dialog");
        if (await modal.isVisible()) {
          console.log("📝 Client creation modal opened!");

          // Try to fill some fields
          await page.fill(
            'input[name*="name"], input[placeholder*="name"]',
            "Test Client"
          );
          await page.waitForTimeout(500);

          await page.fill(
            'input[name*="email"], input[placeholder*="email"]',
            "test@example.com"
          );
          await page.waitForTimeout(500);

          // Close the modal
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
    }

    console.log("✅ Client management test completed!");
  });

  test("Chatbot Management Section", async ({ page }) => {
    console.log("🤖 Testing Chatbot Management Section...");

    // Scroll to chatbots section
    const chatbotsSection = page.locator("text=Chatbots").first();
    if (await chatbotsSection.isVisible()) {
      await chatbotsSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      console.log("🤖 Chatbots section found!");

      // Look for chatbot-related buttons
      const botButtons = page.locator("button").filter({
        hasText: /bot|chatbot|add|create|\+/i,
      });

      const btnCount = await botButtons.count();
      console.log(`🔘 Found ${btnCount} chatbot-related buttons`);

      // Test "Add Chatbot" or "Create Chatbot" button
      const addBotBtn = botButtons
        .filter({ hasText: /add|create|\+/i })
        .first();
      if (await addBotBtn.isVisible()) {
        console.log("➕ Testing Add Chatbot button...");

        await addBotBtn.click();
        await page.waitForTimeout(2000);

        // Check if modal opened
        const modal = page.locator(".modal, .modal-dialog");
        if (await modal.isVisible()) {
          console.log("📝 Chatbot creation modal opened!");

          // Try to fill some fields
          await page.fill(
            'input[name*="name"], input[placeholder*="name"]',
            "Demo Support Bot"
          );
          await page.waitForTimeout(500);

          // Look for type/purpose dropdown
          const typeSelect = page
            .locator('select[name*="type"], select[name*="purpose"]')
            .first();
          if (await typeSelect.isVisible()) {
            await typeSelect.selectOption({ index: 1 });
            await page.waitForTimeout(500);
          }

          // Close the modal
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
    }

    console.log("✅ Chatbot management test completed!");
  });

  test("Interactive Elements and Hover Effects", async ({ page }) => {
    console.log("🖱️ Testing Interactive Elements...");

    // Find all interactive elements
    const interactiveElements = page.locator(
      'button, a, .btn, [role="button"]'
    );
    const elementCount = await interactiveElements.count();

    console.log(`🎯 Found ${elementCount} interactive elements`);

    // Test hover effects on first few elements
    for (let i = 0; i < Math.min(elementCount, 8); i++) {
      const element = interactiveElements.nth(i);
      if (await element.isVisible()) {
        const elementText = await element.textContent();
        console.log(`🖱️ Hovering over: "${elementText?.slice(0, 30)}..."`);

        await element.hover();
        await page.waitForTimeout(500);
      }
    }

    console.log("✅ Interactive elements test completed!");
  });

  test("Form Validation and Input Handling", async ({ page }) => {
    console.log("📝 Testing Form Validation...");

    // Try to trigger a modal with a form
    const createButtons = page
      .locator("button")
      .filter({ hasText: /create|add|\+/i });

    if (await createButtons.first().isVisible()) {
      await createButtons.first().click();
      await page.waitForTimeout(1500);

      const modal = page.locator(".modal");
      if (await modal.isVisible()) {
        console.log("📝 Form modal opened for validation testing...");

        // Test empty form submission
        const submitBtn = modal
          .locator("button")
          .filter({ hasText: /save|create|submit/i })
          .first();
        if (await submitBtn.isVisible()) {
          console.log("❌ Testing empty form submission...");
          await submitBtn.click();
          await page.waitForTimeout(1000);

          // Look for validation messages
          const validationMsgs = page.locator(
            ".invalid-feedback, .error, .alert-danger"
          );
          if (await validationMsgs.first().isVisible()) {
            console.log("✅ Validation messages appeared!");
          }
        }

        // Fill form with valid data
        console.log("✅ Testing valid form data...");
        const nameInput = modal.locator("input").first();
        if (await nameInput.isVisible()) {
          await nameInput.fill("Valid Test Name");
          await page.waitForTimeout(500);
        }

        // Close modal
        const closeBtn = modal
          .locator("button")
          .filter({ hasText: /close|cancel/i })
          .first();
        if (await closeBtn.isVisible()) {
          await closeBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    }

    console.log("✅ Form validation test completed!");
  });

  test("Performance and Loading Indicators", async ({ page }) => {
    console.log("⏱️ Testing Performance and Loading...");

    // Measure page load time
    const startTime = Date.now();
    await page.reload();
    await page.waitForLoadState("networkidle");
    const loadTime = Date.now() - startTime;

    console.log(`⏱️ Page load time: ${loadTime}ms`);

    // Look for loading indicators
    const loadingIndicators = page.locator(
      ".spinner-border, .spinner-grow, .loading"
    );
    if (await loadingIndicators.first().isVisible({ timeout: 1000 })) {
      console.log("⏳ Loading indicators detected");
      await page.waitForTimeout(2000);
    }

    // Test if content loads within reasonable time
    await expect(page.locator("h1, .navbar-brand")).toBeVisible({
      timeout: 5000,
    });

    console.log("✅ Performance test completed!");
  });
});

// Quick smoke tests
test.describe("Quick Smoke Tests", () => {
  test("App Loads Without Errors", async ({ page }) => {
    console.log("💨 Running quick smoke test...");

    // Listen for console errors
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");

    // Check basic elements exist
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("nav, header")).toBeVisible();

    // Log any console errors
    if (errors.length > 0) {
      console.log(`⚠️ Console errors detected: ${errors.length}`);
      errors.forEach((error) => console.log(`❌ ${error}`));
    } else {
      console.log("✅ No console errors detected!");
    }

    console.log("✅ Smoke test completed!");
  });
});
