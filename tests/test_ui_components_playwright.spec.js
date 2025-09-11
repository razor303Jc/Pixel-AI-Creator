/**
 * Comprehensive Playwright Tests for New UI Components
 * Tests AnalyticsDashboard, ChatbotManager, and ClientDashboard
 */

const { test, expect } = require("@playwright/test");

test.describe("UI Components Test Suite", () => {
  test.beforeEach(async ({ page }) => {
    // Start the frontend server and navigate to login
    await page.goto("http://localhost:3002");

    // Mock login for testing (if authentication is required)
    await page.evaluate(() => {
      localStorage.setItem("authToken", "mock-jwt-token");
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: 1,
          email: "test@example.com",
          role: "admin",
        })
      );
    });
  });

  test.describe("Analytics Dashboard Component", () => {
    test("should load analytics dashboard with key metrics", async ({
      page,
    }) => {
      // Navigate to analytics dashboard
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Wait for the component to load
      await page.waitForSelector('[data-testid="analytics-dashboard"]', {
        timeout: 10000,
      });

      // Check if header is present
      await expect(page.locator("h2")).toContainText("Analytics Dashboard");

      // Verify key metrics cards are displayed
      await expect(
        page.locator('[data-testid="total-conversations"]')
      ).toBeVisible();
      await expect(page.locator('[data-testid="success-rate"]')).toBeVisible();
      await expect(
        page.locator('[data-testid="avg-response-time"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-testid="total-messages"]')
      ).toBeVisible();

      // Check if metrics have values
      const conversationsText = await page
        .locator('[data-testid="total-conversations"] h3')
        .textContent();
      expect(conversationsText).toMatch(/\d+/); // Should contain numbers
    });

    test("should display conversation volume chart", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Wait for charts to load
      await page.waitForSelector(".recharts-responsive-container", {
        timeout: 15000,
      });

      // Verify chart container is present
      await expect(
        page.locator(".recharts-responsive-container")
      ).toBeVisible();

      // Check if chart has data points
      await expect(page.locator(".recharts-area")).toBeVisible();
    });

    test("should allow time range filtering", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Wait for dropdown to be available
      await page.waitForSelector('[data-testid="time-range-dropdown"]', {
        timeout: 10000,
      });

      // Click time range dropdown
      await page.click('[data-testid="time-range-dropdown"]');

      // Select different time range
      await page.click("text=Last 30 days");

      // Verify the selection changed
      await expect(
        page.locator('[data-testid="time-range-dropdown"]')
      ).toContainText("Last 30 days");
    });

    test("should display client satisfaction pie chart", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Wait for pie chart component
      await page.waitForSelector(".recharts-pie", { timeout: 15000 });

      // Verify pie chart is visible
      await expect(page.locator(".recharts-pie")).toBeVisible();
    });
  });

  test.describe("Chatbot Manager Component", () => {
    test("should display chatbot management interface", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Wait for component to load
      await page.waitForSelector('[data-testid="chatbot-manager"]', {
        timeout: 10000,
      });

      // Check header
      await expect(page.locator("h2")).toContainText("Chatbot Management");

      // Verify create button is present
      await expect(
        page.locator('button:has-text("Create New Chatbot")')
      ).toBeVisible();
    });

    test("should open create chatbot modal", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Click create new chatbot button
      await page.click('button:has-text("Create New Chatbot")');

      // Wait for modal to appear
      await page.waitForSelector(".modal-dialog", { timeout: 5000 });

      // Verify modal is visible
      await expect(page.locator(".modal-title")).toContainText(
        "Create New Chatbot"
      );

      // Check form fields are present
      await expect(
        page.locator('input[placeholder="Enter chatbot name"]')
      ).toBeVisible();
      await expect(
        page.locator('textarea[placeholder="Describe your chatbot\'s purpose"]')
      ).toBeVisible();
    });

    test("should display chatbot cards with status badges", async ({
      page,
    }) => {
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Wait for chatbot cards to load
      await page.waitForSelector(".card", { timeout: 10000 });

      // Verify at least one chatbot card is present
      await expect(page.locator(".card").first()).toBeVisible();

      // Check for status badges
      await expect(page.locator(".badge").first()).toBeVisible();
    });

    test("should open test modal for chatbot testing", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Wait for chatbot cards and click test button
      await page.waitForSelector('button:has-text("Test")', { timeout: 10000 });
      await page.click('button:has-text("Test")');

      // Wait for test modal
      await page.waitForSelector(".modal-dialog", { timeout: 5000 });

      // Verify test interface
      await expect(page.locator(".modal-title")).toContainText("Test Chatbot");
      await expect(
        page.locator('input[placeholder="Type a test message..."]')
      ).toBeVisible();
    });

    test("should navigate between configuration tabs", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Open create modal
      await page.click('button:has-text("Create New Chatbot")');
      await page.waitForSelector(".modal-dialog", { timeout: 5000 });

      // Click on different tabs
      await page.click('button[data-rb-event-key="behavior"]');
      await expect(
        page.locator('textarea[placeholder*="instructions"]')
      ).toBeVisible();

      await page.click('button[data-rb-event-key="features"]');
      await expect(page.locator('input[type="checkbox"]')).toBeVisible();
    });
  });

  test.describe("Client Dashboard Component", () => {
    test("should display client performance metrics", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/client");

      // Wait for component to load
      await page.waitForSelector('[data-testid="client-dashboard"]', {
        timeout: 10000,
      });

      // Check header
      await expect(page.locator("h2")).toContainText("Client Dashboard");

      // Verify metric cards
      await expect(
        page.locator('[data-testid="total-conversations-metric"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-testid="average-rating-metric"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-testid="response-time-metric"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-testid="monthly-spend-metric"]')
      ).toBeVisible();
    });

    test("should display usage progress bars", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/client");

      // Wait for usage section
      await page.waitForSelector(".progress", { timeout: 10000 });

      // Verify progress bars are present
      const progressBars = await page.locator(".progress").count();
      expect(progressBars).toBeGreaterThan(0);

      // Check progress bar labels
      await expect(page.locator("text=Conversations")).toBeVisible();
      await expect(page.locator("text=Messages")).toBeVisible();
      await expect(page.locator("text=Storage")).toBeVisible();
    });

    test("should open billing modal", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/client");

      // Click billing button
      await page.click('button:has-text("Billing")');

      // Wait for billing modal
      await page.waitForSelector(".modal-dialog", { timeout: 5000 });

      // Verify billing information
      await expect(page.locator(".modal-title")).toContainText(
        "Billing Information"
      );
      await expect(page.locator("text=Current Plan")).toBeVisible();
      await expect(page.locator("text=Monthly Spend")).toBeVisible();
    });

    test("should switch between overview and performance tabs", async ({
      page,
    }) => {
      await page.goto("http://localhost:3002/dashboard/client");

      // Wait for tabs to load
      await page.waitForSelector(".nav-tabs", { timeout: 10000 });

      // Click performance tab
      await page.click('button[data-rb-event-key="performance"]');

      // Verify performance content is displayed
      await expect(page.locator("text=Chatbot Performance")).toBeVisible();

      // Switch back to overview
      await page.click('button[data-rb-event-key="overview"]');

      // Verify overview content
      await expect(page.locator("text=Monthly Usage Trends")).toBeVisible();
    });

    test("should display responsive charts", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/client");

      // Wait for charts to render
      await page.waitForSelector(".recharts-responsive-container", {
        timeout: 15000,
      });

      // Verify multiple charts are present
      const chartContainers = await page
        .locator(".recharts-responsive-container")
        .count();
      expect(chartContainers).toBeGreaterThan(0);

      // Check if charts are interactive
      await expect(page.locator(".recharts-area")).toBeVisible();
    });
  });

  test.describe("Integration Tests", () => {
    test("should navigate between dashboard components", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard");

      // Test navigation to analytics
      await page.click('a[href*="analytics"]');
      await expect(page).toHaveURL(/.*analytics.*/);

      // Test navigation to chatbots
      await page.click('a[href*="chatbots"]');
      await expect(page).toHaveURL(/.*chatbots.*/);

      // Test navigation to client dashboard
      await page.click('a[href*="client"]');
      await expect(page).toHaveURL(/.*client.*/);
    });

    test("should maintain authentication state across components", async ({
      page,
    }) => {
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Verify auth token is maintained
      const authToken = await page.evaluate(() =>
        localStorage.getItem("authToken")
      );
      expect(authToken).toBe("mock-jwt-token");

      // Navigate to different component
      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Verify auth is still valid
      const authTokenAfterNavigation = await page.evaluate(() =>
        localStorage.getItem("authToken")
      );
      expect(authTokenAfterNavigation).toBe("mock-jwt-token");
    });

    test("should handle loading states gracefully", async ({ page }) => {
      await page.goto("http://localhost:3002/dashboard/analytics");

      // Check for loading spinners during initial load
      await page
        .waitForSelector(".spinner-border", { timeout: 2000 })
        .catch(() => {
          // Loading might be too fast to catch, which is fine
        });

      // Verify content loads after loading states
      await page.waitForSelector('[data-testid="analytics-dashboard"]', {
        timeout: 10000,
      });
      await expect(page.locator("h2")).toContainText("Analytics Dashboard");
    });

    test("should display error states when API fails", async ({ page }) => {
      // Mock API failure
      await page.route("**/api/**", (route) => {
        route.fulfill({
          status: 500,
          body: "Internal Server Error",
        });
      });

      await page.goto("http://localhost:3002/dashboard/analytics");

      // Should gracefully handle errors and show fallback data
      await page.waitForSelector('[data-testid="analytics-dashboard"]', {
        timeout: 10000,
      });

      // Component should still render with mock data
      await expect(page.locator("h2")).toContainText("Analytics Dashboard");
    });
  });

  test.describe("Responsive Design Tests", () => {
    test("should display correctly on mobile devices", async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto("http://localhost:3002/dashboard/analytics");

      // Wait for component to adapt to mobile
      await page.waitForSelector('[data-testid="analytics-dashboard"]', {
        timeout: 10000,
      });

      // Verify mobile layout
      await expect(page.locator("h2")).toBeVisible();

      // Check if charts are responsive
      await page.waitForSelector(".recharts-responsive-container", {
        timeout: 15000,
      });
      await expect(
        page.locator(".recharts-responsive-container")
      ).toBeVisible();
    });

    test("should display correctly on tablet devices", async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.goto("http://localhost:3002/dashboard/chatbots");

      // Wait for component
      await page.waitForSelector('[data-testid="chatbot-manager"]', {
        timeout: 10000,
      });

      // Verify layout adapts to tablet
      await expect(page.locator("h2")).toBeVisible();
      await expect(page.locator(".card").first()).toBeVisible();
    });
  });
});

// Performance tests
test.describe("Performance Tests", () => {
  test("should load dashboard components within acceptable time", async ({
    page,
  }) => {
    const startTime = Date.now();

    await page.goto("http://localhost:3002/dashboard/analytics");
    await page.waitForSelector('[data-testid="analytics-dashboard"]', {
      timeout: 10000,
    });

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  });

  test("should handle multiple simultaneous chart renders", async ({
    page,
  }) => {
    await page.goto("http://localhost:3002/dashboard/client");

    // Wait for multiple charts to load simultaneously
    await Promise.all([
      page.waitForSelector(".recharts-area", { timeout: 15000 }),
      page.waitForSelector(".recharts-bar", { timeout: 15000 }),
      page.waitForSelector(".recharts-pie", { timeout: 15000 }),
    ]);

    // Verify all charts are rendered
    await expect(page.locator(".recharts-responsive-container")).toHaveCount(3);
  });
});
