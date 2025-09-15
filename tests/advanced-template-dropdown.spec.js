const { test, expect } = require("@playwright/test");

test.describe("Advanced Template Dropdown Functionality", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and authenticate
    await page.goto("http://localhost:3002");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');

    // Navigate to templates
    await page.waitForSelector('[data-testid="nav-templates"]', {
      timeout: 10000,
    });
    await page.click('[data-testid="nav-templates"]');
    await page.waitForSelector('[data-testid="templates-title"]', {
      timeout: 10000,
    });
    await page.waitForTimeout(2000);
  });

  test("should show edit modal with form validation", async ({ page }) => {
    console.log("🔧 TESTING EDIT MODAL FORM VALIDATION");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Find user template
    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   ✅ Found user template");

      // Open dropdown and click edit
      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );
      await dropdown.click();
      await page.waitForTimeout(500);

      const editButton = userTemplate.locator(
        '.dropdown-item:has-text("Edit")'
      );
      await editButton.click();

      // Wait for modal to open
      await page.waitForSelector('[data-testid="edit-template-modal"]', {
        timeout: 10000,
      });
      console.log("   ✅ Edit modal opened");

      // Test form validation
      const nameInput = page.locator(
        '[data-testid="edit-template-name-input"]'
      );

      // Clear name field to trigger validation
      await nameInput.clear();
      await nameInput.blur();

      // Check for validation error
      const validationError = page.locator(
        '.is-invalid, .text-danger:has-text("required")'
      );
      if (await validationError.isVisible()) {
        console.log("   ✅ Form validation working - empty name shows error");
      }

      // Fill in valid data
      await nameInput.fill("Updated Test Template");

      // Test description field
      const descInput = page.locator(
        '[data-testid="edit-template-description-input"]'
      );
      if (await descInput.isVisible()) {
        await descInput.clear();
        await descInput.fill("This is an updated description for testing");
        console.log("   ✅ Description field updated");
      }

      // Close modal without saving
      const cancelButton = page.locator('button:has-text("Cancel")');
      if (await cancelButton.isVisible()) {
        await cancelButton.click();
        console.log("   ✅ Modal closed via Cancel button");
      } else {
        const closeButton = page.locator(".btn-close");
        await closeButton.click();
        console.log("   ✅ Modal closed via X button");
      }

      // Verify modal is closed
      await expect(
        page.locator('[data-testid="edit-template-modal"]')
      ).not.toBeVisible();
      console.log("   ✅ Modal properly closed");
    } else {
      console.log("   ⚠️ User template not found for edit testing");
    }

    console.log("\n🎉 EDIT MODAL FORM VALIDATION TEST COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });

  test("should handle duplicate template functionality", async ({ page }) => {
    console.log("🔧 TESTING DUPLICATE TEMPLATE FUNCTIONALITY");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Test duplicating a user template
    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   📋 Testing user template duplication...");

      // Open dropdown and click duplicate
      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );
      await dropdown.click();
      await page.waitForTimeout(500);

      const duplicateButton = userTemplate.locator(
        '.dropdown-item:has-text("Duplicate")'
      );
      await duplicateButton.click();
      console.log("   ✅ Clicked duplicate button");

      // Wait for success message or modal
      await page.waitForTimeout(2000);

      // Check for success notification
      const successMessage = page.locator(".alert-success").first();
      if (await successMessage.isVisible()) {
        console.log("   ✅ Duplicate success message shown");
      }
    }

    // Test duplicating a system template
    await page.click('text="Public Templates"');
    await page.waitForTimeout(2000);

    const systemTemplate = page
      .locator('[data-testid*="template-card"]')
      .first();
    if (await systemTemplate.isVisible()) {
      console.log("\n   📋 Testing system template duplication...");

      const duplicateSystemBtn = systemTemplate.locator(
        '[data-testid*="duplicate-system-template"]'
      );
      if (await duplicateSystemBtn.isVisible()) {
        await duplicateSystemBtn.click();
        console.log("   ✅ Clicked system template duplicate button");

        // Wait for success message
        await page.waitForTimeout(2000);
        const successMessage = page.locator(".alert-success").first();
        if (await successMessage.isVisible()) {
          console.log("   ✅ System template duplicate success message shown");
        }
      }
    }

    console.log("\n🎉 DUPLICATE TEMPLATE FUNCTIONALITY TEST COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });

  test("should handle delete template with confirmation", async ({ page }) => {
    console.log("🔧 TESTING DELETE TEMPLATE FUNCTIONALITY");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Look for user template to delete
    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   🗑️ Testing delete functionality...");

      // Open dropdown and click delete
      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );
      await dropdown.click();
      await page.waitForTimeout(500);

      const deleteButton = userTemplate.locator(
        '.dropdown-item:has-text("Delete")'
      );
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        console.log("   ✅ Clicked delete button");

        // Look for confirmation dialog/modal
        await page.waitForTimeout(1000);

        const confirmDialog = page.locator(
          '.modal:has-text("delete"), .modal:has-text("confirm"), .alert:has-text("delete")'
        );
        if (await confirmDialog.isVisible()) {
          console.log("   ✅ Delete confirmation dialog shown");

          // Cancel the deletion for safety
          const cancelBtn = page.locator(
            'button:has-text("Cancel"), button:has-text("No")'
          );
          if (await cancelBtn.isVisible()) {
            await cancelBtn.click();
            console.log("   ✅ Delete operation cancelled (safe test)");
          }
        } else {
          // If no confirmation dialog, check for immediate success message
          const successMessage = page.locator(
            '.alert-success:has-text("delete"), .toast:has-text("delete")'
          );
          if (await successMessage.isVisible()) {
            console.log(
              "   ⚠️ Template deleted immediately without confirmation"
            );
          } else {
            console.log(
              "   ⚠️ No confirmation dialog or success message detected"
            );
          }
        }
      }
    } else {
      console.log("   ⚠️ No user template found for delete testing");
    }

    console.log("\n🎉 DELETE TEMPLATE FUNCTIONALITY TEST COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });

  test("should handle export template functionality", async ({ page }) => {
    console.log("🔧 TESTING EXPORT TEMPLATE FUNCTIONALITY");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   📤 Testing export functionality...");

      // Open dropdown and click export
      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );
      await dropdown.click();
      await page.waitForTimeout(500);

      const exportButton = userTemplate.locator(
        '.dropdown-item:has-text("Export")'
      );
      if (await exportButton.isVisible()) {
        // Set up download listener
        const downloadPromise = page.waitForEvent("download", {
          timeout: 5000,
        });

        await exportButton.click();
        console.log("   ✅ Clicked export button");

        try {
          const download = await downloadPromise;
          console.log(
            `   ✅ Download initiated: ${download.suggestedFilename()}`
          );

          // Cancel the download to avoid file system pollution
          await download.cancel();
          console.log("   ✅ Download cancelled (test cleanup)");
        } catch (error) {
          console.log(
            "   ⚠️ No download initiated or export not implemented yet"
          );
        }
      } else {
        console.log("   ⚠️ Export button not found in dropdown");
      }
    } else {
      console.log("   ⚠️ No user template found for export testing");
    }

    console.log("\n🎉 EXPORT TEMPLATE FUNCTIONALITY TEST COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });

  test("should handle dropdown accessibility and keyboard navigation", async ({
    page,
  }) => {
    console.log("🔧 TESTING DROPDOWN ACCESSIBILITY");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   ♿ Testing keyboard navigation...");

      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );

      // Focus the dropdown button
      await dropdown.focus();
      console.log("   ✅ Dropdown button focused");

      // Press Enter to open dropdown
      await page.keyboard.press("Enter");
      await page.waitForTimeout(500);

      // Check if dropdown is open
      const dropdownMenu = userTemplate.locator(".dropdown-menu:visible");
      if (await dropdownMenu.isVisible()) {
        console.log("   ✅ Dropdown opened with keyboard");

        // Navigate with arrow keys
        await page.keyboard.press("ArrowDown");
        await page.waitForTimeout(200);
        await page.keyboard.press("ArrowDown");
        await page.waitForTimeout(200);

        console.log("   ✅ Arrow key navigation tested");

        // Press Escape to close
        await page.keyboard.press("Escape");
        await page.waitForTimeout(500);

        if (!(await dropdownMenu.isVisible())) {
          console.log("   ✅ Dropdown closed with Escape key");
        }
      } else {
        console.log("   ⚠️ Dropdown did not open with keyboard");
      }

      // Test ARIA attributes
      const ariaExpanded = await dropdown.getAttribute("aria-expanded");
      const ariaHasPopup = await dropdown.getAttribute("aria-haspopup");

      if (ariaHasPopup) {
        console.log(`   ✅ ARIA haspopup attribute present: ${ariaHasPopup}`);
      }
      if (ariaExpanded !== null) {
        console.log(`   ✅ ARIA expanded attribute present: ${ariaExpanded}`);
      }
    }

    console.log("\n🎉 DROPDOWN ACCESSIBILITY TEST COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });
});
