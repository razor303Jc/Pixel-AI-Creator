"""
End-to-End Playwright tests for Pixel AI Creator frontend.

This test suite covers:
- Complete user journeys from login to chatbot creation
- Frontend-backend integration testing
- UI/UX validation and accessibility testing
- Cross-browser compatibility testing
- Performance and load testing
"""

import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import asyncio
import json
import time
from datetime import datetime
import os

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000")
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser):
    """Create browser context with common settings."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
        timezone_id="America/New_York",
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext):
    """Create a new page for each test."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def test_user():
    """Test user credentials."""
    return {
        "email": f"test.user.{int(time.time())}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User E2E",
    }


@pytest.fixture
def test_client_data():
    """Test client data."""
    timestamp = int(time.time())
    return {
        "name": f"E2E Test Client {timestamp}",
        "email": f"client.{timestamp}@testcorp.com",
        "industry": "Technology",
        "description": "End-to-end test client",
    }


class TestAuthenticationFlows:
    """Test complete authentication user journeys."""

    async def test_user_registration_flow(self, page: Page, test_user):
        """Test complete user registration flow."""
        # Navigate to registration page
        await page.goto(f"{BASE_URL}/register")
        await page.wait_for_load_state("networkidle")

        # Verify registration form is visible
        await page.wait_for_selector('[data-testid="register-form"]')

        # Fill registration form
        await page.fill('[data-testid="email-input"]', test_user["email"])
        await page.fill('[data-testid="password-input"]', test_user["password"])
        await page.fill('[data-testid="full-name-input"]', test_user["full_name"])

        # Submit registration
        await page.click('[data-testid="register-button"]')

        # Wait for successful registration and redirect
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)

        # Verify user is on dashboard
        await page.wait_for_selector('[data-testid="dashboard-welcome"]')
        welcome_text = await page.text_content('[data-testid="dashboard-welcome"]')
        assert test_user["full_name"] in welcome_text

    async def test_user_login_flow(self, page: Page, test_user):
        """Test user login flow."""
        # First register the user via API
        async with page.request.new_context() as api_context:
            await api_context.post(f"{API_URL}/api/auth/register", data=test_user)

        # Navigate to login page
        await page.goto(f"{BASE_URL}/login")
        await page.wait_for_load_state("networkidle")

        # Fill login form
        await page.fill('[data-testid="login-email"]', test_user["email"])
        await page.fill('[data-testid="login-password"]', test_user["password"])

        # Submit login
        await page.click('[data-testid="login-button"]')

        # Wait for redirect to dashboard
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)

        # Verify successful login
        await page.wait_for_selector('[data-testid="user-menu"]')
        user_menu = await page.text_content('[data-testid="user-menu"]')
        assert test_user["full_name"] in user_menu

    async def test_logout_flow(self, page: Page, test_user):
        """Test user logout flow."""
        # Login first
        await self.login_user(page, test_user)

        # Click user menu
        await page.click('[data-testid="user-menu"]')
        await page.wait_for_selector('[data-testid="logout-button"]')

        # Click logout
        await page.click('[data-testid="logout-button"]')

        # Verify redirect to login page
        await page.wait_for_url(f"{BASE_URL}/login", timeout=10000)

        # Verify login form is visible
        await page.wait_for_selector('[data-testid="login-form"]')

    async def login_user(self, page: Page, user_data):
        """Helper method to login a user."""
        # Register user via API first
        async with page.request.new_context() as api_context:
            register_response = await api_context.post(
                f"{API_URL}/api/auth/register", data=user_data
            )
            assert register_response.ok

        # Navigate and login
        await page.goto(f"{BASE_URL}/login")
        await page.fill('[data-testid="login-email"]', user_data["email"])
        await page.fill('[data-testid="login-password"]', user_data["password"])
        await page.click('[data-testid="login-button"]')
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)


