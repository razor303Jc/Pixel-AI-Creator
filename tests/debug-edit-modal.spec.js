const { test, expect } = require("@playwright/test");

test.describe("Debug Edit Modal", () => {
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

  test("debug edit modal opening", async ({ page }) => {
    console.log("🔧 DEBUGGING EDIT MODAL");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Take screenshot before action
    await page.screenshot({
      path: "test-results/debug-before-edit.png",
      fullPage: true,
    });

    // Find user template
    const userTemplate = page
      .locator(
        '[data-testid*="template-card"]:has-text("My Custom Sales Assistant")'
      )
      .first();

    if (await userTemplate.isVisible()) {
      console.log("   ✅ Found user template");

      // Take screenshot of template card
      await userTemplate.screenshot({
        path: "test-results/debug-template-card.png",
      });

      // Open dropdown
      const dropdown = userTemplate.locator(
        '[data-testid*="template-dropdown"]'
      );
      console.log("   🔍 Clicking dropdown...");
      await dropdown.click();
      await page.waitForTimeout(1000);

      // Take screenshot after dropdown click
      await page.screenshot({
        path: "test-results/debug-after-dropdown.png",
        fullPage: true,
      });

      // Check if dropdown menu is visible
      const dropdownMenu = page.locator(
        ".dropdown-menu:visible, .show .dropdown-menu"
      );
      if (await dropdownMenu.isVisible()) {
        console.log("   ✅ Dropdown menu is visible");

        // Take screenshot of dropdown menu
        await dropdownMenu.screenshot({
          path: "test-results/debug-dropdown-menu.png",
        });

        // List all dropdown items
        const items = await dropdownMenu.locator(".dropdown-item").all();
        console.log(`   📋 Found ${items.length} dropdown items:`);

        for (let i = 0; i < items.length; i++) {
          const text = await items[i].textContent();
          const testId = await items[i].getAttribute("data-testid");
          console.log(`      ${i + 1}. "${text}" (testid: ${testId})`);
        }

        // Find and click edit button
        const editButton = dropdownMenu.locator(
          '.dropdown-item:has-text("Edit")'
        );
        if (await editButton.isVisible()) {
          console.log("   ✅ Edit button found and visible");

          // Take screenshot before clicking edit
          await page.screenshot({
            path: "test-results/debug-before-edit-click.png",
            fullPage: true,
          });

          console.log("   🔍 Clicking edit button...");
          await editButton.click();

          // Wait and check for modal
          await page.waitForTimeout(2000);

          // Take screenshot after edit click
          await page.screenshot({
            path: "test-results/debug-after-edit-click.png",
            fullPage: true,
          });

          // Check for any modals
          const allModals = page.locator('.modal, [data-testid*="modal"]');
          const visibleModals = await allModals.all();
          console.log(`   📋 Found ${visibleModals.length} modal elements:`);

          for (let i = 0; i < visibleModals.length; i++) {
            const isVisible = await visibleModals[i].isVisible();
            const testId = await visibleModals[i].getAttribute("data-testid");
            const className = await visibleModals[i].getAttribute("class");
            console.log(
              `      ${
                i + 1
              }. Visible: ${isVisible}, TestId: ${testId}, Class: ${className}`
            );
          }

          // Specifically check for edit modal
          const editModal = page.locator('[data-testid="edit-template-modal"]');
          const editModalVisible = await editModal.isVisible();
          console.log(
            `   🎯 Edit modal specifically: Visible = ${editModalVisible}`
          );

          if (editModalVisible) {
            console.log("   ✅ Edit modal is visible!");
          } else {
            console.log("   ❌ Edit modal is not visible");

            // Check for any errors in console
            page.on("console", (msg) => console.log("BROWSER:", msg.text()));
            page.on("pageerror", (exception) =>
              console.log("PAGE ERROR:", exception)
            );
          }
        } else {
          console.log("   ❌ Edit button not found or not visible");
        }
      } else {
        console.log("   ❌ Dropdown menu is not visible");
      }
    } else {
      console.log("   ❌ User template not found");
    }

    console.log("\n🎉 DEBUG COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });
});
