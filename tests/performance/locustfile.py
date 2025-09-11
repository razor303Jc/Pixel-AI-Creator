"""
Performance testing with Locust for Pixel AI Creator API.

This file contains performance tests for:
- API endpoint load testing
- Concurrent user simulation
- Response time benchmarking
- Stress testing scenarios
- Resource utilization monitoring
"""

from locust import HttpUser, task, between
import json
import random
import string
from datetime import datetime


class PixelAIUser(HttpUser):
    """Simulated user for performance testing."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Setup user session."""
        self.register_and_login()
        self.create_test_client()

    def register_and_login(self):
        """Register a new user and login."""
        # Generate unique user data
        timestamp = str(int(datetime.now().timestamp()))
        self.user_data = {
            "email": f"perf_user_{timestamp}_{random.randint(1000, 9999)}@example.com",
            "password": "PerfTest123!",
            "full_name": f"Performance User {timestamp}",
        }

        # Register user
        register_response = self.client.post("/api/auth/register", json=self.user_data)
        if register_response.status_code == 201:
            data = register_response.json()
            self.access_token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            # Try to login if user already exists
            login_response = self.client.post(
                "/api/auth/login",
                json={
                    "email": self.user_data["email"],
                    "password": self.user_data["password"],
                },
            )
            if login_response.status_code == 200:
                data = login_response.json()
                self.access_token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def create_test_client(self):
        """Create a test client for the user."""
        client_data = {
            "name": f"Perf Test Client {random.randint(1000, 9999)}",
            "email": f"client_{random.randint(1000, 9999)}@perftest.com",
            "industry": random.choice(
                ["Technology", "Healthcare", "Finance", "Retail"]
            ),
            "description": "Performance testing client",
        }

        response = self.client.post(
            "/api/clients", json=client_data, headers=self.headers
        )
        if response.status_code == 201:
            self.client_id = response.json()["id"]

    @task(10)
    def view_dashboard(self):
        """View user dashboard - most common action."""
        self.client.get("/api/auth/profile", headers=self.headers, name="Dashboard")

    @task(8)
    def list_clients(self):
        """List clients - frequent action."""
        self.client.get("/api/clients", headers=self.headers, name="List Clients")

    @task(6)
    def view_client_details(self):
        """View specific client details."""
        if hasattr(self, "client_id"):
            self.client.get(
                f"/api/clients/{self.client_id}",
                headers=self.headers,
                name="View Client",
            )

    @task(5)
    def list_chatbots(self):
        """List chatbots."""
        self.client.get("/api/chatbots", headers=self.headers, name="List Chatbots")

    @task(4)
    def create_chatbot(self):
        """Create a new chatbot."""
        if hasattr(self, "client_id"):
            chatbot_data = {
                "name": f"Perf Bot {random.randint(1000, 9999)}",
                "type": random.choice(["customer_support", "sales", "lead_generation"]),
                "complexity": random.choice(["basic", "moderate", "advanced"]),
                "client_id": self.client_id,
                "industry": "Technology",
                "requirements": "Performance testing chatbot",
            }
            self.client.post(
                "/api/chatbots",
                json=chatbot_data,
                headers=self.headers,
                name="Create Chatbot",
            )

    @task(3)
    def list_conversations(self):
        """List conversations."""
        self.client.get(
            "/api/conversations", headers=self.headers, name="List Conversations"
        )

    @task(2)
    def view_analytics(self):
        """View analytics dashboard."""
        self.client.get(
            "/api/analytics/summary", headers=self.headers, name="Analytics Summary"
        )

    @task(2)
    def update_profile(self):
        """Update user profile."""
        update_data = {"full_name": f"Updated Perf User {random.randint(1000, 9999)}"}
        self.client.put(
            "/api/auth/profile",
            json=update_data,
            headers=self.headers,
            name="Update Profile",
        )

    @task(1)
    def create_conversation(self):
        """Create a new conversation - less frequent."""
        # First get available chatbots
        chatbots_response = self.client.get("/api/chatbots", headers=self.headers)
        if chatbots_response.status_code == 200:
            chatbots = chatbots_response.json().get("chatbots", [])
            if chatbots:
                chatbot_id = random.choice(chatbots)["id"]
                conv_data = {
                    "chatbot_id": chatbot_id,
                    "title": f"Perf Test Conversation {random.randint(1000, 9999)}",
                }
                self.client.post(
                    "/api/conversations",
                    json=conv_data,
                    headers=self.headers,
                    name="Create Conversation",
                )


class AdminUser(HttpUser):
    """Admin user for testing admin-specific endpoints."""

    wait_time = between(2, 5)
    weight = 1  # Less frequent than regular users

    def on_start(self):
        """Setup admin user session."""
        self.register_admin_and_login()

    def register_admin_and_login(self):
        """Register admin user and login."""
        timestamp = str(int(datetime.now().timestamp()))
        self.admin_data = {
            "email": f"admin_perf_{timestamp}_{random.randint(1000, 9999)}@example.com",
            "password": "AdminPerf123!",
            "full_name": f"Admin Performance User {timestamp}",
            "role": "admin",
        }

        # Register admin
        register_response = self.client.post("/api/auth/register", json=self.admin_data)
        if register_response.status_code == 201:
            data = register_response.json()
            self.access_token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @task(5)
    def view_admin_dashboard(self):
        """View admin dashboard."""
        self.client.get(
            "/api/admin/dashboard", headers=self.headers, name="Admin Dashboard"
        )

    @task(3)
    def view_system_stats(self):
        """View system statistics."""
        self.client.get("/api/admin/stats", headers=self.headers, name="System Stats")

    @task(2)
    def view_all_users(self):
        """View all users - admin only."""
        self.client.get("/api/admin/users", headers=self.headers, name="All Users")

    @task(2)
    def view_system_health(self):
        """Check system health."""
        self.client.get("/api/health", name="System Health")

    @task(1)
    def view_performance_metrics(self):
        """View performance metrics."""
        self.client.get(
            "/api/performance/cache/stats",
            headers=self.headers,
            name="Performance Metrics",
        )


