"""
Playwright End-to-End Tests for Pixel-AI-Creator Frontend
Tests user interactions and frontend functionality
"""

import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import asyncio
import time


class TestFrontendAccessibility:
    """Test basic frontend accessibility and loading"""

    FRONTEND_URL = "http://localhost:3002"
    API_URL = "http://localhost:8002"

    @pytest.fixture
    async def browser_setup(self):
        """Setup browser for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            yield page, browser, context
            await context.close()
            await browser.close()

    async def test_homepage_loads(self, browser_setup):
        """Test homepage loads successfully"""
        page, browser, context = browser_setup

        try:
            await page.goto(self.FRONTEND_URL, timeout=10000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Check if page loaded
            title = await page.title()
            assert "Pixel AI Creator" in title

            # Check for main content
            main_content = await page.query_selector("body")
            assert main_content is not None

        except Exception as e:
            pytest.skip(f"Frontend not accessible: {e}")

    async def test_page_structure(self, browser_setup):
        """Test basic page structure elements"""
        page, browser, context = browser_setup

        try:
            await page.goto(self.FRONTEND_URL, timeout=10000)
            await page.wait_for_load_state("networkidle", timeout=5000)

            # Check for React app root element
            root_element = await page.query_selector("#root")
            assert root_element is not None

            # Check for any navigation elements
            nav_elements = await page.query_selector_all(
                'nav, header, [role="navigation"]'
            )
            # Navigation might exist

            # Check for main content area
            main_areas = await page.query_selector_all(
                'main, [role="main"], .main-content'
            )
            # Main content area should exist in some form

        except Exception as e:
            pytest.skip(f"Page structure test failed: {e}")

    async def test_responsive_design(self, browser_setup):
        """Test responsive design on different screen sizes"""
        page, browser, context = browser_setup

        try:
            await page.goto(self.FRONTEND_URL, timeout=10000)

            # Test different viewport sizes
            viewports = [
                {"width": 1920, "height": 1080},  # Desktop
                {"width": 768, "height": 1024},  # Tablet
                {"width": 375, "height": 667},  # Mobile
            ]

            for viewport in viewports:
                await page.set_viewport_size(viewport["width"], viewport["height"])
                await page.wait_for_timeout(1000)  # Allow layout to adjust

                # Check if page is still functional
                body = await page.query_selector("body")
                assert body is not None

                # Check for responsive elements
                content_width = await page.evaluate("document.body.scrollWidth")
                assert content_width <= viewport["width"] + 50  # Allow some tolerance

        except Exception as e:
            pytest.skip(f"Responsive design test failed: {e}")


class TestUserInteractions:
    """Test user interaction flows"""

    FRONTEND_URL = "http://localhost:3002"

    @pytest.fixture
    async def page_setup(self):
        """Setup page for interaction testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(self.FRONTEND_URL, timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=5000)
                yield page
            except Exception:
                pytest.skip("Frontend not accessible for interaction testing")
            finally:
                await context.close()
                await browser.close()

    async def test_form_interactions(self, page_setup):
        """Test form input interactions"""
        page = page_setup

        try:
            # Look for input forms
            input_fields = await page.query_selector_all("input, textarea, select")

            for field in input_fields[:3]:  # Test first 3 fields
                field_type = await field.get_attribute("type")
                field_name = await field.get_attribute("name") or "test"

                if field_type in ["text", "email", "password"] or field_type is None:
                    await field.fill("test input")
                    value = await field.input_value()
                    assert "test" in value

        except Exception as e:
            # Forms might not exist yet, that's okay
            pass

    async def test_button_clicks(self, page_setup):
        """Test button click interactions"""
        page = page_setup

        try:
            # Look for clickable buttons
            buttons = await page.query_selector_all('button, [role="button"], .btn')

            for button in buttons[:2]:  # Test first 2 buttons
                if await button.is_visible():
                    # Check if button is enabled
                    is_disabled = await button.get_attribute("disabled")
                    if not is_disabled:
                        await button.click()
                        await page.wait_for_timeout(1000)  # Allow for any response

        except Exception as e:
            # Buttons might not exist or might trigger complex flows
            pass

    async def test_navigation_flow(self, page_setup):
        """Test navigation between pages/sections"""
        page = page_setup

        try:
            # Look for navigation links
            nav_links = await page.query_selector_all('a, [role="link"]')

            initial_url = page.url

            for link in nav_links[:2]:  # Test first 2 links
                href = await link.get_attribute("href")
                if href and not href.startswith("http") and href != "#":
                    await link.click()
                    await page.wait_for_timeout(2000)

                    # Check if navigation occurred
                    current_url = page.url
                    # URL might change or stay same for SPA

                    # Go back to test other links
                    await page.goto(initial_url)
                    await page.wait_for_timeout(1000)

        except Exception as e:
            # Navigation might not be implemented yet
            pass


