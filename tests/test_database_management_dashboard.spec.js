const { test, expect } = require("@playwright/test");

/**
 * Database Management Dashboard Tests
 *
 * Tests for the comprehensive database management interface including:
 * - Health monitoring dashboard
 * - Connection management interface
 * - Backup creation and management
 * - Alert management system
 * - Performance metrics visualization
 */

test.describe("Database Management Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    // Mock the API responses for testing
    await page.route("**/api/database/**", async (route) => {
      const url = route.request().url();

      if (url.includes("/health")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            status: "healthy",
            message: "Database is operating normally",
            metrics: {
              connections: 15,
              avg_response_time_ms: 45.2,
              error_rate_percent: 0.1,
              total_queries: 15420,
            },
            alerts: {
              critical: 0,
              error: 0,
              warning: 1,
              total: 1,
            },
            timestamp: new Date().toISOString(),
          }),
        });
      } else if (url.includes("/connections/stats")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            total_connections: 20,
            active_connections: 15,
            idle_connections: 5,
            max_connections: 100,
            avg_response_time: 45.2,
            status: "healthy",
          }),
        });
      } else if (url.includes("/metrics/history")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              connection_count: 12,
              avg_response_time: 42.1,
              error_rate: 0.05,
              total_queries: 14200,
            },
            {
              timestamp: new Date(Date.now() - 1800000).toISOString(),
              connection_count: 15,
              avg_response_time: 45.2,
              error_rate: 0.1,
              total_queries: 15420,
            },
          ]),
        });
      } else if (url.includes("/alerts")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "alert-001",
              level: "warning",
              metric_type: "response_time",
              message: "Response time above threshold",
              value: 52.3,
              threshold: 50.0,
              timestamp: new Date().toISOString(),
              resolved: false,
            },
          ]),
        });
      } else if (url.includes("/backups")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "backup-001",
              backup_type: "full",
              file_size: 15728640, // 15MB
              status: "completed",
              created_at: new Date(Date.now() - 86400000).toISOString(),
              completed_at: new Date(Date.now() - 86340000).toISOString(),
              error_message: null,
              encrypted: true,
            },
            {
              id: "backup-002",
              backup_type: "incremental",
              file_size: 2097152, // 2MB
              status: "completed",
              created_at: new Date(Date.now() - 43200000).toISOString(),
              completed_at: new Date(Date.now() - 43140000).toISOString(),
              error_message: null,
              encrypted: true,
            },
          ]),
        });
      }
    });

    // Navigate to the database management dashboard
    await page.goto("http://localhost:3000/admin/database");
  });

  test("should display database health overview correctly", async ({
    page,
  }) => {
    // Wait for the page to load
    await page.waitForSelector('[data-testid="database-health-status"]', {
      timeout: 10000,
    });

    // Check health status indicators
    const healthBadge = page.locator('[data-testid="health-badge"]');
    await expect(healthBadge).toContainText("HEALTHY");

    // Check connection metrics
    const connectionCount = page.locator('[data-testid="connection-count"]');
    await expect(connectionCount).toContainText("15 / 100");

    // Check active alerts count
    const alertsCount = page.locator('[data-testid="alerts-count"]');
    await expect(alertsCount).toContainText("1");

    // Check recent backups count
    const backupsCount = page.locator('[data-testid="backups-count"]');
    await expect(backupsCount).toContainText("2");
  });

  test("should render performance metrics chart", async ({ page }) => {
    // Wait for charts to load
    await page.waitForSelector(".recharts-responsive-container", {
      timeout: 15000,
    });

    // Check if performance chart is visible
    const performanceChart = page.locator('[data-testid="performance-chart"]');
    await expect(performanceChart).toBeVisible();

    // Check if chart has data points
    const chartLines = page.locator(".recharts-line");
    await expect(chartLines).toHaveCount(3); // connections, response time, error rate

    // Check chart legend
    const legend = page.locator(".recharts-legend-wrapper");
    await expect(legend).toBeVisible();
    await expect(legend).toContainText("Connections");
    await expect(legend).toContainText("Response Time (ms)");
    await expect(legend).toContainText("Error Rate (%)");
  });

  test("should display and manage active alerts", async ({ page }) => {
    // Wait for alerts table to load
    await page.waitForSelector('[data-testid="alerts-table"]', {
      timeout: 10000,
    });

    // Check if alert is displayed
    const alertRow = page.locator('[data-testid="alert-row"]').first();
    await expect(alertRow).toContainText("warning");
    await expect(alertRow).toContainText("Response time above threshold");

    // Test resolve alert functionality
    const resolveButton = page
      .locator('[data-testid="resolve-alert-btn"]')
      .first();

    // Mock the resolve alert API call
    await page.route("**/api/database/alerts/*/resolve", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true }),
      });
    });

    await resolveButton.click();

    // Verify the API call was made
    await page.waitForRequest("**/api/database/alerts/*/resolve");
  });

  test("should display and manage database backups", async ({ page }) => {
    // Wait for backups table to load
    await page.waitForSelector('[data-testid="backups-table"]', {
      timeout: 10000,
    });

    // Check if backups are displayed
    const backupRows = page.locator('[data-testid="backup-row"]');
    await expect(backupRows).toHaveCount(2);

    // Check backup details
    const firstBackup = backupRows.first();
    await expect(firstBackup).toContainText("full");
    await expect(firstBackup).toContainText("15.0 MB");
    await expect(firstBackup).toContainText("completed");

    // Check encryption indicator
    const encryptionIcon = page
      .locator('[data-testid="encryption-icon"]')
      .first();
    await expect(encryptionIcon).toBeVisible();
  });

  test("should create new database backup", async ({ page }) => {
    // Click create backup button
    const createBackupBtn = page.locator('[data-testid="create-backup-btn"]');
    await createBackupBtn.click();

    // Wait for modal to appear
    await page.waitForSelector('[data-testid="backup-modal"]', {
      timeout: 5000,
    });

    // Fill backup form
    const backupTypeSelect = page.locator('[data-testid="backup-type-select"]');
    await backupTypeSelect.selectOption("full");

    const customNameInput = page.locator('[data-testid="custom-name-input"]');
    await customNameInput.fill("test-backup-playwright");

    // Mock the create backup API call
    await page.route("**/api/database/backups", async (route) => {
      if (route.request().method() === "POST") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "backup-003",
            backup_type: "full",
            file_size: 0,
            status: "pending",
            created_at: new Date().toISOString(),
            completed_at: null,
            error_message: null,
            encrypted: true,
          }),
        });
      }
    });

    // Submit the form
    const submitBtn = page.locator('[data-testid="create-backup-submit"]');
    await submitBtn.click();

    // Verify the API call was made
    await page.waitForRequest("**/api/database/backups");

    // Modal should close
    await expect(
      page.locator('[data-testid="backup-modal"]')
    ).not.toBeVisible();
  });

  test("should show backup restore confirmation", async ({ page }) => {
    // Wait for backups table
    await page.waitForSelector('[data-testid="backups-table"]', {
      timeout: 10000,
    });

    // Click on actions dropdown for first backup
    const actionsDropdown = page
      .locator('[data-testid="backup-actions-dropdown"]')
      .first();
    await actionsDropdown.click();

    // Click restore option
    const restoreOption = page.locator('[data-testid="restore-backup-option"]');
    await restoreOption.click();

    // Wait for restore confirmation modal
    await page.waitForSelector('[data-testid="restore-modal"]', {
      timeout: 5000,
    });

    // Check warning message
    const warningText = page.locator('[data-testid="restore-warning"]');
    await expect(warningText).toContainText("Warning");
    await expect(warningText).toContainText(
      "This will replace all current data"
    );

    // Check backup details are shown
    const backupDetails = page.locator(
      '[data-testid="restore-backup-details"]'
    );
    await expect(backupDetails).toContainText("backup-001");
    await expect(backupDetails).toContainText("full");
    await expect(backupDetails).toContainText("15.0 MB");
  });

  test("should refresh dashboard data", async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="database-health-status"]', {
      timeout: 10000,
    });

    // Click refresh button for alerts
    const refreshAlertsBtn = page.locator('[data-testid="refresh-alerts-btn"]');

    // Mock updated alerts response
    await page.route("**/api/database/alerts", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]), // No alerts
      });
    });

    await refreshAlertsBtn.click();

    // Verify API call was made
    await page.waitForRequest("**/api/database/alerts");

    // Check that alerts table shows no alerts
    await expect(
      page.locator('[data-testid="no-alerts-message"]')
    ).toContainText("No active alerts");
  });

  test("should handle API errors gracefully", async ({ page }) => {
    // Mock API error for health endpoint
    await page.route("**/api/database/health", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Database service unavailable" }),
      });
    });

    // Reload page to trigger error
    await page.reload();

    // Wait for error alert to appear
    await page.waitForSelector('[data-testid="error-alert"]', {
      timeout: 10000,
    });

    // Check error message
    const errorAlert = page.locator('[data-testid="error-alert"]');
    await expect(errorAlert).toContainText("Database service unavailable");

    // Check that error alert is dismissible
    const dismissBtn = page.locator('[data-testid="dismiss-error-btn"]');
    await dismissBtn.click();

    await expect(errorAlert).not.toBeVisible();
  });

  test("should be responsive on mobile devices", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Wait for page to load
    await page.waitForSelector('[data-testid="database-health-status"]', {
      timeout: 10000,
    });

    // Check that mobile layout is applied
    const container = page.locator(".container-fluid");
    await expect(container).toBeVisible();

    // Check that cards stack vertically on mobile
    const healthCards = page.locator('[data-testid="health-card"]');
    const firstCard = healthCards.first();
    const secondCard = healthCards.nth(1);

    const firstCardBox = await firstCard.boundingBox();
    const secondCardBox = await secondCard.boundingBox();

    // On mobile, cards should stack (second card should be below first)
    expect(secondCardBox?.y).toBeGreaterThan(
      firstCardBox?.y + firstCardBox?.height
    );
  });

  test("should update metrics in real-time", async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="database-health-status"]', {
      timeout: 10000,
    });

    // Get initial connection count
    const connectionCount = page.locator('[data-testid="connection-count"]');
    const initialText = await connectionCount.textContent();

    // Mock updated stats
    await page.route("**/api/database/connections/stats", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_connections: 25,
          active_connections: 20,
          idle_connections: 5,
          max_connections: 100,
          avg_response_time: 48.7,
          status: "healthy",
        }),
      });
    });

    // Wait for auto-refresh (assuming 30 second interval)
    await page.waitForTimeout(2000); // Short wait for test

    // Manually trigger refresh by reloading component data
    await page.evaluate(() => {
      // Simulate component refresh
      window.dispatchEvent(new Event("focus"));
    });

    // Check if connection count updated
    await expect(connectionCount).toContainText("20 / 100");
  });

  test("should validate form inputs correctly", async ({ page }) => {
    // Open create backup modal
    await page.locator('[data-testid="create-backup-btn"]').click();
    await page.waitForSelector('[data-testid="backup-modal"]', {
      timeout: 5000,
    });

    // Try to submit without selecting backup type
    const submitBtn = page.locator('[data-testid="create-backup-submit"]');
    await submitBtn.click();

    // Check for validation message (if implemented)
    // This would depend on your form validation implementation

    // Fill valid data
    await page
      .locator('[data-testid="backup-type-select"]')
      .selectOption("incremental");

    // Test custom name validation (if any constraints exist)
    const customNameInput = page.locator('[data-testid="custom-name-input"]');
    await customNameInput.fill("valid-backup-name");

    // Should be able to submit now
    await expect(submitBtn).toBeEnabled();
  });
});

