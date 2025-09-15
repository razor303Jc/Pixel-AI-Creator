const { test, expect } = require("@playwright/test");

test.describe("Template Delete Fix Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the templates page
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");

    // Mock login state if needed
    await page.evaluate(() => {
      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: 1,
          email: "user@example.com",
          name: "Test User",
        })
      );
    });

    // Navigate to templates section
    await page.click('[data-testid="nav-templates"]');
    await page.waitForLoadState("networkidle");
  });

  test("should allow deletion of duplicated templates", async ({ page }) => {
    // Wait for templates to load
    await page.waitForSelector('[data-testid^="template-card-"]', {
      timeout: 10000,
    });

    // Find a system template and duplicate it
    const systemTemplate = page
      .locator('[data-testid^="duplicate-system-template-"]')
      .first();
    if ((await systemTemplate.count()) > 0) {
      await systemTemplate.click();

      // Wait for duplication to complete
      await page.waitForSelector(".alert-success", { timeout: 5000 });

      // Find the duplicated template (should have "Copy" in the name)
      const duplicatedCard = page
        .locator('[data-testid^="template-card-"]')
        .filter({ hasText: "(Copy)" })
        .first();
      await expect(duplicatedCard).toBeVisible();

      // Click on the dropdown for the duplicated template
      const duplicatedId = await duplicatedCard.getAttribute("data-testid");
      const templateId = duplicatedId.replace("template-card-", "");

      const dropdownToggle = page.locator(
        `[data-testid="template-dropdown-${templateId}"]`
      );
      await expect(dropdownToggle).toBeVisible();
      await dropdownToggle.click();

      // Check that delete option is available
      const deleteOption = page.locator(
        `[data-testid="delete-template-${templateId}"]`
      );
      await expect(deleteOption).toBeVisible();

      // Click delete
      await deleteOption.click();

      // Confirm deletion in modal
      await page.waitForSelector('[data-testid="delete-modal"]', {
        timeout: 5000,
      });
      await page.click('[data-testid="confirm-delete"]');

      // Verify template was deleted (success message should appear)
      await page.waitForSelector(".alert-success", { timeout: 5000 });
      const successMessage = page.locator(".alert-success");
      await expect(successMessage).toContainText("deleted successfully");

      // Verify the template card is no longer visible
      await expect(duplicatedCard).not.toBeVisible();
    }
  });

  test("should show proper dropdown options for user templates", async ({
    page,
  }) => {
    // Wait for templates to load
    await page.waitForSelector('[data-testid^="template-card-"]', {
      timeout: 10000,
    });

    // Find a template with dropdown (user template)
    const userTemplateDropdown = page
      .locator('[data-testid^="template-dropdown-"]')
      .first();

    if ((await userTemplateDropdown.count()) > 0) {
      await userTemplateDropdown.click();

      // Check all dropdown options are present
      await expect(page.locator("text=Edit")).toBeVisible();
      await expect(page.locator("text=Duplicate")).toBeVisible();
      await expect(page.locator("text=Export")).toBeVisible();
      await expect(page.locator("text=Delete")).toBeVisible();
    }
  });

  test("should not show dropdown for system templates", async ({ page }) => {
    // Wait for templates to load
    await page.waitForSelector('[data-testid^="template-card-"]', {
      timeout: 10000,
    });

    // Find a system template (one with "System" badge)
    const systemTemplateCard = page
      .locator('[data-testid^="template-card-"]')
      .filter({ hasText: "System" })
      .first();

    if ((await systemTemplateCard.count()) > 0) {
      // System templates should not have dropdown, only duplicate button
      const dropdownInCard = systemTemplateCard.locator(
        '[data-testid^="template-dropdown-"]'
      );
      await expect(dropdownInCard).not.toBeVisible();

      // But should have duplicate button
      const duplicateButton = systemTemplateCard.locator(
        '[data-testid^="duplicate-system-template-"]'
      );
      await expect(duplicateButton).toBeVisible();
    }
  });
});
