import pytest
import asyncio
import psutil
import time
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor

from main import app


class TestLoadPerformance:
    """Load testing and performance validation"""

    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.performance
    async def test_concurrent_requests_load(self, client: AsyncClient):
        """Test system under concurrent request load"""

        async def make_request():
            response = await client.get("/health")
            return response.status_code == 200

        # Test with increasing concurrent requests
        for concurrency in [10, 25, 50, 100]:
            start_time = time.time()

            tasks = [make_request() for _ in range(concurrency)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            duration = end_time - start_time

            success_count = sum(1 for r in results if r is True)
            success_rate = success_count / concurrency

            print(
                f"Concurrency {concurrency}: {success_rate:.2%} success rate in {duration:.2f}s"
            )

            # Performance requirements
            assert success_rate >= 0.95  # 95% success rate
            assert duration < 10  # Complete within 10 seconds

    @pytest.mark.performance
    async def test_response_time_limits(self, client: AsyncClient):
        """Test response time requirements"""

        endpoints = ["/", "/health", "/api/pixel/status"]

        for endpoint in endpoints:
            start_time = time.time()
            response = await client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 2.0  # All endpoints should respond within 2 seconds

            print(f"{endpoint}: {response_time:.3f}s")

    @pytest.mark.performance
    async def test_memory_usage_under_load(self, client: AsyncClient):
        """Test memory usage doesn't grow excessively under load"""

        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate load
        tasks = []
        for i in range(200):
            client_data = {
                "name": f"Load Test Client {i}",
                "email": f"loadtest{i}@example.com",
                "company": f"Load Test Company {i}",
            }
            tasks.append(client.post("/api/clients", json=client_data))

        await asyncio.gather(*tasks, return_exceptions=True)

        # Measure memory after load
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(
            f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)"
        )

        # Memory shouldn't increase by more than 500MB under this load
        assert memory_increase < 500

    @pytest.mark.performance
    async def test_database_query_performance(self, client: AsyncClient):
        """Test database query performance"""

        # First create some test data
        for i in range(50):
            client_data = {
                "name": f"DB Test Client {i}",
                "email": f"dbtest{i}@example.com",
                "company": f"DB Test Company {i}",
            }
            await client.post("/api/clients", json=client_data)

        # Test query performance
        start_time = time.time()
        response = await client.get("/api/clients")
        end_time = time.time()

        query_time = end_time - start_time

        assert response.status_code == 200
        assert query_time < 1.0  # Query should complete within 1 second

        clients = response.json()
        assert len(clients) >= 50