class TestClientManagementFlows:
    """Test complete client management user journeys."""

    async def login_user(self, page: Page, user_data):
        """Helper method to login a user."""
        async with page.request.new_context() as api_context:
            register_response = await api_context.post(
                f"{API_URL}/api/auth/register", data=user_data
            )
            assert register_response.ok

        await page.goto(f"{BASE_URL}/login")
        await page.fill('[data-testid="login-email"]', user_data["email"])
        await page.fill('[data-testid="login-password"]', user_data["password"])
        await page.click('[data-testid="login-button"]')
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)

    async def test_create_client_flow(self, page: Page, test_user, test_client_data):
        """Test complete client creation flow."""
        # Login first
        await self.login_user(page, test_user)

        # Navigate to clients page
        await page.click('[data-testid="nav-clients"]')
        await page.wait_for_url(f"{BASE_URL}/clients", timeout=10000)

        # Click create client button
        await page.click('[data-testid="create-client-button"]')
        await page.wait_for_selector('[data-testid="client-form"]')

        # Fill client form
        await page.fill('[data-testid="client-name"]', test_client_data["name"])
        await page.fill('[data-testid="client-email"]', test_client_data["email"])
        await page.select_option(
            '[data-testid="client-industry"]', test_client_data["industry"]
        )
        await page.fill(
            '[data-testid="client-description"]', test_client_data["description"]
        )

        # Submit form
        await page.click('[data-testid="submit-client-form"]')

        # Wait for success notification
        await page.wait_for_selector('[data-testid="success-notification"]')

        # Verify client appears in list
        await page.wait_for_selector(
            f'[data-testid="client-{test_client_data["name"]}"]'
        )
        client_element = await page.text_content(
            f'[data-testid="client-{test_client_data["name"]}"]'
        )
        assert test_client_data["name"] in client_element

    async def test_edit_client_flow(self, page: Page, test_user, test_client_data):
        """Test client editing flow."""
        # Login and create client first
        await self.login_user(page, test_user)

        # Create client via API for efficiency
        async with page.request.new_context() as api_context:
            # Get auth token
            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": test_user["email"], "password": test_user["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            # Create client
            await api_context.post(
                f"{API_URL}/api/clients",
                data=test_client_data,
                headers={"Authorization": f"Bearer {token}"},
            )

        # Navigate to clients page
        await page.goto(f"{BASE_URL}/clients")
        await page.wait_for_load_state("networkidle")

        # Find and click edit button for the client
        await page.click(f'[data-testid="edit-client-{test_client_data["name"]}"]')
        await page.wait_for_selector('[data-testid="edit-client-form"]')

        # Update client name
        updated_name = f"{test_client_data['name']} - Updated"
        await page.fill('[data-testid="client-name"]', updated_name)

        # Submit changes
        await page.click('[data-testid="save-client-changes"]')

        # Wait for success notification
        await page.wait_for_selector('[data-testid="success-notification"]')

        # Verify updated name appears
        await page.wait_for_selector(f'[data-testid="client-{updated_name}"]')

    async def test_delete_client_flow(self, page: Page, test_user, test_client_data):
        """Test client deletion flow."""
        # Setup - login and create client
        await self.login_user(page, test_user)

        async with page.request.new_context() as api_context:
            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": test_user["email"], "password": test_user["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            await api_context.post(
                f"{API_URL}/api/clients",
                data=test_client_data,
                headers={"Authorization": f"Bearer {token}"},
            )

        # Navigate to clients page
        await page.goto(f"{BASE_URL}/clients")
        await page.wait_for_load_state("networkidle")

        # Click delete button
        await page.click(f'[data-testid="delete-client-{test_client_data["name"]}"]')

        # Confirm deletion in modal
        await page.wait_for_selector('[data-testid="delete-confirmation-modal"]')
        await page.click('[data-testid="confirm-delete"]')

        # Wait for success notification
        await page.wait_for_selector('[data-testid="success-notification"]')

        # Verify client is removed from list
        await page.wait_for_function(
            f'() => !document.querySelector("[data-testid=\\"client-{test_client_data["name"]}\\"]")',
            timeout=5000,
        )


