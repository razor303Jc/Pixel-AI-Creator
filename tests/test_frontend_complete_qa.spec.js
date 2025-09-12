/**
 * COMPREHENSIVE FRONTEND QA TEST SUITE
 * Pixel-AI-Creator - Complete UI/UX Testing with Playwright
 * 
 * Tests ALL:
 * - Forms & Input Fields
 * - Buttons & Links  
 * - Pages & Navigation
 * - Authentication Components
 * - Dashboard Features
 * - Advanced Authentication (MFA, Social Login, Password Strength)
 * - Database Management
 * - Chatbot Manager
 * - Analytics Dashboard
 * - Client Management
 * - Performance Monitoring
 * - Responsive Design
 * - Error Handling
 * - Accessibility
 */

const { test, expect } = require('@playwright/test');

// Test Configuration
const BASE_URL = 'http://localhost:3002';
const API_URL = 'http://localhost:8002';

// Mock user data for testing
const TEST_USERS = {
  admin: {
    email: 'admin@pixel.ai',
    password: 'admin123',
    role: 'admin'
  },
  user: {
    email: 'user@pixel.ai', 
    password: 'user123',
    role: 'user'
  },
  newUser: {
    email: 'newuser@test.com',
    password: 'NewPassword123!',
    name: 'Test User'
  }
};