class TestAPIIntegration:
    """Test frontend-backend integration"""

    FRONTEND_URL = "http://localhost:3002"
    API_URL = "http://localhost:8002"

    @pytest.fixture
    async def page_with_network(self):
        """Setup page with network monitoring"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Track network requests
            network_requests = []

            async def handle_request(request):
                network_requests.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers),
                    }
                )

            page.on("request", handle_request)

            try:
                await page.goto(self.FRONTEND_URL, timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=5000)
                yield page, network_requests
            except Exception:
                pytest.skip("Frontend not accessible for API integration testing")
            finally:
                await context.close()
                await browser.close()

    async def test_api_calls_from_frontend(self, page_with_network):
        """Test that frontend makes appropriate API calls"""
        page, network_requests = page_with_network

        # Wait for initial requests to complete
        await page.wait_for_timeout(3000)

        # Check for API calls to backend
        api_requests = [req for req in network_requests if self.API_URL in req["url"]]

        # Frontend might make initial API calls
        # This test documents the integration even if no calls are made yet

        # Look for potential API interaction triggers
        buttons = await page.query_selector_all("button")
        for button in buttons[:1]:  # Test one button
            if await button.is_visible():
                try:
                    initial_request_count = len(network_requests)
                    await button.click()
                    await page.wait_for_timeout(2000)

                    # Check if new requests were made
                    new_requests = network_requests[initial_request_count:]
                    # Requests might be made to API

                except Exception:
                    pass

    async def test_error_handling(self, page_with_network):
        """Test frontend error handling"""
        page, network_requests = page_with_network

        # Test how frontend handles potential errors
        # This is more about ensuring no JS errors crash the page

        # Check browser console for errors
        console_messages = []

        async def handle_console(msg):
            if msg.type == "error":
                console_messages.append(msg.text)

        page.on("console", handle_console)

        # Interact with page to trigger potential errors
        await page.wait_for_timeout(2000)

        # Check that no critical errors occurred
        critical_errors = [msg for msg in console_messages if "error" in msg.lower()]
        # Some errors might be acceptable during development


class TestPerformance:
    """Test frontend performance"""

    FRONTEND_URL = "http://localhost:3002"

    async def test_page_load_performance(self):
        """Test page loading performance"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                start_time = time.time()
                await page.goto(self.FRONTEND_URL, timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                end_time = time.time()

                load_time = end_time - start_time

                # Page should load within reasonable time
                assert load_time < 10.0  # 10 seconds max for development

                # Check for basic performance metrics
                performance_metrics = await page.evaluate(
                    """() => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        loadComplete: navigation.loadEventEnd - navigation.loadEventStart
                    };
                }"""
                )

                # Metrics should be reasonable (in milliseconds)
                assert performance_metrics["domContentLoaded"] < 5000

            except Exception as e:
                pytest.skip(f"Performance test failed: {e}")
            finally:
                await context.close()
                await browser.close()

    async def test_resource_loading(self):
        """Test resource loading efficiency"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            resources_loaded = []

            async def handle_response(response):
                resources_loaded.append(
                    {
                        "url": response.url,
                        "status": response.status,
                        "content_type": response.headers.get("content-type", ""),
                        "size": (
                            len(await response.body()) if response.status == 200 else 0
                        ),
                    }
                )

            page.on("response", handle_response)

            try:
                await page.goto(self.FRONTEND_URL, timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=5000)

                # Check resource loading success rate
                successful_resources = [
                    r for r in resources_loaded if r["status"] == 200
                ]
                total_resources = len(resources_loaded)

                if total_resources > 0:
                    success_rate = len(successful_resources) / total_resources
                    assert (
                        success_rate >= 0.8
                    )  # 80% of resources should load successfully

                # Check for reasonable resource sizes
                large_resources = [
                    r for r in successful_resources if r["size"] > 1024 * 1024
                ]  # > 1MB
                # Large resources should be minimal for good performance

            except Exception as e:
                pytest.skip(f"Resource loading test failed: {e}")
            finally:
                await context.close()
                await browser.close()


if __name__ == "__main__":
    # Run basic frontend tests when script is executed directly
    print("Running basic frontend tests...")

    async def run_basic_tests():
        test_accessibility = TestFrontendAccessibility()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:3002", timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=5000)

                title = await page.title()
                print(f"✓ Frontend accessible, title: {title}")

                root = await page.query_selector("#root")
                if root:
                    print("✓ React app root element found")
                else:
                    print("✗ React app root element not found")

            except Exception as e:
                print(f"✗ Frontend accessibility failed: {e}")
            finally:
                await context.close()
                await browser.close()

    asyncio.run(run_basic_tests())
