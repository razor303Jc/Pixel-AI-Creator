const { test, expect } = require('@playwright/test');

test.describe('RazorFlow Human-like Workflow Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3002');
    
    // Login with test user
    await page.fill('[data-testid="email-input"]', 'jc@razorflow-ai.com');
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.click('[data-testid="login-submit"]');
    
    // Wait for login to complete and navigate to Templates
    await page.waitForSelector('[data-testid="sidebar-templates"]', { timeout: 10000 });
    await page.click('[data-testid="sidebar-templates"]');
    
    // Wait for Templates page to load
    await page.waitForSelector('[data-testid="add-template-btn"]', { timeout: 10000 });
  });

  test('should complete human-like workflow: create client then template', async ({ page }) => {
    // Step 1: Navigate to Clients page first (human-like behavior)
    await page.click('[data-testid="sidebar-clients"]');
    await page.waitForSelector('[data-testid="add-client-btn"]', { timeout: 5000 });
    
    // Step 2: Create a new client - Razor 303 at RazorFlow-AI
    await page.click('[data-testid="add-client-btn"]');
    await page.waitForSelector('[data-testid="create-client-modal"]');
    
    await page.fill('[data-testid="client-name-input"]', 'Razor 303');
    await page.fill('[data-testid="client-email-input"]', 'razor303@razorflow-ai.com');
    await page.fill('[data-testid="client-company-input"]', 'RazorFlow-AI');
    await page.fill('[data-testid="client-phone-input"]', '+1-555-0303');
    await page.selectOption('[data-testid="client-industry-select"]', 'Technology');
    await page.fill('[data-testid="client-description-input"]', 'AI and automation solutions');
    
    await page.click('[data-testid="create-client-submit"]');
    await page.waitForSelector('[data-testid="success-message"]', { timeout: 5000 });
    
    // Step 3: Navigate back to Templates (human behavior - move between sections)
    await page.click('[data-testid="sidebar-templates"]');
    await page.waitForSelector('[data-testid="add-template-btn"]');
    
    // Step 4: Create a custom template with advanced features
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Basic template information
    await page.fill('[data-testid="template-name-input"]', 'Custom RazorFlow Assistant');
    await page.fill('[data-testid="template-description-input"]', 'Specialized AI assistant for RazorFlow operations');
    await page.selectOption('[data-testid="template-category-select"]', 'PA');
    await page.selectOption('[data-testid="template-personality-select"]', 'professional');
    await page.fill('[data-testid="template-instructions-input"]', 'You are a specialized assistant for RazorFlow operations.');
    
    // Scope & Training section
    await page.selectOption('[data-testid="template-scope-select"]', 'specialized');
    
    // Add training Q&A
    await page.fill('[data-testid="qa-question-0"]', 'What is RazorFlow?');
    await page.fill('[data-testid="qa-answer-0"]', 'RazorFlow is an AI automation platform.');
    
    await page.click('[data-testid="add-qa-btn"]');
    await page.fill('[data-testid="qa-question-1"]', 'How do we handle support tickets?');
    await page.fill('[data-testid="qa-answer-1"]', 'We prioritize tickets based on client tier and urgency.');
    
    // Tools & Integrations section
    await page.check('[data-testid="tool-email-toggle"]');
    await page.fill('[data-testid="tool-email-apikey"]', 'email-api-key-test');
    
    await page.check('[data-testid="tool-calendar-toggle"]');
    await page.fill('[data-testid="tool-calendar-apikey"]', 'calendar-api-key-test');
    
    await page.check('[data-testid="tool-web-search-toggle"]');
    await page.fill('[data-testid="tool-web-search-apikey"]', 'search-api-key-test');
    
    // Tags
    await page.fill('[data-testid="template-tags-input"]', 'razorflow,custom,specialized');
    
    // Submit the template
    await page.click('[data-testid="create-template-submit"]');
    await page.waitForSelector('[data-testid="success-message"]', { timeout: 10000 });
    
    // Verify template appears in list
    await expect(page.locator('text=Custom RazorFlow Assistant')).toBeVisible();
  });

  test('should validate form fields with proper error handling', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Try to submit empty form
    await page.click('[data-testid="create-template-submit"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="description-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="instructions-error"]')).toBeVisible();
    
    // Fill required fields one by one (human-like behavior)
    await page.fill('[data-testid="template-name-input"]', 'Test Template');
    await page.blur('[data-testid="template-name-input"]');
    await expect(page.locator('[data-testid="name-error"]')).not.toBeVisible();
    
    await page.fill('[data-testid="template-description-input"]', 'A test template for validation');
    await page.blur('[data-testid="template-description-input"]');
    await expect(page.locator('[data-testid="description-error"]')).not.toBeVisible();
    
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions for the AI assistant');
    await page.blur('[data-testid="template-instructions-input"]');
    await expect(page.locator('[data-testid="instructions-error"]')).not.toBeVisible();
  });

  test('should test Q&A management functionality', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill basic required fields
    await page.fill('[data-testid="template-name-input"]', 'QA Test Template');
    await page.fill('[data-testid="template-description-input"]', 'Testing Q&A functionality');
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions');
    
    // Test Q&A functionality
    await page.fill('[data-testid="qa-question-0"]', 'First question?');
    await page.fill('[data-testid="qa-answer-0"]', 'First answer');
    
    // Add another Q&A pair
    await page.click('[data-testid="add-qa-btn"]');
    await expect(page.locator('[data-testid="qa-question-1"]')).toBeVisible();
    
    await page.fill('[data-testid="qa-question-1"]', 'Second question?');
    await page.fill('[data-testid="qa-answer-1"]', 'Second answer');
    
    // Add third Q&A pair
    await page.click('[data-testid="add-qa-btn"]');
    await page.fill('[data-testid="qa-question-2"]', 'Third question?');
    await page.fill('[data-testid="qa-answer-2"]', 'Third answer');
    
    // Remove middle Q&A pair
    await page.click('[data-testid="remove-qa-1"]');
    
    // Verify only 2 Q&A pairs remain
    await expect(page.locator('[data-testid="qa-question-0"]')).toBeVisible();
    await expect(page.locator('[data-testid="qa-question-1"]')).toBeVisible();
    await expect(page.locator('[data-testid="qa-question-2"]')).not.toBeVisible();
    
    // Verify the remaining pairs have correct content
    await expect(page.locator('[data-testid="qa-question-0"]')).toHaveValue('First question?');
    await expect(page.locator('[data-testid="qa-question-1"]')).toHaveValue('Third question?');
  });

  test('should test tools configuration functionality', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill basic required fields
    await page.fill('[data-testid="template-name-input"]', 'Tools Test Template');
    await page.fill('[data-testid="template-description-input"]', 'Testing tools configuration');
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions');
    
    // Test various tools
    const tools = [
      { name: 'web-search', hasApiKey: true },
      { name: 'email', hasApiKey: true },
      { name: 'calendar', hasApiKey: true },
      { name: 'file-system', hasApiKey: false },
      { name: 'api-client', hasApiKey: true },
      { name: 'weather', hasApiKey: true }
    ];
    
    for (const tool of tools) {
      // Toggle the tool
      await page.check(`[data-testid="tool-${tool.name}-toggle"]`);
      
      if (tool.hasApiKey) {
        // Verify API key field appears
        await expect(page.locator(`[data-testid="tool-${tool.name}-apikey"]`)).toBeVisible();
        await page.fill(`[data-testid="tool-${tool.name}-apikey"]`, `${tool.name}-api-key-test`);
      }
      
      // Toggle off
      await page.uncheck(`[data-testid="tool-${tool.name}-toggle"]`);
      
      if (tool.hasApiKey) {
        // Verify API key field disappears
        await expect(page.locator(`[data-testid="tool-${tool.name}-apikey"]`)).not.toBeVisible();
      }
      
      // Toggle back on for final state
      await page.check(`[data-testid="tool-${tool.name}-toggle"]`);
    }
  });

  test('should test database tool special configuration', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill basic required fields
    await page.fill('[data-testid="template-name-input"]', 'Database Test Template');
    await page.fill('[data-testid="template-description-input"]', 'Testing database configuration');
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions');
    
    // Test database tool special configuration
    await page.check('[data-testid="tool-database-toggle"]');
    
    // Verify database config fields appear
    await expect(page.locator('[data-testid="tool-database-host"]')).toBeVisible();
    await expect(page.locator('[data-testid="tool-database-port"]')).toBeVisible();
    await expect(page.locator('[data-testid="tool-database-database"]')).toBeVisible();
    
    // Fill database configuration
    await page.fill('[data-testid="tool-database-host"]', 'localhost');
    await page.fill('[data-testid="tool-database-port"]', '5432');
    await page.fill('[data-testid="tool-database-database"]', 'test_db');
    
    // Toggle off and verify fields disappear
    await page.uncheck('[data-testid="tool-database-toggle"]');
    await expect(page.locator('[data-testid="tool-database-host"]')).not.toBeVisible();
  });

  test('should validate scope and training Q&A requirements', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill basic required fields
    await page.fill('[data-testid="template-name-input"]', 'Validation Test Template');
    await page.fill('[data-testid="template-description-input"]', 'Testing validation');
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions');
    
    // Test scope validation
    await page.selectOption('[data-testid="template-scope-select"]', 'expert');
    
    // Leave Q&A empty and try to submit
    await page.click('[data-testid="create-template-submit"]');
    
    // Check for Q&A validation error
    await expect(page.locator('[data-testid="qa-error"]')).toBeVisible();
    
    // Fill incomplete Q&A (only question)
    await page.fill('[data-testid="qa-question-0"]', 'Test question?');
    await page.click('[data-testid="create-template-submit"]');
    
    // Should still show error for incomplete Q&A
    await expect(page.locator('[data-testid="qa-error"]')).toBeVisible();
    
    // Complete the Q&A
    await page.fill('[data-testid="qa-answer-0"]', 'Test answer');
    
    // Now submission should work (assuming other validations pass)
    await page.click('[data-testid="create-template-submit"]');
    await expect(page.locator('[data-testid="qa-error"]')).not.toBeVisible();
  });
});

  test('should open create template modal and display new sections', async ({ page }) => {
    // Click Add Template button
    await page.click('[data-testid="add-template-btn"]');
    
    // Wait for modal to open
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Verify Scope & Training section exists
    await expect(page.locator('text=Scope & Training')).toBeVisible();
    await expect(page.locator('[data-testid="template-scope-select"]')).toBeVisible();
    
    // Verify Tools & Integrations section exists
    await expect(page.locator('text=Tools & Integrations')).toBeVisible();
    await expect(page.locator('[data-testid="tool-web-search-toggle"]')).toBeVisible();
  });

  test('should interact with AI Scope selection', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Test scope selection
    const scopeSelect = page.locator('[data-testid="template-scope-select"]');
    await expect(scopeSelect).toHaveValue('general');
    
    // Change to specialized
    await scopeSelect.selectOption('specialized');
    await expect(scopeSelect).toHaveValue('specialized');
    
    // Change to expert
    await scopeSelect.selectOption('expert');
    await expect(scopeSelect).toHaveValue('expert');
    
    // Change to domain-specific
    await scopeSelect.selectOption('domain-specific');
    await expect(scopeSelect).toHaveValue('domain-specific');
  });

  test('should manage Q&A training pairs', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Verify initial Q&A pair exists
    await expect(page.locator('[data-testid="training-question-0"]')).toBeVisible();
    await expect(page.locator('[data-testid="training-answer-0"]')).toBeVisible();
    
    // Fill in first Q&A pair
    await page.fill('[data-testid="training-question-0"]', 'What is your primary function?');
    await page.fill('[data-testid="training-answer-0"]', 'I am an AI assistant designed to help with various tasks.');
    
    // Add another Q&A pair
    await page.click('text=Add Q&A Pair');
    
    // Verify second pair exists
    await expect(page.locator('[data-testid="training-question-1"]')).toBeVisible();
    await expect(page.locator('[data-testid="training-answer-1"]')).toBeVisible();
    
    // Fill in second Q&A pair
    await page.fill('[data-testid="training-question-1"]', 'How can you help me?');
    await page.fill('[data-testid="training-answer-1"]', 'I can assist with information, analysis, and task completion.');
    
    // Add third Q&A pair
    await page.click('text=Add Q&A Pair');
    await expect(page.locator('[data-testid="training-question-2"]')).toBeVisible();
    
    // Now remove the second pair (middle one)
    const deleteButtons = page.locator('button[variant="outline-danger"]');
    await deleteButtons.nth(0).click(); // Delete second pair (index 1, but first delete button)
    
    // Verify only 2 pairs remain
    await expect(page.locator('[data-testid="training-question-0"]')).toBeVisible();
    await expect(page.locator('[data-testid="training-question-1"]')).toBeVisible();
    await expect(page.locator('[data-testid="training-question-2"]')).not.toBeVisible();
  });

  test('should toggle and configure tools', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Test Web Search tool
    const webSearchToggle = page.locator('[data-testid="tool-web-search-toggle"]');
    await expect(webSearchToggle).not.toBeChecked();
    
    // Toggle on web search
    await webSearchToggle.click();
    await expect(webSearchToggle).toBeChecked();
    
    // API key field should appear
    await expect(page.locator('[data-testid="tool-web-search-api-key"]')).toBeVisible();
    await page.fill('[data-testid="tool-web-search-api-key"]', 'test-search-api-key');
    
    // Test Email tool
    const emailToggle = page.locator('[data-testid="tool-email-toggle"]');
    await emailToggle.click();
    await expect(emailToggle).toBeChecked();
    await page.fill('[data-testid="tool-email-api-key"]', 'test-email-key');
    
    // Test Database tool (more complex configuration)
    const databaseToggle = page.locator('[data-testid="tool-database-toggle"]');
    await databaseToggle.click();
    await expect(databaseToggle).toBeChecked();
    
    // Fill database configuration
    await page.fill('[data-testid="tool-database-host"]', 'localhost');
    await page.fill('[data-testid="tool-database-port"]', '5432');
    await page.fill('[data-testid="tool-database-name"]', 'testdb');
    
    // Toggle off web search and verify API key field disappears
    await webSearchToggle.click();
    await expect(webSearchToggle).not.toBeChecked();
    await expect(page.locator('[data-testid="tool-web-search-api-key"]')).not.toBeVisible();
  });

  test('should create complete template with advanced features', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill basic template information
    await page.fill('[data-testid="template-name-input"]', 'Advanced AI Assistant');
    await page.fill('[data-testid="template-description-input"]', 'A comprehensive AI assistant with multiple tools and training data for enhanced capabilities.');
    
    // Select category
    await page.selectOption('[data-testid="template-category-select"]', 'technical');
    
    // Fill instructions
    await page.fill('[data-testid="template-instructions-input"]', 'You are an advanced AI assistant with access to multiple tools and specialized training. Use your tools appropriately and refer to your training data for specific responses.');
    
    // Add tags
    await page.fill('[data-testid="template-tags-input"]', 'advanced, ai, tools, training, technical');
    
    // Configure scope
    await page.selectOption('[data-testid="template-scope-select"]', 'expert');
    
    // Add training Q&A
    await page.fill('[data-testid="training-question-0"]', 'What tools do you have access to?');
    await page.fill('[data-testid="training-answer-0"]', 'I have access to web search, email, calendar, database, and various other tools to assist you.');
    
    // Add second Q&A pair
    await page.click('text=Add Q&A Pair');
    await page.fill('[data-testid="training-question-1"]', 'How do you handle technical questions?');
    await page.fill('[data-testid="training-answer-1"]', 'I analyze technical questions carefully and use appropriate tools and my specialized training to provide accurate, detailed responses.');
    
    // Enable tools
    await page.click('[data-testid="tool-web-search-toggle"]');
    await page.fill('[data-testid="tool-web-search-api-key"]', 'search-api-key-123');
    
    await page.click('[data-testid="tool-database-toggle"]');
    await page.fill('[data-testid="tool-database-host"]', 'db.example.com');
    await page.fill('[data-testid="tool-database-port"]', '5432');
    await page.fill('[data-testid="tool-database-name"]', 'production_db');
    
    await page.click('[data-testid="tool-weather-toggle"]');
    await page.fill('[data-testid="tool-weather-api-key"]', 'weather-key-456');
    
    // Make template public
    await page.click('[data-testid="template-public-checkbox"]');
    
    // Submit the template
    await page.click('[data-testid="submit-template-btn"]');
    
    // Wait for success message
    await expect(page.locator('text=Template "Advanced AI Assistant" created successfully!')).toBeVisible();
    
    // Verify modal closed
    await expect(page.locator('[data-testid="create-template-modal"]')).not.toBeVisible();
    
    // Verify template appears in list
    await expect(page.locator('text=Advanced AI Assistant')).toBeVisible();
  });

  test('should validate Q&A pairs properly', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Fill required fields first
    await page.fill('[data-testid="template-name-input"]', 'Test Template');
    await page.fill('[data-testid="template-description-input"]', 'Test description for validation');
    await page.fill('[data-testid="template-instructions-input"]', 'Test instructions for the template');
    await page.fill('[data-testid="template-tags-input"]', 'test, validation');
    
    // Add incomplete Q&A pair (question only)
    await page.fill('[data-testid="training-question-0"]', 'Test question without answer');
    // Leave answer empty
    
    // Try to submit
    await page.click('[data-testid="submit-template-btn"]');
    
    // Should show validation error
    await expect(page.locator('text=Please fix the errors below before submitting')).toBeVisible();
    
    // Complete the Q&A pair
    await page.fill('[data-testid="training-answer-0"]', 'Test answer for the question');
    
    // Now submission should work
    await page.click('[data-testid="submit-template-btn"]');
    await expect(page.locator('text=Template "Test Template" created successfully!')).toBeVisible();
  });

  test('should test all tool switches', async ({ page }) => {
    await page.click('[data-testid="add-template-btn"]');
    await page.waitForSelector('[data-testid="create-template-modal"]');
    
    // Test all tool toggles
    const tools = [
      'web-search', 'email', 'calendar', 'file-system', 
      'database', 'api-client', 'weather', 'maps', 
      'translation', 'image-analysis'
    ];
    
    for (const tool of tools) {
      const toggle = page.locator(`[data-testid="tool-${tool}-toggle"]`);
      await expect(toggle).not.toBeChecked();
      await toggle.click();
      await expect(toggle).toBeChecked();
      
      // Special handling for file-system (no API key)
      if (tool !== 'file-system') {
        if (tool === 'database') {
          // Database has complex config
          await expect(page.locator(`[data-testid="tool-${tool}-host"]`)).toBeVisible();
        } else {
          // Most tools have API key field
          const apiKeyField = page.locator(`[data-testid="tool-${tool}-api-key"], [data-testid="tool-${tool}-key"]`);
          await expect(apiKeyField).toBeVisible();
        }
      }
    }
  });
});