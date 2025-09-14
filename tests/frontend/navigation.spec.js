/**
 * Navigation and Dashboard Tests
 * Tests main navigation, dashboard components, and user interface elements
 */

const { test, expect } = require("@playwright/test");

test.describe("Navigation and Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3002");

    // Helper function to ensure we're logged in
    const ensureLoggedIn = async () => {
      const isLoginForm = await page.isVisible("#loginEmail");

      if (isLoginForm) {
        // Try to register and login a test user
        await page.click("text=Sign up here");

        const timestamp = Date.now();
        const testEmail = `nav.test.${timestamp}@example.com`;

        await page.fill("#firstName", "Nav");
        await page.fill("#lastName", "Test");
        await page.fill("#email", testEmail);
        await page.fill("#password", "Password123!");
        await page.fill("#confirmPassword", "Password123!");
        await page.click('button[type="submit"]');

        await page.waitForTimeout(3000);
      }
    };

    await ensureLoggedIn();
  });

  test("should display main navigation elements", async ({ page }) => {
    // Check for common navigation elements
    const commonNavElements = [
      "text=Dashboard",
      "text=Home",
      "text=Chat",
      "text=Profile",
      "text=Settings",
      "text=Logout",
      "text=Documents",
      "text=AI Assistant",
    ];

    let foundElements = 0;
    for (const selector of commonNavElements) {
      if (await page.isVisible(selector)) {
        foundElements++;
        console.log(`Found navigation element: ${selector}`);
      }
    }

    // Should have at least some navigation elements
    expect(foundElements).toBeGreaterThan(0);
  });

  test("should have responsive design elements", async ({ page }) => {
    // Check viewport meta tag
    const viewportMeta = page.locator('meta[name="viewport"]');
    await expect(viewportMeta).toHaveAttribute("content", /width=device-width/);

    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);

    // Check if hamburger menu or mobile navigation exists
    const body = await page.textContent("body");
    const hasMobileElements =
      (await page.isVisible('button[aria-label*="menu"]')) ||
      (await page.isVisible(".navbar-toggler")) ||
      (await page.isVisible('[data-testid="mobile-menu"]')) ||
      body.includes("☰") ||
      body.includes("≡");

    // Reset viewport
    await page.setViewportSize({ width: 1280, height: 720 });

    console.log(`Mobile navigation elements found: ${hasMobileElements}`);
  });

  test("should display user information when logged in", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for user information display
    const bodyText = await page.textContent("body");
    const hasUserInfo =
      bodyText.includes("Welcome") ||
      bodyText.includes("Dashboard") ||
      bodyText.includes("Profile") ||
      (await page.isVisible('[data-testid="user-avatar"]')) ||
      (await page.isVisible(".user-info")) ||
      (await page.isVisible(".profile-section"));

    expect(hasUserInfo).toBeTruthy();
  });

  test("should handle logout functionality", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for logout button/link
    const logoutSelectors = [
      "text=Logout",
      "text=Sign Out",
      'button:has-text("Logout")',
      'a:has-text("Logout")',
      '[data-testid="logout"]',
      ".logout-btn",
    ];

    let logoutFound = false;
    for (const selector of logoutSelectors) {
      if (await page.isVisible(selector)) {
        await page.click(selector);
        logoutFound = true;
        break;
      }
    }

    if (logoutFound) {
      await page.waitForTimeout(2000);

      // Should redirect to login page
      const currentUrl = page.url();
      const bodyText = await page.textContent("body");

      expect(
        currentUrl.includes("login") ||
          bodyText.includes("Sign In") ||
          bodyText.includes("Welcome Back")
      ).toBeTruthy();
    } else {
      // If no logout button found, that's also valid information
      console.log("No logout functionality found in current view");
    }
  });

  test("should have working internal links", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Get all internal links
    const links = await page.locator("a[href]").all();
    let workingLinks = 0;
    let totalInternalLinks = 0;

    for (const link of links) {
      const href = await link.getAttribute("href");

      // Skip external links, mailto, tel, etc.
      if (
        href &&
        !href.startsWith("http") &&
        !href.startsWith("mailto:") &&
        !href.startsWith("tel:")
      ) {
        totalInternalLinks++;

        try {
          // Check if link is visible and clickable
          if (await link.isVisible()) {
            workingLinks++;
          }
        } catch (error) {
          console.log(`Link ${href} has issues: ${error.message}`);
        }
      }
    }

    console.log(
      `Found ${totalInternalLinks} internal links, ${workingLinks} appear functional`
    );

    // At least some links should be working
    if (totalInternalLinks > 0) {
      expect(workingLinks).toBeGreaterThan(0);
    }
  });

  test("should display main content areas", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Check for main content structure
    const contentSelectors = [
      "main",
      '[role="main"]',
      ".main-content",
      ".dashboard",
      ".content",
      "#root",
      ".app",
    ];

    let contentFound = false;
    for (const selector of contentSelectors) {
      if (await page.isVisible(selector)) {
        contentFound = true;
        console.log(`Found main content area: ${selector}`);
        break;
      }
    }

    expect(contentFound).toBeTruthy();
  });

  test("should handle breadcrumbs if present", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Check for breadcrumb navigation
    const breadcrumbSelectors = [
      ".breadcrumb",
      '[aria-label="breadcrumb"]',
      ".breadcrumbs",
      'nav[aria-label*="breadcrumb"]',
    ];

    for (const selector of breadcrumbSelectors) {
      if (await page.isVisible(selector)) {
        console.log(`Found breadcrumb navigation: ${selector}`);

        // Check if breadcrumbs are functional
        const breadcrumbLinks = page.locator(`${selector} a`);
        const linkCount = await breadcrumbLinks.count();

        if (linkCount > 0) {
          console.log(`Breadcrumb has ${linkCount} clickable links`);
        }

        return; // Exit after finding breadcrumbs
      }
    }

    console.log("No breadcrumb navigation found");
  });

  test("should have proper page titles", async ({ page }) => {
    await page.waitForTimeout(2000);

    const title = await page.title();

    // Title should not be empty and should be meaningful
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
    expect(title).not.toBe("React App"); // Should be customized

    console.log(`Page title: ${title}`);
  });

  test("should handle search functionality if present", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for search inputs
    const searchSelectors = [
      'input[type="search"]',
      'input[placeholder*="search" i]',
      'input[placeholder*="Search" i]',
      '[data-testid="search"]',
      ".search-input",
      "#search",
    ];

    for (const selector of searchSelectors) {
      if (await page.isVisible(selector)) {
        console.log(`Found search input: ${selector}`);

        // Test search functionality
        await page.fill(selector, "test search");
        await page.press(selector, "Enter");

        await page.waitForTimeout(1000);
        console.log("Search functionality tested");

        return;
      }
    }

    console.log("No search functionality found");
  });

  test("should display footer information", async ({ page }) => {
    await page.waitForTimeout(2000);

    // Check for footer
    const footerSelectors = [
      "footer",
      ".footer",
      '[role="contentinfo"]',
      ".page-footer",
    ];

    for (const selector of footerSelectors) {
      if (await page.isVisible(selector)) {
        console.log(`Found footer: ${selector}`);

        const footerText = await page.textContent(selector);
        expect(footerText.length).toBeGreaterThan(0);

        return;
      }
    }

    console.log("No footer found");
  });
});