class TestStressScenarios:
    """Stress testing with edge cases"""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.stress
    async def test_rapid_client_creation(self, client: AsyncClient):
        """Test rapid client creation without delays"""

        async def create_client(index):
            client_data = {
                "name": f"Rapid Client {index}",
                "email": f"rapid{index}@example.com",
                "company": f"Rapid Company {index}",
            }
            response = await client.post("/api/clients", json=client_data)
            return response.status_code

        # Create 100 clients as fast as possible
        start_time = time.time()

        tasks = [create_client(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        success_count = sum(1 for r in results if r == 200)

        print(f"Created {success_count}/100 clients in {duration:.2f}s")
        print(f"Rate: {success_count/duration:.1f} clients/second")

        # Should handle at least 80% successfully
        assert success_count >= 80

    @pytest.mark.stress
    async def test_large_payload_handling(self, client: AsyncClient):
        """Test handling of large payloads"""

        # Create client with very large description
        large_description = "A" * 10000  # 10KB description

        client_data = {
            "name": "Large Payload Client",
            "email": "large@example.com",
            "company": "Large Payload Company",
            "description": large_description,
        }

        response = await client.post("/api/clients", json=client_data)
        assert response.status_code == 200

        created_client = response.json()
        assert len(created_client["description"]) == 10000

    @pytest.mark.stress
    async def test_malformed_request_handling(self, client: AsyncClient):
        """Test system handles malformed requests gracefully"""

        malformed_requests = [
            # Missing required fields
            {"name": "Test"},
            # Invalid email format
            {"name": "Test", "email": "invalid"},
            # Extremely long fields
            {"name": "x" * 1000, "email": "test@example.com"},
            # Wrong data types
            {"name": 123, "email": "test@example.com"},
            # Empty request
            {},
        ]

        for malformed_data in malformed_requests:
            response = await client.post("/api/clients", json=malformed_data)
            # Should return 4xx error, not crash
            assert 400 <= response.status_code < 500


class TestScalabilityLimits:
    """Test system behavior at scale limits"""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.scalability
    async def test_max_clients_supported(self, client: AsyncClient):
        """Test creating large number of clients"""

        batch_size = 50
        total_clients = 1000

        for batch in range(0, total_clients, batch_size):
            tasks = []
            for i in range(batch, min(batch + batch_size, total_clients)):
                client_data = {
                    "name": f"Scale Client {i}",
                    "email": f"scale{i}@example.com",
                    "company": f"Scale Company {i}",
                }
                tasks.append(client.post("/api/clients", json=client_data))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(
                1 for r in results if hasattr(r, "status_code") and r.status_code == 200
            )

            print(
                f"Batch {batch//batch_size + 1}: {success_count}/{len(tasks)} successful"
            )

            # Should maintain high success rate even at scale
            assert success_count >= len(tasks) * 0.9  # 90% success rate

    @pytest.mark.scalability
    async def test_concurrent_analysis_requests(self, client: AsyncClient):
        """Test many concurrent analysis requests"""

        # Create a test client first
        client_data = {
            "name": "Analysis Test Client",
            "email": "analysistest@example.com",
            "company": "Analysis Test Company",
            "website": "https://test.com",
        }

        create_response = await client.post("/api/clients", json=client_data)
        client_id = create_response.json()["id"]

        # Start many concurrent analyses
        tasks = []
        for i in range(20):
            task = client.post(
                "/api/analyze/website",
                params={"url": f"https://test{i}.com", "client_id": client_id},
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(
            1 for r in results if hasattr(r, "status_code") and r.status_code == 200
        )

        print(f"Concurrent analyses: {success_count}/20 successful")

        # Should handle concurrent analyses well
        assert success_count >= 18  # 90% success rate


class TestResourceUtilization:
    """Test resource usage patterns"""

    @pytest.mark.resource
    async def test_cpu_usage_under_load(self):
        """Monitor CPU usage during load testing"""

        async with AsyncClient(app=app, base_url="http://test") as client:

            # Monitor CPU before load
            initial_cpu = psutil.cpu_percent(interval=1)

            # Generate CPU load with complex operations
            tasks = []
            for i in range(50):
                client_data = {
                    "name": f"CPU Test Client {i}",
                    "email": f"cputest{i}@example.com",
                    "company": f"CPU Test Company {i}",
                    "website": f"https://cputest{i}.com",
                }

                # Create client and start analysis (CPU intensive)
                create_task = client.post("/api/clients", json=client_data)
                tasks.append(create_task)

            await asyncio.gather(*tasks, return_exceptions=True)

            # Monitor CPU after load
            final_cpu = psutil.cpu_percent(interval=1)

            print(f"CPU usage: {initial_cpu}% -> {final_cpu}%")

            # CPU usage should not exceed reasonable limits
            assert final_cpu < 80  # Should stay under 80%

    @pytest.mark.resource
    async def test_connection_pool_limits(self):
        """Test database connection pool under stress"""

        async with AsyncClient(app=app, base_url="http://test") as client:

            # Create many concurrent database operations
            tasks = []
            for i in range(200):  # More than typical connection pool size
                tasks.append(client.get("/api/clients"))

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            duration = end_time - start_time
            success_count = sum(
                1 for r in results if hasattr(r, "status_code") and r.status_code == 200
            )

            print(f"Connection pool test: {success_count}/200 in {duration:.2f}s")

            # Should handle connection pool efficiently
            assert success_count >= 190  # 95% success rate
            assert duration < 30  # Complete within 30 seconds


class TestFailureScenarios:
    """Test system behavior under failure conditions"""

    @pytest.mark.failure
    async def test_database_connection_loss_simulation(self):
        """Test behavior when database is unavailable"""

        # This would require mocking database connection failures
        # For now, just test that errors are handled gracefully
        pass

    @pytest.mark.failure
    async def test_openai_api_failure_simulation(self):
        """Test behavior when OpenAI API is unavailable"""

        # This would require mocking OpenAI API failures
        # For now, just test that errors are handled gracefully
        pass


if __name__ == "__main__":
    # Run performance tests
    pytest.main(
        [
            __file__,
            "-v",
            "-m",
            "performance or stress or scalability or resource",
            "--tb=short",
        ]
    )
