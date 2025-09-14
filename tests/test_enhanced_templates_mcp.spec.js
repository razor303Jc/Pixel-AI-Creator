import { test, expect } from "@playwright/test";

/**
 * Enhanced Templates Testing Suite
 * Tests the new MCP-enabled templates with tools and integrations
 */

test.describe("Enhanced Templates with MCP Integration", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:3002");
    await page.waitForLoadState("networkidle");
    
    // Check if we need to register/login
    const signUpLink = page.locator('a:has-text("Sign up here"), .signup-link, a[href*="signup"]');
    const signInButton = page.locator('button:has-text("Sign In"), .btn:has-text("Sign In")');
    
    if (await signUpLink.isVisible({ timeout: 3000 })) {
      console.log("📝 Registering new test user...");
      
      // Click sign up link
      await signUpLink.click();
      await page.waitForTimeout(2000);
      
      // Fill registration form - use unique email to avoid conflicts
      const timestamp = Date.now();
      const testEmail = `test${timestamp}@example.com`;
      
      await page.fill('input[name="first_name"], input[placeholder*="First" i], input[id*="firstName"]', 'Test');
      await page.fill('input[name="last_name"], input[placeholder*="Last" i], input[id*="lastName"]', 'User');
      await page.fill('input[name="email"], input[type="email"], input[placeholder*="email" i]', testEmail);
      await page.fill('input[name="password"], input[type="password"], input[placeholder*="Password" i]', 'TestPass123!');
      await page.fill('input[name="company_name"], input[placeholder*="Company" i], input[id*="company"]', 'Test Company');
      await page.fill('input[name="phone"], input[type="tel"], input[placeholder*="Phone" i]', '123-456-7890');
      
      // Submit registration
      await page.click('button[type="submit"], .btn-primary, button:has-text("Sign Up")');
      await page.waitForTimeout(3000);
      
      // Check if registration was successful or if we need to login
      if (await signInButton.isVisible({ timeout: 3000 })) {
        console.log("🔐 Registration successful, now logging in...");
        
        // Fill login form
        await page.fill('input[name="email"], input[type="email"], input[placeholder*="email" i]', testEmail);
        await page.fill('input[name="password"], input[type="password"], input[placeholder*="Password" i]', 'TestPass123!');
        
        // Submit login
        await page.click('button[type="submit"], .btn-primary, button:has-text("Sign In")');
        await page.waitForTimeout(3000);
      }
    } else if (await signInButton.isVisible({ timeout: 3000 })) {
      console.log("🔐 Attempting to login with existing test user...");
      
      // Try with a common test account
      await page.fill('input[name="email"], input[type="email"], input[placeholder*="email" i]', 'test@example.com');
      await page.fill('input[name="password"], input[type="password"], input[placeholder*="Password" i]', 'TestPass123!');
      
      // Submit login
      await page.click('button[type="submit"], .btn-primary, button:has-text("Sign In")');
      await page.waitForTimeout(3000);
    }
    
    // Wait for dashboard to load - look for any common dashboard elements
    await page.waitForSelector('nav, .navbar, .dashboard, .main-content, .sidebar, .nav-tabs', { timeout: 15000 });
    
    // Look for Templates section - try multiple approaches
    const templatesSelectors = [
      'a:has-text("Templates")',
      '.nav-link:has-text("Templates")',
      'button:has-text("Templates")',
      '[href="#templates"]',
      '.nav-tabs a:nth-child(2)', // Templates is often the second tab
      '.nav-tabs .nav-link:contains("Templates")'
    ];
    
    let templatesFound = false;
    for (const selector of templatesSelectors) {
      try {
        const element = page.locator(selector);
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          templatesFound = true;
          console.log(`✅ Found and clicked templates with selector: ${selector}`);
          await page.waitForTimeout(1000);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    if (!templatesFound) {
      console.log("⚠️  Templates tab not found, taking screenshot for debugging...");
      await page.screenshot({
        path: "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/debug-dashboard.png",
        fullPage: true
      });
    }
    
    // Wait for templates content to load
    await page.waitForSelector('.card, .template-card, .item, .content-area', { timeout: 10000 });
  });

  test("should display MCP-enabled templates", async ({ page }) => {
    console.log("🔍 Testing MCP-enabled templates display...");

    // Check for Executive Personal Assistant (MCP) template
    const paTemplate = page.locator('.card:has-text("Executive Personal Assistant")');
    await expect(paTemplate).toBeVisible();
    
    // Verify MCP is mentioned in the template
    await expect(paTemplate).toContainText("MCP");
    await expect(paTemplate).toContainText("calendar");
    await expect(paTemplate).toContainText("email");

    console.log("✅ Executive Personal Assistant (MCP) template found");
  });

  test("should display Project Manager Pro with MCP tools", async ({ page }) => {
    console.log("🔍 Testing Project Manager Pro (MCP) template...");

    const pmTemplate = page.locator('.card:has-text("Project Manager Pro")');
    await expect(pmTemplate).toBeVisible();
    
    // Verify MCP and project management features
    await expect(pmTemplate).toContainText("MCP");
    await expect(pmTemplate).toContainText("task tracking");
    await expect(pmTemplate).toContainText("team coordination");

    console.log("✅ Project Manager Pro (MCP) template found");
  });

  test("should display Social Media Manager with integrations", async ({ page }) => {
    console.log("🔍 Testing Social Media Manager (MCP) template...");

    const socialTemplate = page.locator('.card:has-text("Social Media Manager")');
    await expect(socialTemplate).toBeVisible();
    
    // Verify social media and MCP features
    await expect(socialTemplate).toContainText("MCP");
    await expect(socialTemplate).toContainText("multi-platform");
    await expect(socialTemplate).toContainText("analytics");

    console.log("✅ Social Media Manager (MCP) template found");
  });

  test("should display Data Analytics Assistant", async ({ page }) => {
    console.log("🔍 Testing Data Analytics Assistant (MCP) template...");

    const analyticsTemplate = page.locator('.card:has-text("Data Analytics Assistant")');
    await expect(analyticsTemplate).toBeVisible();
    
    // Verify analytics and MCP features
    await expect(analyticsTemplate).toContainText("MCP");
    await expect(analyticsTemplate).toContainText("database");
    await expect(analyticsTemplate).toContainText("visualization");

    console.log("✅ Data Analytics Assistant (MCP) template found");
  });

  test("should display Customer Support Pro with CRM integration", async ({ page }) => {
    console.log("🔍 Testing Customer Support Pro (MCP) template...");

    const supportTemplate = page.locator('.card:has-text("Customer Support Pro")');
    await expect(supportTemplate).toBeVisible();
    
    // Verify CRM and MCP features
    await expect(supportTemplate).toContainText("MCP");
    await expect(supportTemplate).toContainText("CRM");
    await expect(supportTemplate).toContainText("ticketing");

    console.log("✅ Customer Support Pro (MCP) template found");
  });

  test("should display DevOps Assistant", async ({ page }) => {
    console.log("🔍 Testing DevOps Assistant (MCP) template...");

    const devopsTemplate = page.locator('.card:has-text("DevOps Assistant")');
    await expect(devopsTemplate).toBeVisible();
    
    // Verify DevOps and MCP features
    await expect(devopsTemplate).toContainText("MCP");
    await expect(devopsTemplate).toContainText("CI/CD");
    await expect(devopsTemplate).toContainText("infrastructure");

    console.log("✅ DevOps Assistant (MCP) template found");
  });

  test("should have updated category filters", async ({ page }) => {
    console.log("🔍 Testing category filters...");

    // Check for new categories: PA, PM, M&S, A&D
    const expectedCategories = ["PA", "PM", "M&S", "A&D"];
    
    for (const category of expectedCategories) {
      const categoryFilter = page.locator(`button:has-text("${category}"), .btn:has-text("${category}"), [data-category="${category}"]`);
      await expect(categoryFilter).toBeVisible();
      console.log(`✅ Found category filter: ${category}`);
    }
  });

  test("should filter templates by PA category", async ({ page }) => {
    console.log("🔍 Testing PA category filtering...");

    // Click PA category filter
    await page.click('button:has-text("PA"), .btn:has-text("PA"), [data-category="PA"]');
    
    // Wait for filtering to complete
    await page.waitForTimeout(500);
    
    // Should show Executive Personal Assistant
    const paTemplate = page.locator('.card:has-text("Executive Personal Assistant")');
    await expect(paTemplate).toBeVisible();
    
    // Should have PA badge
    const paBadge = page.locator('.badge:has-text("PA")');
    await expect(paBadge).toBeVisible();

    console.log("✅ PA category filtering works");
  });

  test("should filter templates by PM category", async ({ page }) => {
    console.log("🔍 Testing PM category filtering...");

    // Click PM category filter
    await page.click('button:has-text("PM"), .btn:has-text("PM"), [data-category="PM"]');
    
    // Wait for filtering to complete
    await page.waitForTimeout(500);
    
    // Should show Project Manager Pro
    const pmTemplate = page.locator('.card:has-text("Project Manager Pro")');
    await expect(pmTemplate).toBeVisible();

    console.log("✅ PM category filtering works");
  });

  test("should filter templates by M&S category", async ({ page }) => {
    console.log("🔍 Testing M&S category filtering...");

    // Click M&S category filter
    await page.click('button:has-text("M&S"), .btn:has-text("M&S"), [data-category="M&S"]');
    
    // Wait for filtering to complete
    await page.waitForTimeout(500);
    
    // Should show Social Media Manager
    const socialTemplate = page.locator('.card:has-text("Social Media Manager")');
    await expect(socialTemplate).toBeVisible();

    console.log("✅ M&S category filtering works");
  });

  test("should filter templates by A&D category", async ({ page }) => {
    console.log("🔍 Testing A&D category filtering...");

    // Click A&D category filter
    await page.click('button:has-text("A&D"), .btn:has-text("A&D"), [data-category="A&D"]');
    
    // Wait for filtering to complete
    await page.waitForTimeout(500);
    
    // Should show Data Analytics Assistant
    const analyticsTemplate = page.locator('.card:has-text("Data Analytics Assistant")');
    await expect(analyticsTemplate).toBeVisible();

    console.log("✅ A&D category filtering works");
  });

  test("should search for MCP templates", async ({ page }) => {
    console.log("🔍 Testing MCP template search...");

    // Find and use the search input
    const searchInput = page.locator('input[placeholder*="Search"], input[type="search"], .form-control:has([placeholder*="search" i])');
    await searchInput.fill("MCP");
    
    // Wait for search to filter
    await page.waitForTimeout(500);
    
    // Should show multiple MCP templates
    const mcpTemplates = page.locator('.card:has-text("MCP")');
    await expect(mcpTemplates.first()).toBeVisible();
    
    // Count should be at least 6 (our 6 MCP templates)
    const mcpCount = await mcpTemplates.count();
    expect(mcpCount).toBeGreaterThanOrEqual(6);

    console.log(`✅ Found ${mcpCount} MCP templates in search`);
  });

  test("should display template usage counts", async ({ page }) => {
    console.log("🔍 Testing template usage counts...");

    // Check that templates show usage statistics
    const usageStats = page.locator('.card:has-text("usage"), .card:has-text("used")');
    await expect(usageStats.first()).toBeVisible();

    console.log("✅ Template usage counts are displayed");
  });

  test("should show template creation and edit functionality", async ({ page }) => {
    console.log("🔍 Testing template creation button...");

    // Look for create template button
    const createButton = page.locator('button:has-text("Create"), .btn:has-text("Create"), button:has-text("New Template")');
    await expect(createButton.first()).toBeVisible();

    console.log("✅ Template creation functionality is available");
  });

  test("should validate template card structure", async ({ page }) => {
    console.log("🔍 Testing template card structure...");

    // Get the first template card
    const firstCard = page.locator('.card').first();
    await expect(firstCard).toBeVisible();
    
    // Should have title, description, category badge
    await expect(firstCard.locator('.card-title, h5, h4')).toBeVisible();
    await expect(firstCard.locator('.card-text, p')).toBeVisible();
    await expect(firstCard.locator('.badge')).toBeVisible();

    console.log("✅ Template card structure is correct");
  });

  test("should take screenshot of enhanced templates page", async ({ page }) => {
    console.log("📸 Taking screenshot of enhanced templates page...");

    // Ensure we're showing all templates
    await page.click('button:has-text("all"), .btn:has-text("all"), [data-category="all"]');
    await page.waitForTimeout(1000);

    // Take full page screenshot
    await page.screenshot({
      path: "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/enhanced-templates-screenshot.png",
      fullPage: true
    });

    console.log("📸 Screenshot saved: enhanced-templates-screenshot.png");
  });
});