class AnonymousUser(HttpUser):
    """Anonymous user for testing public endpoints."""

    wait_time = between(3, 8)
    weight = 2  # Some anonymous traffic

    @task(10)
    def view_landing_page(self):
        """View public landing page."""
        self.client.get("/", name="Landing Page")

    @task(5)
    def view_health_check(self):
        """Check API health."""
        self.client.get("/health", name="Health Check")

    @task(3)
    def view_api_docs(self):
        """View API documentation."""
        self.client.get("/docs", name="API Docs")

    @task(2)
    def attempt_protected_endpoint(self):
        """Attempt to access protected endpoint (should fail)."""
        self.client.get("/api/auth/profile", name="Protected Endpoint (Unauthorized)")


class StressTestUser(HttpUser):
    """High-intensity user for stress testing."""

    wait_time = between(0.1, 0.5)  # Very fast requests
    weight = 0.5  # Fewer stress test users

    def on_start(self):
        """Setup stress test user."""
        self.register_and_login()

    def register_and_login(self):
        """Register and login stress test user."""
        timestamp = str(int(datetime.now().timestamp()))
        self.user_data = {
            "email": f"stress_user_{timestamp}_{random.randint(1000, 9999)}@example.com",
            "password": "StressTest123!",
            "full_name": f"Stress Test User {timestamp}",
        }

        register_response = self.client.post("/api/auth/register", json=self.user_data)
        if register_response.status_code == 201:
            data = register_response.json()
            self.access_token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @task
    def rapid_requests(self):
        """Make rapid API requests."""
        endpoints = [
            "/api/auth/profile",
            "/api/clients",
            "/api/chatbots",
            "/api/conversations",
            "/health",
        ]

        endpoint = random.choice(endpoints)
        if endpoint == "/health":
            self.client.get(endpoint, name="Stress - Health")
        else:
            self.client.get(endpoint, headers=self.headers, name=f"Stress - {endpoint}")


class DatabaseIntensiveUser(HttpUser):
    """User that performs database-intensive operations."""

    wait_time = between(1, 2)
    weight = 0.3  # Limited number for database stress

    def on_start(self):
        """Setup database test user."""
        self.register_and_login()
        self.create_multiple_clients()

    def register_and_login(self):
        """Register and login."""
        timestamp = str(int(datetime.now().timestamp()))
        self.user_data = {
            "email": f"db_user_{timestamp}_{random.randint(1000, 9999)}@example.com",
            "password": "DBTest123!",
            "full_name": f"DB Test User {timestamp}",
        }

        register_response = self.client.post("/api/auth/register", json=self.user_data)
        if register_response.status_code == 201:
            data = register_response.json()
            self.access_token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client_ids = []
        self.chatbot_ids = []

    def create_multiple_clients(self):
        """Create multiple clients for testing."""
        for i in range(3):
            client_data = {
                "name": f"DB Test Client {i} - {random.randint(1000, 9999)}",
                "email": f"dbclient{i}_{random.randint(1000, 9999)}@test.com",
                "industry": random.choice(["Technology", "Healthcare", "Finance"]),
                "description": f"Database test client {i}",
            }

            response = self.client.post(
                "/api/clients", json=client_data, headers=self.headers
            )
            if response.status_code == 201:
                self.client_ids.append(response.json()["id"])

    @task(5)
    def complex_client_query(self):
        """Perform complex client queries."""
        params = {
            "page": random.randint(1, 5),
            "limit": random.randint(10, 50),
            "industry": random.choice(["Technology", "Healthcare", "Finance", ""]),
        }
        self.client.get(
            "/api/clients",
            params=params,
            headers=self.headers,
            name="Complex Client Query",
        )

    @task(3)
    def create_multiple_chatbots(self):
        """Create multiple chatbots."""
        if self.client_ids:
            for _ in range(2):
                client_id = random.choice(self.client_ids)
                chatbot_data = {
                    "name": f"DB Test Bot {random.randint(1000, 9999)}",
                    "type": random.choice(
                        ["customer_support", "sales", "lead_generation"]
                    ),
                    "complexity": random.choice(["basic", "moderate", "advanced"]),
                    "client_id": client_id,
                    "industry": "Technology",
                }
                response = self.client.post(
                    "/api/chatbots",
                    json=chatbot_data,
                    headers=self.headers,
                    name="Create Multiple Chatbots",
                )
                if response.status_code == 201:
                    self.chatbot_ids.append(response.json()["id"])

    @task(2)
    def bulk_conversation_creation(self):
        """Create multiple conversations."""
        if self.chatbot_ids:
            for _ in range(3):
                chatbot_id = random.choice(self.chatbot_ids)
                conv_data = {
                    "chatbot_id": chatbot_id,
                    "title": f"DB Test Conversation {random.randint(1000, 9999)}",
                }
                self.client.post(
                    "/api/conversations",
                    json=conv_data,
                    headers=self.headers,
                    name="Bulk Conversations",
                )


# Custom events for monitoring
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """Log successful requests."""
    if response_time > 2000:  # Log slow requests (>2 seconds)
        print(f"SLOW REQUEST: {name} took {response_time}ms")


def on_request_failure(
    request_type, name, response_time, response_length, exception, **kwargs
):
    """Log failed requests."""
    print(f"FAILED REQUEST: {name} failed with {exception}")


# Register event handlers
import locust.events

locust.events.request_success.add_listener(on_request_success)
locust.events.request_failure.add_listener(on_request_failure)