class TestChatbotCreationFlows:
    """Test complete chatbot creation user journeys."""

    async def setup_client(self, page: Page, user_data, client_data):
        """Helper to setup user and client."""
        # Register and login user
        async with page.request.new_context() as api_context:
            register_response = await api_context.post(
                f"{API_URL}/api/auth/register", data=user_data
            )
            assert register_response.ok

            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": user_data["email"], "password": user_data["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            # Create client
            client_response = await api_context.post(
                f"{API_URL}/api/clients",
                data=client_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            client_data_response = await client_response.json()

        # Login in browser
        await page.goto(f"{BASE_URL}/login")
        await page.fill('[data-testid="login-email"]', user_data["email"])
        await page.fill('[data-testid="login-password"]', user_data["password"])
        await page.click('[data-testid="login-button"]')
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)

        return client_data_response["id"]

    async def test_basic_chatbot_creation_flow(
        self, page: Page, test_user, test_client_data
    ):
        """Test basic chatbot creation flow."""
        # Setup
        client_id = await self.setup_client(page, test_user, test_client_data)

        # Navigate to chatbot creation
        await page.click('[data-testid="nav-chatbots"]')
        await page.wait_for_url(f"{BASE_URL}/chatbots", timeout=10000)
        await page.click('[data-testid="create-chatbot-button"]')

        # Fill chatbot creation form
        await page.wait_for_selector('[data-testid="chatbot-creation-form"]')
        await page.fill('[data-testid="chatbot-name"]', "E2E Test Bot")
        await page.select_option('[data-testid="chatbot-type"]', "customer_support")
        await page.select_option('[data-testid="chatbot-complexity"]', "basic")
        await page.select_option('[data-testid="chatbot-client"]', str(client_id))
        await page.fill(
            '[data-testid="chatbot-requirements"]',
            "Basic customer support functionality",
        )

        # Submit form
        await page.click('[data-testid="create-chatbot-submit"]')

        # Wait for success and redirect to chatbot details
        await page.wait_for_selector('[data-testid="chatbot-creation-success"]')

        # Verify chatbot appears in list
        await page.goto(f"{BASE_URL}/chatbots")
        await page.wait_for_selector('[data-testid="chatbot-E2E Test Bot"]')

    async def test_advanced_chatbot_creation_flow(
        self, page: Page, test_user, test_client_data
    ):
        """Test advanced chatbot creation with custom settings."""
        # Setup
        client_id = await self.setup_client(page, test_user, test_client_data)

        # Navigate to advanced chatbot creation
        await page.click('[data-testid="nav-chatbots"]')
        await page.click('[data-testid="create-chatbot-button"]')
        await page.click('[data-testid="advanced-mode-toggle"]')

        # Fill advanced form
        await page.fill('[data-testid="chatbot-name"]', "Advanced E2E Bot")
        await page.select_option('[data-testid="chatbot-type"]', "sales")
        await page.select_option('[data-testid="chatbot-complexity"]', "enterprise")
        await page.select_option('[data-testid="chatbot-client"]', str(client_id))

        # Advanced settings
        await page.check('[data-testid="enable-multilingual"]')
        await page.select_option('[data-testid="primary-language"]', "en")
        await page.check('[data-testid="enable-sentiment-analysis"]')
        await page.check('[data-testid="enable-escalation"]')

        # Custom personality settings
        await page.fill(
            '[data-testid="personality-traits"]',
            "Professional, empathetic, solution-oriented",
        )
        await page.fill('[data-testid="response-style"]', "Concise and helpful")

        # Integration settings
        await page.check('[data-testid="enable-crm-integration"]')
        await page.fill('[data-testid="api-endpoints"]', "https://api.example.com/crm")

        # Submit advanced form
        await page.click('[data-testid="create-advanced-chatbot"]')

        # Wait for processing
        await page.wait_for_selector('[data-testid="chatbot-processing"]')

        # Verify creation success
        await page.wait_for_selector(
            '[data-testid="chatbot-creation-success"]', timeout=30000
        )

    async def test_chatbot_configuration_flow(
        self, page: Page, test_user, test_client_data
    ):
        """Test chatbot configuration after creation."""
        # Create chatbot first
        client_id = await self.setup_client(page, test_user, test_client_data)

        # Create chatbot via API for efficiency
        async with page.request.new_context() as api_context:
            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": test_user["email"], "password": test_user["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            chatbot_data = {
                "name": "Config Test Bot",
                "type": "customer_support",
                "complexity": "moderate",
                "client_id": client_id,
                "industry": "Technology",
            }
            chatbot_response = await api_context.post(
                f"{API_URL}/api/chatbots",
                data=chatbot_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            chatbot_info = await chatbot_response.json()

        # Navigate to chatbot configuration
        await page.goto(f"{BASE_URL}/chatbots/{chatbot_info['id']}/configure")
        await page.wait_for_load_state("networkidle")

        # Test general settings
        await page.click('[data-testid="general-settings-tab"]')
        await page.fill('[data-testid="response-timeout"]', "30")
        await page.fill('[data-testid="max-conversation-length"]', "50")
        await page.check('[data-testid="enable-logging"]')

        # Test conversation settings
        await page.click('[data-testid="conversation-settings-tab"]')
        await page.check('[data-testid="auto-greeting"]')
        await page.fill(
            '[data-testid="greeting-message"]', "Hello! How can I help you today?"
        )
        await page.check('[data-testid="enable-feedback"]')

        # Test integration settings
        await page.click('[data-testid="integration-settings-tab"]')
        await page.check('[data-testid="webhook-notifications"]')
        await page.fill('[data-testid="webhook-url"]', "https://example.com/webhook")

        # Save configuration
        await page.click('[data-testid="save-configuration"]')

        # Verify success
        await page.wait_for_selector('[data-testid="config-saved-notification"]')


class TestConversationFlows:
    """Test conversation management flows."""

    async def setup_chatbot(self, page: Page, user_data, client_data):
        """Helper to setup user, client, and chatbot."""
        async with page.request.new_context() as api_context:
            # Register user
            register_response = await api_context.post(
                f"{API_URL}/api/auth/register", data=user_data
            )
            assert register_response.ok

            # Login
            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": user_data["email"], "password": user_data["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            # Create client
            client_response = await api_context.post(
                f"{API_URL}/api/clients",
                data=client_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            client_info = await client_response.json()

            # Create chatbot
            chatbot_data = {
                "name": "Conversation Test Bot",
                "type": "customer_support",
                "complexity": "basic",
                "client_id": client_info["id"],
                "industry": "Technology",
            }
            chatbot_response = await api_context.post(
                f"{API_URL}/api/chatbots",
                data=chatbot_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            chatbot_info = await chatbot_response.json()

        # Login in browser
        await page.goto(f"{BASE_URL}/login")
        await page.fill('[data-testid="login-email"]', user_data["email"])
        await page.fill('[data-testid="login-password"]', user_data["password"])
        await page.click('[data-testid="login-button"]')
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)

        return chatbot_info["id"]

    async def test_start_conversation_flow(
        self, page: Page, test_user, test_client_data
    ):
        """Test starting a new conversation."""
        # Setup
        chatbot_id = await self.setup_chatbot(page, test_user, test_client_data)

        # Navigate to conversations
        await page.click('[data-testid="nav-conversations"]')
        await page.wait_for_url(f"{BASE_URL}/conversations", timeout=10000)

        # Start new conversation
        await page.click('[data-testid="start-conversation-button"]')
        await page.wait_for_selector('[data-testid="new-conversation-form"]')

        # Select chatbot and set title
        await page.select_option(
            '[data-testid="conversation-chatbot"]', str(chatbot_id)
        )
        await page.fill('[data-testid="conversation-title"]', "E2E Test Conversation")

        # Start conversation
        await page.click('[data-testid="start-conversation"]')

        # Verify conversation interface loads
        await page.wait_for_selector('[data-testid="conversation-interface"]')
        await page.wait_for_selector('[data-testid="message-input"]')

    async def test_send_messages_flow(self, page: Page, test_user, test_client_data):
        """Test sending messages in conversation."""
        # Setup and start conversation
        chatbot_id = await self.setup_chatbot(page, test_user, test_client_data)

        # Create conversation via API
        async with page.request.new_context() as api_context:
            login_response = await api_context.post(
                f"{API_URL}/api/auth/login",
                data={"email": test_user["email"], "password": test_user["password"]},
            )
            login_data = await login_response.json()
            token = login_data["access_token"]

            conv_data = {"chatbot_id": chatbot_id, "title": "Message Test Conversation"}
            conv_response = await api_context.post(
                f"{API_URL}/api/conversations",
                data=conv_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            conv_info = await conv_response.json()

        # Navigate to conversation
        await page.goto(f"{BASE_URL}/conversations/{conv_info['id']}")
        await page.wait_for_load_state("networkidle")

        # Send test messages
        test_messages = [
            "Hello, I need help with my account",
            "Can you provide information about your services?",
            "Thank you for your assistance",
        ]

        for message in test_messages:
            # Type message
            await page.fill('[data-testid="message-input"]', message)

            # Send message
            await page.click('[data-testid="send-message-button"]')

            # Wait for message to appear in chat
            await page.wait_for_selector(f'[data-message-content="{message}"]')

            # Wait a bit for any bot response
            await page.wait_for_timeout(2000)

        # Verify all messages are visible
        messages_count = await page.locator('[data-testid="chat-message"]').count()
        assert messages_count >= len(test_messages)


class TestPerformanceAndAccessibility:
    """Test performance and accessibility requirements."""

    async def test_page_load_performance(self, page: Page, test_user):
        """Test page load performance."""
        # Register and login user
        async with page.request.new_context() as api_context:
            await api_context.post(f"{API_URL}/api/auth/register", data=test_user)

        await page.goto(f"{BASE_URL}/login")
        await page.fill('[data-testid="login-email"]', test_user["email"])
        await page.fill('[data-testid="login-password"]', test_user["password"])

        # Measure login and dashboard load time
        start_time = time.time()
        await page.click('[data-testid="login-button"]')
        await page.wait_for_url(f"{BASE_URL}/dashboard", timeout=10000)
        await page.wait_for_load_state("networkidle")
        end_time = time.time()

        load_time = end_time - start_time
        assert load_time < 5.0, f"Dashboard load time {load_time}s exceeds 5s threshold"

    async def test_accessibility_compliance(self, page: Page):
        """Test basic accessibility compliance."""
        await page.goto(f"{BASE_URL}/login")
        await page.wait_for_load_state("networkidle")

        # Check for proper heading structure
        h1_count = await page.locator("h1").count()
        assert h1_count >= 1, "Page should have at least one H1 heading"

        # Check for alt attributes on images
        images = await page.locator("img").all()
        for img in images:
            alt_text = await img.get_attribute("alt")
            assert alt_text is not None, "All images should have alt attributes"

        # Check for form labels
        inputs = await page.locator('input[type="email"], input[type="password"]').all()
        for input_elem in inputs:
            aria_label = await input_elem.get_attribute("aria-label")
            associated_label = await input_elem.get_attribute("aria-labelledby")
            assert (
                aria_label or associated_label
            ), "All inputs should have proper labels"

    async def test_responsive_design(self, page: Page):
        """Test responsive design across different screen sizes."""
        test_sizes = [
            {"width": 375, "height": 667},  # Mobile
            {"width": 768, "height": 1024},  # Tablet
            {"width": 1280, "height": 720},  # Desktop
            {"width": 1920, "height": 1080},  # Large desktop
        ]

        for size in test_sizes:
            await page.set_viewport_size(size)
            await page.goto(f"{BASE_URL}/login")
            await page.wait_for_load_state("networkidle")

            # Check if login form is visible and properly sized
            form = page.locator('[data-testid="login-form"]')
            await form.wait_for()

            form_box = await form.bounding_box()
            assert (
                form_box is not None
            ), f"Login form should be visible at {size['width']}x{size['height']}"
            assert form_box["width"] > 0, "Form should have positive width"
            assert form_box["height"] > 0, "Form should have positive height"


class TestErrorHandlingFlows:
    """Test error handling in user flows."""

    async def test_network_error_handling(self, page: Page, test_user):
        """Test handling of network errors."""
        await page.goto(f"{BASE_URL}/login")

        # Block network requests to simulate network failure
        await page.route("**/api/**", lambda route: route.abort())

        # Try to login
        await page.fill('[data-testid="login-email"]', test_user["email"])
        await page.fill('[data-testid="login-password"]', test_user["password"])
        await page.click('[data-testid="login-button"]')

        # Should show error message
        await page.wait_for_selector('[data-testid="error-notification"]')
        error_text = await page.text_content('[data-testid="error-notification"]')
        assert "network" in error_text.lower() or "connection" in error_text.lower()

    async def test_validation_error_display(self, page: Page):
        """Test form validation error display."""
        await page.goto(f"{BASE_URL}/register")

        # Submit form without filling required fields
        await page.click('[data-testid="register-button"]')

        # Should show validation errors
        await page.wait_for_selector('[data-testid="validation-error"]')

        # Fill invalid email
        await page.fill('[data-testid="email-input"]', "invalid-email")
        await page.click('[data-testid="register-button"]')

        # Should show email validation error
        email_error = await page.wait_for_selector(
            '[data-testid="email-validation-error"]'
        )
        error_text = await email_error.text_content()
        assert "email" in error_text.lower()


if __name__ == "__main__":
    # Run with pytest-playwright
    # pytest tests/test_e2e_playwright.py --browser chromium --headed
    pass
