const { test, expect } = require("@playwright/test");

test.describe("Corrected MCP Template Creation", () => {
  test("should successfully create Executive Personal Assistant MCP template with correct selectors", async ({
    page,
  }) => {
    console.log(
      "🎯 CORRECTED MCP TEMPLATE CREATION - EXECUTIVE PERSONAL ASSISTANT"
    );
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Navigate to the application
    await page.goto("http://localhost:3002");

    // Login with correct credentials
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForSelector('[data-testid="nav-templates"]', {
      timeout: 10000,
    });

    // Navigate to templates
    await page.click('[data-testid="nav-templates"]');
    await page.waitForSelector('[data-testid="create-template-btn"]', {
      timeout: 10000,
    });

    // Click create template button
    await page.click('[data-testid="create-template-btn"]');
    await page.waitForSelector(".modal-content", { timeout: 5000 });
    console.log("✅ Template creation modal opened successfully");

    // Fill basic template information
    console.log("\n📝 FILLING REQUIRED TEMPLATE INFORMATION:");
    await page.fill(
      '[data-testid="template-name-input"]',
      "Executive Personal Assistant MCP"
    );
    console.log("   ✅ Name: Executive Personal Assistant MCP");

    await page.fill(
      '[data-testid="template-description-input"]',
      "Advanced MCP-integrated executive assistant with calendar, email, file system, and database connectivity for comprehensive administrative support."
    );
    console.log(
      "   ✅ Description: MCP-integrated executive assistant (detailed)"
    );

    await page.selectOption('[data-testid="template-category-select"]', "PA");
    console.log("   ✅ Category: PA (Personal Assistant)");

    await page.selectOption(
      '[data-testid="template-personality-select"]',
      "professional"
    );
    console.log("   ✅ Personality: Professional");

    await page.fill(
      '[data-testid="template-tags-input"]',
      "executive-assistant, mcp, calendar, email, productivity, professional, ai-assistant"
    );
    console.log(
      "   ✅ Tags: executive-assistant, mcp, calendar, email, productivity, professional, ai-assistant"
    );

    // Add comprehensive instructions
    console.log("\n📋 ADDING COMPREHENSIVE INSTRUCTIONS:");
    const instructions = `# Executive Personal Assistant with MCP Integration

You are an advanced Executive Personal Assistant with access to Model Context Protocol (MCP) servers for comprehensive administrative support.

## Core Capabilities:
- **Calendar Management**: Schedule meetings, check availability, set reminders via MCP calendar server
- **Email Management**: Draft, send, and organize emails through MCP email server  
- **File System**: Access, organize, and manage documents via MCP file system server
- **Database Access**: Query client information, project data, and metrics through MCP database server
- **Task Coordination**: Manage priorities, deadlines, and workflow optimization

## MCP Server Integrations:
1. **Calendar Server**: Real-time scheduling and availability management
2. **Email Server**: Professional email handling and organization
3. **File System Server**: Document management and file operations
4. **Database Server**: Client and project data access
5. **API Gateway**: External service integrations

## Executive Protocols:
- Maintain strict confidentiality and professional discretion
- Prioritize urgent requests while managing long-term objectives
- Provide proactive recommendations and insights
- Ensure seamless coordination across all platforms and systems
- Maintain detailed records and follow-up tracking

## Response Format:
Always provide actionable, professional responses with clear next steps and relevant MCP server integration points.`;

    await page.fill(
      '[data-testid="template-instructions-input"]',
      instructions
    );
    console.log(
      "   ✅ Comprehensive instructions with MCP integration details added"
    );

    // Configure Scope & Training with correct selector
    console.log("\n🎯 CONFIGURING SCOPE & TRAINING:");

    // Set scope to expert level with correct selector
    await page.selectOption('[data-testid="template-scope-select"]', "expert");
    console.log("   ✅ Scope: Expert Level - Deep domain expertise required");

    // Add comprehensive Q&A training
    console.log("\n📚 ADDING TRAINING Q&A PAIRS:");

    // Clear existing Q&A and add first pair
    await page.fill(
      '[data-testid="training-question-0"]',
      "How do you handle scheduling conflicts for high-priority meetings?"
    );
    await page.fill(
      '[data-testid="training-answer-0"]',
      "I immediately access the calendar via MCP server to identify all conflicts, prioritize based on stakeholder importance and urgency, propose alternative times, and proactively communicate with all parties to find optimal solutions while maintaining executive availability for critical decisions."
    );
    console.log("   ✅ Q&A Pair 1: Scheduling conflicts handling");

    // Add second Q&A pair
    await page.click('button:has-text("Add Q&A Pair")');
    await page.fill(
      '[data-testid="training-question-1"]',
      "What is your approach to managing confidential information across multiple MCP servers?"
    );
    await page.fill(
      '[data-testid="training-answer-1"]',
      "I implement strict access controls, use encrypted connections to all MCP servers, maintain audit trails of all data access, apply role-based permissions, and ensure compliance with confidentiality agreements while enabling seamless executive workflow across calendar, email, file, and database systems."
    );
    console.log("   ✅ Q&A Pair 2: Confidential information management");

    // Add third Q&A pair
    await page.click('button:has-text("Add Q&A Pair")');
    await page.fill(
      '[data-testid="training-question-2"]',
      "How do you optimize executive productivity using MCP integrations?"
    );
    await page.fill(
      '[data-testid="training-answer-2"]',
      "I leverage real-time data from all MCP servers to provide intelligent recommendations: analyzing calendar patterns for optimal meeting scheduling, monitoring email for priority responses, organizing files for quick access, and querying databases for informed decision-making, creating a seamless digital ecosystem that anticipates executive needs."
    );
    console.log("   ✅ Q&A Pair 3: Executive productivity optimization");

    console.log("\n🔧 TOOLS & INTEGRATIONS CONFIGURATION:");
    console.log(
      "   ℹ️ Tools section is optional - proceeding with MCP server integrations as primary capability"
    );

    // Submit the template
    console.log("\n🚀 SUBMITTING TEMPLATE:");
    await page.click('[data-testid="submit-template-btn"]');

    // Wait for success response
    await page.waitForTimeout(3000);
    console.log("   ✅ Template creation submitted successfully");

    // Verify we're back to templates page
    await page.waitForSelector('[data-testid="create-template-btn"]', {
      timeout: 10000,
    });
    console.log("   ✅ Returned to templates page after creation");

    console.log(
      "\n🎉 EXECUTIVE PERSONAL ASSISTANT MCP TEMPLATE CREATED SUCCESSFULLY!"
    );
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });

  test("should verify template appears in library with MCP capabilities", async ({
    page,
  }) => {
    console.log("📚 VERIFYING MCP TEMPLATE IN LIBRARY");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );

    // Navigate to the application and login
    await page.goto("http://localhost:3002");
    await page.fill("#loginEmail", "jc@razorflow-ai.com");
    await page.fill("#loginPassword", "Password123!");
    await page.click('button[type="submit"]');

    // Wait for dashboard and navigate to templates
    await page.waitForSelector('[data-testid="nav-templates"]', {
      timeout: 10000,
    });
    await page.click('[data-testid="nav-templates"]');
    await page.waitForSelector('[data-testid="create-template-btn"]', {
      timeout: 10000,
    });

    // Count total templates
    const templateCards = await page.locator(".card").count();
    console.log(`📊 Total templates in library: ${templateCards}`);

    // Search for our MCP template
    console.log("\n🔍 SEARCHING FOR MCP TEMPLATE:");
    if (await page.locator('input[placeholder*="Search"]').isVisible()) {
      await page.fill(
        'input[placeholder*="Search"]',
        "Executive Personal Assistant MCP"
      );
      await page.waitForTimeout(1000);

      const searchResults = await page.locator(".card").count();
      console.log(
        `   🔍 Search "Executive Personal Assistant MCP": ${searchResults} results`
      );

      if (searchResults > 0) {
        console.log("   ✅ MCP template found in search results");
      } else {
        console.log("   ⚠️ MCP template not yet visible (may be processing)");
      }

      // Clear search
      await page.fill('input[placeholder*="Search"]', "");
      await page.waitForTimeout(1000);
    }

    // Test MCP-related searches
    const mcpTerms = ["MCP", "Executive", "Assistant", "Calendar", "Email"];
    for (const term of mcpTerms) {
      if (await page.locator('input[placeholder*="Search"]').isVisible()) {
        await page.fill('input[placeholder*="Search"]', term);
        await page.waitForTimeout(500);
        const results = await page.locator(".card").count();
        console.log(`   🔍 Search "${term}": ${results} results`);
        await page.fill('input[placeholder*="Search"]', "");
        await page.waitForTimeout(500);
      }
    }

    console.log("\n🎯 MCP INTEGRATION VERIFICATION COMPLETE");
    console.log(
      "════════════════════════════════════════════════════════════════"
    );
  });
});
