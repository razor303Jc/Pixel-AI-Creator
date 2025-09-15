const { test, expect } = require("@playwright/test");

test.describe("Debug Edit Modal with Console", () => {
  test.beforeEach(async ({ page }) => {
    // Listen for console messages
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log("❌ BROWSER ERROR:", msg.text());
      } else if (msg.type() === "warning") {
        console.log("⚠️ BROWSER WARNING:", msg.text());
      } else {
        console.log("ℹ️ BROWSER:", msg.text());
      }
    });

    // Listen for page errors
    page.on("pageerror", (exception) => {
      console.log("💥 PAGE ERROR:", exception.message);
    });

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

  test("debug edit modal with console monitoring", async ({ page }) => {
    console.log("🔧 DEBUGGING EDIT MODAL WITH CONSOLE MONITORING");
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
      console.log("   🔍 About to click edit button...");

      // Click edit and monitor for errors
      await editButton.click();

      console.log("   ✅ Edit button clicked");

      // Wait longer and check
      await page.waitForTimeout(3000);

      // Check current page state
      const pageTitle = await page.title();
      console.log(`   📄 Current page title: ${pageTitle}`);

      // Check for edit modal again
      const editModal = page.locator('[data-testid="edit-template-modal"]');
      const editModalVisible = await editModal.isVisible();
      console.log(`   🎯 Edit modal visible: ${editModalVisible}`);

      if (!editModalVisible) {
        // Try to find any modal that might be open
        const anyModal = page.locator(
          '.modal.show, .modal[style*="display: block"]'
        );
        const anyModalVisible = await anyModal.isVisible();
        console.log(`   🔍 Any modal visible: ${anyModalVisible}`);

        if (anyModalVisible) {
          const modalContent = await anyModal.textContent();
          console.log(
            `   📝 Modal content: ${modalContent?.substring(0, 100)}...`
          );
        }
      }

      // Also check React state by evaluating JavaScript
      const reactState = await page.evaluate(() => {
        // Try to find React component state
        const templateCards = document.querySelectorAll(
          '[data-testid*="template-card"]'
        );
        return {
          templateCardsCount: templateCards.length,
          hasModals: document.querySelectorAll(".modal").length,
          hasShowModalClass: document.querySelectorAll(".modal.show").length,
        };
      });

      console.log(`   🔍 React state check:`, reactState);
    }

    console.log("\n🎉 DEBUG WITH CONSOLE COMPLETE!");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });
});