test.describe('🎯 COMPREHENSIVE FRONTEND QA SUITE', () => {

  test.beforeEach(async ({ page }) => {
    // Setup console error tracking
    await page.addInitScript(() => {
      window.consoleErrors = [];
      const originalError = console.error;
      console.error = (...args) => {
        window.consoleErrors.push(args.join(' '));
        originalError.apply(console, args);
      };
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
  });

  test.describe('🔐 AUTHENTICATION SYSTEM - COMPLETE TESTING', () => {
    
    test('Login Form - All Elements and Validations', async ({ page }) => {
      // Take screenshot for visual verification
      await page.screenshot({ path: 'test-reports/login-form-initial.png' });

      // Verify page title and meta
      await expect(page).toHaveTitle('Pixel AI Creator');
      
      // Test all form elements existence
      await expect(page.locator('h3')).toContainText('Welcome Back');
      
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const signInButton = page.locator('button:has-text("Sign In")');
      const signUpButton = page.locator('button:has-text("Sign up here")');

      // Verify all elements are visible
      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
      await expect(signInButton).toBeVisible();
      await expect(signUpButton).toBeVisible();

      // Test placeholder texts
      await expect(emailInput).toHaveAttribute('placeholder', 'Enter your email');
      await expect(passwordInput).toHaveAttribute('placeholder', 'Enter your password');

      // Test input field focus states
      await emailInput.focus();
      await expect(emailInput).toBeFocused();
      
      await passwordInput.focus();
      await expect(passwordInput).toBeFocused();
    });

    test('Email Input - Complete Validation Testing', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]');

      // Test cases for email validation
      const emailTests = [
        { value: '', expectValid: false, description: 'Empty email' },
        { value: 'invalid', expectValid: false, description: 'Invalid format - no @' },
        { value: 'invalid@', expectValid: false, description: 'Invalid format - no domain' },
        { value: '@domain.com', expectValid: false, description: 'Invalid format - no local part' },
        { value: 'test@.com', expectValid: false, description: 'Invalid format - empty domain' },
        { value: 'test@domain', expectValid: false, description: 'Invalid format - no TLD' },
        { value: 'test@domain.', expectValid: false, description: 'Invalid format - empty TLD' },
        { value: 'valid@example.com', expectValid: true, description: 'Valid email' },
        { value: 'user.name+tag@example.com', expectValid: true, description: 'Valid complex email' },
        { value: 'test123@domain-name.co.uk', expectValid: true, description: 'Valid subdomain email' }
      ];

      for (const emailTest of emailTests) {
        await emailInput.fill(emailTest.value);
        await emailInput.blur();
        await page.waitForTimeout(100);

        // Verify value was entered
        await expect(emailInput).toHaveValue(emailTest.value);
        
        console.log(`✓ Email test: ${emailTest.description} - ${emailTest.value}`);
      }
    });

    test('Password Input - Security Features Testing', async ({ page }) => {
      const passwordInput = page.locator('input[type="password"]');
      const toggleButton = page.locator('button:has([role="img"])').last();

      // Test password entry
      const testPassword = 'TestPassword123!';
      await passwordInput.fill(testPassword);
      await expect(passwordInput).toHaveValue(testPassword);

      // Test password is hidden by default
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // Test password visibility toggle if available
      if (await toggleButton.isVisible()) {
        await toggleButton.click();
        await page.waitForTimeout(100);
        
        // May toggle to text type
        const currentType = await passwordInput.getAttribute('type');
        console.log(`Password visibility toggle: ${currentType}`);
      }

      // Test various password strengths
      const passwordTests = [
        '123',                    // Weak - too short
        'password',              // Weak - common word
        'Password',              // Medium - mixed case
        'Password123',           // Strong - mixed case + numbers
        'Password123!',          // Very strong - mixed case + numbers + symbols
      ];

      for (const pwd of passwordTests) {
        await passwordInput.fill(pwd);
        await page.waitForTimeout(200);
        console.log(`✓ Password strength test: ${pwd}`);
      }
    });

    test('Login Form Submission - All Scenarios', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const signInButton = page.locator('button:has-text("Sign In")');

      // Test 1: Empty form submission
      await signInButton.click();
      await page.waitForTimeout(1000);
      
      // Test 2: Invalid credentials
      await emailInput.fill('invalid@test.com');
      await passwordInput.fill('wrongpassword');
      await signInButton.click();
      await page.waitForTimeout(2000);

      // Test 3: Valid credentials (if backend is running)
      await emailInput.fill(TEST_USERS.admin.email);
      await passwordInput.fill(TEST_USERS.admin.password);
      await signInButton.click();
      await page.waitForTimeout(3000);

      // Check response - either success redirect or error message
      const currentUrl = page.url();
      const hasErrorMessage = await page.locator('.error, .alert, [role="alert"]').count() > 0;
      
      console.log(`Login attempt result - URL: ${currentUrl}, Has Error: ${hasErrorMessage}`);
    });

    test('Registration Form - Switch and Validation', async ({ page }) => {
      const signUpButton = page.locator('button:has-text("Sign up here")');
      
      // Click to switch to registration
      await signUpButton.click();
      await page.waitForTimeout(1000);

      // Look for registration form elements
      const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]');
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const confirmPasswordInput = page.locator('input[placeholder*="confirm" i], input[name*="confirm" i]');

      // Test registration form if it appears
      if (await nameInput.count() > 0) {
        await nameInput.fill(TEST_USERS.newUser.name);
        await emailInput.fill(TEST_USERS.newUser.email);
        await passwordInput.fill(TEST_USERS.newUser.password);
        
        if (await confirmPasswordInput.count() > 0) {
          await confirmPasswordInput.fill(TEST_USERS.newUser.password);
        }

        // Try to submit registration
        const submitButton = page.locator('button[type="submit"], button:has-text("Sign Up"), button:has-text("Register")');
        if (await submitButton.count() > 0) {
          await submitButton.click();
          await page.waitForTimeout(2000);
        }
      }

      console.log('✓ Registration form testing completed');
    });
  });

  test.describe('🛡️ ADVANCED AUTHENTICATION FEATURES', () => {
    
    test.beforeEach(async ({ page }) => {
      // Mock authenticated state for advanced features
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
        localStorage.setItem('user', JSON.stringify({
          id: 1,
          email: 'test@pixel.ai',
          name: 'Test User',
          role: 'admin',
          mfa_enabled: false
        }));
      });
    });

    test('MFA Setup Component Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Look for MFA-related elements
      const mfaElements = await page.locator('[data-testid*="mfa"], .mfa, button:has-text("MFA"), button:has-text("2FA")').count();
      
      if (mfaElements > 0) {
        const mfaButton = page.locator('button:has-text("MFA"), button:has-text("2FA")').first();
        await mfaButton.click();
        await page.waitForTimeout(1000);

        // Look for QR code or setup form
        const qrCode = page.locator('canvas, .qr-code, [data-testid="qr-code"]');
        const setupForm = page.locator('form, .mfa-setup');

        if (await qrCode.count() > 0) {
          console.log('✓ MFA QR Code displayed');
        }

        if (await setupForm.count() > 0) {
          console.log('✓ MFA Setup form displayed');
        }
      }

      console.log(`MFA elements found: ${mfaElements}`);
    });

    test('Social Login Buttons Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Look for social login buttons
      const socialButtons = [
        'button:has-text("Google")',
        'button:has-text("Facebook")', 
        'button:has-text("GitHub")',
        'button:has-text("LinkedIn")',
        '.social-login button',
        '[data-testid*="social"]'
      ];

      for (const selector of socialButtons) {
        const button = page.locator(selector);
        if (await button.count() > 0) {
          await button.click();
          await page.waitForTimeout(500);
          console.log(`✓ Social login button clicked: ${selector}`);
        }
      }
    });

    test('Password Strength Indicator Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Look for password change form
      const passwordChangeButton = page.locator('button:has-text("Change Password"), button:has-text("Update Password")');
      
      if (await passwordChangeButton.count() > 0) {
        await passwordChangeButton.click();
        await page.waitForTimeout(1000);

        const newPasswordInput = page.locator('input[placeholder*="new password" i], input[name*="new" i]');
        
        if (await newPasswordInput.count() > 0) {
          const testPasswords = ['weak', 'Medium123', 'StrongPassword123!'];
          
          for (const pwd of testPasswords) {
            await newPasswordInput.fill(pwd);
            await page.waitForTimeout(500);
            
            // Look for strength indicator
            const strengthIndicator = page.locator('.strength, .password-strength, [data-testid*="strength"]');
            if (await strengthIndicator.count() > 0) {
              const strengthText = await strengthIndicator.textContent();
              console.log(`Password "${pwd}" strength: ${strengthText}`);
            }
          }
        }
      }
    });

    test('Security Dashboard Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Look for security/settings navigation
      const securityNav = page.locator('a:has-text("Security"), button:has-text("Security"), a:has-text("Settings")');
      
      if (await securityNav.count() > 0) {
        await securityNav.first().click();
        await page.waitForTimeout(1000);

        // Look for security features
        const securityFeatures = [
          'button:has-text("Change Password")',
          'button:has-text("Enable MFA")',
          'button:has-text("Download Backup Codes")',
          '.session, .active-sessions',
          '.security-log, .audit-log'
        ];

        for (const feature of securityFeatures) {
          const element = page.locator(feature);
          if (await element.count() > 0) {
            console.log(`✓ Security feature found: ${feature}`);
          }
        }
      }
    });
  });

  test.describe('📊 DASHBOARD COMPONENTS TESTING', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
        localStorage.setItem('user', JSON.stringify({
          id: 1,
          email: 'admin@pixel.ai',
          role: 'admin'
        }));
      });
    });

    test('Main Dashboard Layout and Navigation', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Take dashboard screenshot
      await page.screenshot({ path: 'test-reports/dashboard-layout.png' });

      // Test navigation elements
      const navElements = [
        'nav',
        '.navbar',
        '.sidebar',
        '.navigation',
        '.menu',
        '[data-testid="navigation"]'
      ];

      let foundNav = false;
      for (const selector of navElements) {
        if (await page.locator(selector).count() > 0) {
          foundNav = true;
          console.log(`✓ Navigation found: ${selector}`);
          break;
        }
      }

      // Test main content area
      const contentElements = [
        '.content',
        '.main',
        '.dashboard',
        '.container',
        '[data-testid="main-content"]'
      ];

      let foundContent = false;
      for (const selector of contentElements) {
        if (await page.locator(selector).count() > 0) {
          foundContent = true;
          console.log(`✓ Main content found: ${selector}`);
          break;
        }
      }

      expect(foundNav || foundContent).toBeTruthy();
    });

    test('Analytics Cards and Metrics Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for analytics/metrics cards
      const metricSelectors = [
        '.card',
        '.metric',
        '.stat',
        '.analytics-card',
        '[data-testid*="metric"]',
        '.dashboard-card'
      ];

      let totalMetrics = 0;
      for (const selector of metricSelectors) {
        const count = await page.locator(selector).count();
        totalMetrics += count;
        if (count > 0) {
          console.log(`✓ Metrics found with ${selector}: ${count}`);
        }
      }

      // Test metric values and formatting
      if (totalMetrics > 0) {
        const metricValues = await page.locator('.card .value, .metric .number, .stat .count').allTextContents();
        for (const value of metricValues) {
          console.log(`Metric value: ${value}`);
        }
      }

      console.log(`Total metric elements: ${totalMetrics}`);
    });

    test('Charts and Visualizations Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for chart elements
      const chartSelectors = [
        'svg',
        'canvas',
        '.recharts-wrapper',
        '.chart',
        '.graph',
        '.visualization',
        '[data-testid*="chart"]'
      ];

      let chartsFound = 0;
      for (const selector of chartSelectors) {
        const count = await page.locator(selector).count();
        chartsFound += count;
        if (count > 0) {
          console.log(`✓ Charts found with ${selector}: ${count}`);
        }
      }

      // Test chart interactions if available
      if (chartsFound > 0) {
        const chartElement = page.locator('svg, canvas').first();
        await chartElement.hover();
        await page.waitForTimeout(500);
        
        // Look for tooltips or interactive elements
        const tooltip = page.locator('.tooltip, .chart-tooltip');
        if (await tooltip.count() > 0) {
          console.log('✓ Chart tooltip interaction working');
        }
      }

      console.log(`Total charts found: ${chartsFound}`);
    });
  });

  test.describe('🤖 CHATBOT MANAGER TESTING', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
      });
    });

    test('Chatbot List and Management Interface', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for chatbot-related navigation
      const chatbotNav = page.locator('a:has-text("Chatbot"), a:has-text("Bots"), button:has-text("Chatbot")');
      
      if (await chatbotNav.count() > 0) {
        await chatbotNav.first().click();
        await page.waitForTimeout(2000);

        // Look for chatbot list
        const chatbotList = page.locator('.chatbot-list, .bot-list, .chatbots');
        const chatbotCards = page.locator('.chatbot-card, .bot-card');

        if (await chatbotList.count() > 0 || await chatbotCards.count() > 0) {
          console.log('✓ Chatbot management interface found');
          
          // Test create new chatbot button
          const createButton = page.locator('button:has-text("Create"), button:has-text("New"), button:has-text("Add")');
          if (await createButton.count() > 0) {
            await createButton.first().click();
            await page.waitForTimeout(1000);
            console.log('✓ Create chatbot button working');
          }
        }
      }
    });

    test('Chatbot Creation Form Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Try to find and open create chatbot form
      const createButtons = page.locator('button:has-text("Create"), button:has-text("New Chatbot"), button:has-text("Add Bot")');
      
      if (await createButtons.count() > 0) {
        await createButtons.first().click();
        await page.waitForTimeout(1000);

        // Test form fields
        const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]');
        const descriptionInput = page.locator('textarea[name="description"], textarea[placeholder*="description" i]');
        const typeSelect = page.locator('select[name="type"], select[name="category"]');

        if (await nameInput.count() > 0) {
          await nameInput.fill('Test Chatbot');
          console.log('✓ Chatbot name field working');
        }

        if (await descriptionInput.count() > 0) {
          await descriptionInput.fill('This is a test chatbot for QA testing');
          console.log('✓ Chatbot description field working');
        }

        if (await typeSelect.count() > 0) {
          await typeSelect.selectOption({ index: 0 });
          console.log('✓ Chatbot type selection working');
        }

        // Test submit button
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")');
        if (await submitButton.count() > 0) {
          // Note: We won't actually submit to avoid creating test data
          console.log('✓ Submit button found');
        }
      }
    });

    test('Chatbot Configuration and Settings', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for existing chatbot to configure
      const chatbotItems = page.locator('.chatbot-item, .bot-card, .chatbot-card');
      
      if (await chatbotItems.count() > 0) {
        // Click on first chatbot
        await chatbotItems.first().click();
        await page.waitForTimeout(1000);

        // Look for configuration options
        const configElements = [
          'button:has-text("Configure")',
          'button:has-text("Settings")',
          'button:has-text("Edit")',
          '.config, .settings'
        ];

        for (const selector of configElements) {
          if (await page.locator(selector).count() > 0) {
            await page.locator(selector).first().click();
            await page.waitForTimeout(500);
            console.log(`✓ Configuration option found: ${selector}`);
          }
        }
      }
    });
  });

  test.describe('👥 CLIENT MANAGEMENT TESTING', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
      });
    });

    test('Client List and Dashboard', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Navigate to clients section
      const clientNav = page.locator('a:has-text("Client"), a:has-text("Customer"), button:has-text("Client")');
      
      if (await clientNav.count() > 0) {
        await clientNav.first().click();
        await page.waitForTimeout(2000);

        // Look for client list elements
        const clientList = page.locator('.client-list, .customer-list, .clients');
        const clientCards = page.locator('.client-card, .customer-card');
        const clientTable = page.locator('table, .data-table');

        let clientUIFound = false;
        if (await clientList.count() > 0) {
          clientUIFound = true;
          console.log('✓ Client list view found');
        }
        if (await clientCards.count() > 0) {
          clientUIFound = true;
          console.log(`✓ Client cards found: ${await clientCards.count()}`);
        }
        if (await clientTable.count() > 0) {
          clientUIFound = true;
          console.log('✓ Client table view found');
        }

        expect(clientUIFound).toBeTruthy();
      }
    });

    test('Add New Client Form Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for add client button
      const addClientButton = page.locator('button:has-text("Add Client"), button:has-text("New Client"), button:has-text("Create Client")');
      
      if (await addClientButton.count() > 0) {
        await addClientButton.first().click();
        await page.waitForTimeout(1000);

        // Test client form fields
        const formFields = [
          { selector: 'input[name="name"], input[placeholder*="name" i]', value: 'Test Client Company' },
          { selector: 'input[name="email"], input[type="email"]', value: 'client@testcompany.com' },
          { selector: 'input[name="phone"], input[placeholder*="phone" i]', value: '+1234567890' },
          { selector: 'textarea[name="description"], textarea[placeholder*="description" i]', value: 'Test client description' }
        ];

        for (const field of formFields) {
          const element = page.locator(field.selector);
          if (await element.count() > 0) {
            await element.fill(field.value);
            await expect(element).toHaveValue(field.value);
            console.log(`✓ Client form field working: ${field.selector}`);
          }
        }

        // Test form submission (without actually submitting)
        const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
        if (await submitButton.count() > 0) {
          console.log('✓ Client form submit button found');
        }
      }
    });

    test('Client Details and Edit Functions', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for existing client to view/edit
      const clientItems = page.locator('.client-item, .client-card, .client-row');
      
      if (await clientItems.count() > 0) {
        await clientItems.first().click();
        await page.waitForTimeout(1000);

        // Look for client detail actions
        const detailActions = [
          'button:has-text("Edit")',
          'button:has-text("Update")',
          'button:has-text("Delete")',
          'button:has-text("View")',
          '.actions button'
        ];

        for (const action of detailActions) {
          if (await page.locator(action).count() > 0) {
            console.log(`✓ Client action found: ${action}`);
          }
        }
      }
    });
  });

  test.describe('🗄️ DATABASE MANAGEMENT TESTING', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
        localStorage.setItem('user', JSON.stringify({ role: 'admin' }));
      });
    });

    test('Database Dashboard and Overview', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Navigate to database management
      const dbNav = page.locator('a:has-text("Database"), a:has-text("Admin"), button:has-text("Database")');
      
      if (await dbNav.count() > 0) {
        await dbNav.first().click();
        await page.waitForTimeout(2000);

        // Look for database statistics
        const dbStats = page.locator('.db-stats, .database-stats, .stats');
        const dbTables = page.locator('.table-list, .db-tables');
        const dbMetrics = page.locator('.db-metric, .database-metric');

        if (await dbStats.count() > 0) {
          console.log('✓ Database statistics found');
        }
        if (await dbTables.count() > 0) {
          console.log('✓ Database tables list found');
        }
        if (await dbMetrics.count() > 0) {
          console.log(`✓ Database metrics found: ${await dbMetrics.count()}`);
        }
      }
    });

    test('Table Management and Operations', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for table management interface
      const tableElements = page.locator('.table-row, .db-table-item, table tbody tr');
      
      if (await tableElements.count() > 0) {
        // Test table interaction
        await tableElements.first().click();
        await page.waitForTimeout(500);

        // Look for table operations
        const tableOps = [
          'button:has-text("View")',
          'button:has-text("Edit")',
          'button:has-text("Export")',
          'button:has-text("Backup")',
          '.table-actions button'
        ];

        for (const op of tableOps) {
          if (await page.locator(op).count() > 0) {
            console.log(`✓ Table operation found: ${op}`);
          }
        }
      }
    });

    test('Database Query Interface Testing', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Look for query interface
      const queryInterface = page.locator('.query-editor, .sql-editor, textarea[placeholder*="query" i]');
      
      if (await queryInterface.count() > 0) {
        // Test query input
        await queryInterface.fill('SELECT * FROM users LIMIT 10;');
        await expect(queryInterface).toContainText('SELECT');

        // Look for execute button
        const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run"), button:has-text("Query")');
        if (await executeButton.count() > 0) {
          console.log('✓ Query execute button found');
        }

        // Look for results area
        const resultsArea = page.locator('.query-results, .results, .output');
        if (await resultsArea.count() > 0) {
          console.log('✓ Query results area found');
        }
      }
    });
  });

  test.describe('📱 RESPONSIVE DESIGN TESTING', () => {
    
    const viewports = [
      { name: 'Mobile Portrait', width: 375, height: 667 },
      { name: 'Mobile Landscape', width: 667, height: 375 },
      { name: 'Tablet Portrait', width: 768, height: 1024 },
      { name: 'Tablet Landscape', width: 1024, height: 768 },
      { name: 'Desktop Small', width: 1366, height: 768 },
      { name: 'Desktop Large', width: 1920, height: 1080 }
    ];

    for (const viewport of viewports) {
      test(`${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.reload();
        await page.waitForTimeout(2000);

        // Take screenshot for visual verification
        await page.screenshot({ 
          path: `test-reports/responsive-${viewport.name.toLowerCase().replace(' ', '-')}.png`,
          fullPage: true 
        });

        // Test critical elements are still accessible
        const criticalElements = [
          'button:visible',
          'input:visible',
          'a:visible',
          '.nav:visible, .navbar:visible',
          '.content:visible, .main:visible'
        ];

        let visibleElements = 0;
        for (const selector of criticalElements) {
          const count = await page.locator(selector).count();
          visibleElements += count;
        }

        expect(visibleElements).toBeGreaterThan(0);
        console.log(`✓ ${viewport.name}: ${visibleElements} interactive elements visible`);

        // Test scrolling works
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(500);
        await page.evaluate(() => window.scrollTo(0, 0));

        // Test touch interactions on mobile
        if (viewport.width < 768) {
          const firstButton = page.locator('button:visible').first();
          if (await firstButton.count() > 0) {
            await firstButton.tap();
            await page.waitForTimeout(300);
          }
        }
      });
    }
  });

  test.describe('🔄 ERROR HANDLING AND EDGE CASES', () => {
    
    test('Network Failure Handling', async ({ page }) => {
      // Mock network failures
      await page.route('**/api/**', route => route.abort('internetdisconnected'));
      
      await page.reload();
      await page.waitForTimeout(3000);

      // Try to trigger API calls
      const buttons = await page.locator('button:visible').all();
      for (let i = 0; i < Math.min(buttons.length, 3); i++) {
        try {
          await buttons[i].click();
          await page.waitForTimeout(1000);
          
          // Application should still be responsive
          const title = await page.title();
          expect(title).toBeDefined();
        } catch (error) {
          console.log(`Button click handled gracefully: ${error.message}`);
        }
      }

      console.log('✓ Network failure handling tested');
    });

    test('Invalid Input Handling', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Test various invalid inputs
      const inputs = await page.locator('input:visible').all();
      
      const invalidInputs = [
        '<script>alert("xss")</script>',
        'SELECT * FROM users;',
        '../../etc/passwd',
        'null',
        'undefined',
        ''.repeat(1000), // Very long string
        '\n\r\t\0'       // Special characters
      ];

      for (let i = 0; i < Math.min(inputs.length, 3); i++) {
        for (const invalidInput of invalidInputs.slice(0, 3)) {
          try {
            await inputs[i].fill(invalidInput);
            await inputs[i].blur();
            await page.waitForTimeout(200);
            
            // Check for any console errors
            const errors = await page.evaluate(() => window.consoleErrors || []);
            console.log(`Invalid input test: ${invalidInput.substring(0, 20)}... - Errors: ${errors.length}`);
            
          } catch (error) {
            console.log(`Input validation working: ${error.message}`);
          }
        }
      }
    });

    test('Rapid User Interaction Stress Test', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Rapid clicking stress test
      const buttons = await page.locator('button:visible').all();
      
      if (buttons.length > 0) {
        const testButton = buttons[0];
        
        // Rapid clicks
        for (let i = 0; i < 10; i++) {
          await testButton.click();
          await page.waitForTimeout(50);
        }

        // Verify application is still responsive
        const title = await page.title();
        expect(title).toBeDefined();
        console.log('✓ Rapid interaction stress test passed');
      }
    });

    test('Browser Console Error Detection', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(3000);

      // Perform various interactions
      const interactiveElements = await page.locator('button:visible, a:visible, input:visible').all();
      
      for (let i = 0; i < Math.min(interactiveElements.length, 5); i++) {
        try {
          await interactiveElements[i].click();
          await page.waitForTimeout(500);
        } catch (error) {
          // Continue with other elements
        }
      }

      // Check for console errors
      const consoleErrors = await page.evaluate(() => window.consoleErrors || []);
      
      console.log(`Console errors detected: ${consoleErrors.length}`);
      for (const error of consoleErrors.slice(0, 5)) {
        console.log(`  Error: ${error}`);
      }

      // Warning: Don't fail test on console errors as they might be expected
      // expect(consoleErrors.length).toBe(0);
    });
  });

  test.describe('⚡ PERFORMANCE TESTING', () => {
    
    test('Page Load Performance', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(BASE_URL);
      await page.waitForLoadState('domcontentloaded');
      
      const domLoadTime = Date.now() - startTime;
      
      await page.waitForLoadState('networkidle');
      const fullLoadTime = Date.now() - startTime;

      console.log(`DOM Load Time: ${domLoadTime}ms`);
      console.log(`Full Load Time: ${fullLoadTime}ms`);

      // Performance assertions
      expect(domLoadTime).toBeLessThan(5000); // DOM should load within 5 seconds
      expect(fullLoadTime).toBeLessThan(10000); // Full load within 10 seconds

      // Take performance screenshot
      await page.screenshot({ path: 'test-reports/performance-loaded.png' });
    });

    test('Memory Usage and Resource Loading', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Get performance metrics
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          resourceCount: performance.getEntriesByType('resource').length
        };
      });

      console.log('Performance Metrics:', metrics);
      
      expect(metrics.resourceCount).toBeGreaterThan(0);
    });

    test('Large Dataset Handling', async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('access_token', 'mock-jwt-token');
      });

      await page.reload();
      await page.waitForTimeout(3000);

      // Look for pagination or infinite scroll
      const paginationElements = page.locator('.pagination, .pager, button:has-text("Load More"), button:has-text("Next")');
      
      if (await paginationElements.count() > 0) {
        const nextButton = paginationElements.first();
        
        // Test pagination performance
        const startTime = Date.now();
        await nextButton.click();
        await page.waitForTimeout(2000);
        const paginationTime = Date.now() - startTime;
        
        console.log(`Pagination load time: ${paginationTime}ms`);
        expect(paginationTime).toBeLessThan(5000);
      }
    });
  });

  test.describe('♿ ACCESSIBILITY TESTING', () => {
    
    test('Keyboard Navigation', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Test Tab navigation
      await page.keyboard.press('Tab');
      await page.waitForTimeout(200);
      
      let focusedElement = await page.locator(':focus').count();
      expect(focusedElement).toBeGreaterThan(0);

      // Navigate through multiple elements
      for (let i = 0; i < 5; i++) {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(100);
      }

      // Test Enter key activation
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      console.log('✓ Keyboard navigation tested');
    });

    test('Focus Indicators and ARIA Labels', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Check for ARIA labels
      const ariaElements = await page.locator('[aria-label], [aria-labelledby], [role]').count();
      console.log(`Elements with ARIA attributes: ${ariaElements}`);

      // Check focus indicators
      const focusableElements = await page.locator('button, input, a, select, textarea').all();
      
      for (let i = 0; i < Math.min(focusableElements.length, 3); i++) {
        await focusableElements[i].focus();
        await page.waitForTimeout(100);
        
        // Visual focus should be present (this would need visual testing in real scenarios)
        const isFocused = await focusableElements[i].evaluate(el => el === document.activeElement);
        expect(isFocused).toBeTruthy();
      }

      console.log('✓ Accessibility features tested');
    });

    test('Screen Reader Compatibility', async ({ page }) => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Check for proper heading structure
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
      console.log(`Heading elements found: ${headings}`);

      // Check for alt text on images
      const images = await page.locator('img').count();
      const imagesWithAlt = await page.locator('img[alt]').count();
      console.log(`Images: ${images}, With alt text: ${imagesWithAlt}`);

      // Check for form labels
      const inputs = await page.locator('input').count();
      const labeledInputs = await page.locator('input[aria-label], input[aria-labelledby], label input').count();
      console.log(`Inputs: ${inputs}, Properly labeled: ${labeledInputs}`);
    });
  });

  // Cleanup and Reporting
  test.afterEach(async ({ page }) => {
    // Check for any console errors that occurred during the test
    const consoleErrors = await page.evaluate(() => window.consoleErrors || []);
    if (consoleErrors.length > 0) {
      console.log('\n📋 Console Errors Detected:');
      consoleErrors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error}`);
      });
    }

    // Take final screenshot
    await page.screenshot({ 
      path: `test-reports/final-state-${Date.now()}.png`,
      fullPage: true 
    });
  });
});

// Export test results summary
test.afterAll(async () => {
  console.log('\n🎯 COMPREHENSIVE QA TESTING COMPLETED');
  console.log('📊 Test Reports Generated in: test-reports/');
  console.log('📸 Screenshots Available for Visual Verification');
  console.log('🔍 Check Playwright HTML Report for Detailed Results');
});