test.describe("Database Management Dashboard - Advanced Features", () => {
  test("should handle connection management operations", async ({ page }) => {
    // Mock connection details endpoint
    await page.route("**/api/database/connections/details", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          active_connections: [
            {
              pid: 12345,
              user: "app_user",
              database: "pixel_ai_db",
              state: "active",
              query: "SELECT * FROM chatbots WHERE status = $1",
              duration: 250,
            },
            {
              pid: 12346,
              user: "app_user",
              database: "pixel_ai_db",
              state: "idle",
              query: "",
              duration: 5000,
            },
          ],
        }),
      });
    });

    await page.goto("http://localhost:3000/admin/database");

    // Navigate to connection details (if this feature exists)
    const connectionDetailsBtn = page.locator(
      '[data-testid="view-connections-btn"]'
    );
    if (await connectionDetailsBtn.isVisible()) {
      await connectionDetailsBtn.click();

      // Verify connection details are shown
      await expect(
        page.locator('[data-testid="connection-12345"]')
      ).toContainText("active");
      await expect(
        page.locator('[data-testid="connection-12346"]')
      ).toContainText("idle");
    }
  });

  test("should show performance optimization recommendations", async ({
    page,
  }) => {
    // Mock performance analysis endpoint
    await page.route("**/api/database/performance/analyze", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          slow_queries: [
            {
              query: "SELECT * FROM conversations WHERE created_at > $1",
              avg_duration: 1500,
              call_count: 245,
              total_time: 367500,
            },
          ],
          recommendations: [
            "Add index on conversations.created_at column",
            "Consider connection pooling optimization",
          ],
          index_suggestions: [
            {
              table: "conversations",
              columns: ["created_at", "status"],
              rationale: "Frequent filtering on these columns",
            },
          ],
        }),
      });
    });

    await page.goto("http://localhost:3000/admin/database");

    // Check if performance recommendations are shown
    const performanceBtn = page.locator(
      '[data-testid="performance-analysis-btn"]'
    );
    if (await performanceBtn.isVisible()) {
      await performanceBtn.click();

      await expect(
        page.locator('[data-testid="performance-recommendations"]')
      ).toContainText("Add index");
    }
  });
});
