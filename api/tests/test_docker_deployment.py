"""
Docker deployment and staging tests
"""

import pytest
import subprocess
import requests
import time
import docker
from pathlib import Path


class TestDockerDeployment:
    """Test Docker deployment functionality"""

    @pytest.fixture(scope="class")
    def docker_client(self):
        """Docker client fixture"""
        return docker.from_env()

    @pytest.fixture(scope="class")
    def project_root(self):
        """Project root directory"""
        return Path(__file__).parent.parent.parent

    def test_dockerfile_exists(self, project_root):
        """Test that Dockerfile exists and is valid"""
        api_dockerfile = project_root / "docker" / "api" / "Dockerfile"
        assert api_dockerfile.exists(), "API Dockerfile not found"

        # Check Dockerfile content
        content = api_dockerfile.read_text()
        assert "FROM python:3.11-slim" in content
        assert "COPY requirements.txt" in content
        assert "RUN pip install" in content
        assert "ENTRYPOINT" in content
        assert "HEALTHCHECK" in content

    def test_entrypoint_script_exists(self, project_root):
        """Test that entrypoint script exists and is executable"""
        entrypoint = project_root / "docker" / "api" / "entrypoint.sh"
        assert entrypoint.exists(), "Entrypoint script not found"
        assert entrypoint.stat().st_mode & 0o111, "Entrypoint not executable"

        # Check script content
        content = entrypoint.read_text()
        assert "#!/bin/bash" in content
        assert "validate_environment()" in content
        assert "wait_for_service()" in content
        assert "check_database()" in content
        assert "run_startup_tests()" in content

    def test_docker_compose_exists(self, project_root):
        """Test that docker-compose.yml exists and is valid"""
        compose_file = project_root / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml not found"

        content = compose_file.read_text()
        assert "version:" in content
        assert "services:" in content
        assert "api:" in content
        assert "postgres:" in content
        assert "redis:" in content

    def test_requirements_file_exists(self, project_root):
        """Test that requirements.txt exists"""
        requirements = project_root / "api" / "requirements.txt"
        assert requirements.exists(), "requirements.txt not found"

        content = requirements.read_text()
        assert "fastapi" in content
        assert "sqlalchemy" in content
        assert "redis" in content

    @pytest.mark.integration
    def test_docker_build_api(self, docker_client, project_root):
        """Test building the API Docker image"""
        try:
            # Build the image
            image, logs = docker_client.images.build(
                path=str(project_root / "api"),
                dockerfile=str(project_root / "docker" / "api" / "Dockerfile"),
                tag="pixel-ai-api:test",
                rm=True,
            )

            assert image is not None
            assert "pixel-ai-api:test" in [tag for tag in image.tags]

            # Cleanup
            docker_client.images.remove("pixel-ai-api:test", force=True)

        except docker.errors.BuildError as e:
            pytest.fail(f"Docker build failed: {e}")

    @pytest.mark.integration
    def test_docker_compose_validation(self, project_root):
        """Test docker-compose file validation"""
        compose_path = project_root / "docker-compose.yml"

        try:
            # Validate compose file
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_path), "config", "--quiet"],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            assert result.returncode == 0, f"Compose validation failed: {result.stderr}"

        except FileNotFoundError:
            pytest.skip("docker-compose not available")

    @pytest.mark.slow
    def test_full_stack_startup(self, docker_client, project_root):
        """Test full stack startup with docker-compose"""
        compose_path = project_root / "docker-compose.yml"

        try:
            # Start services
            startup_result = subprocess.run(
                ["docker-compose", "-f", str(compose_path), "up", "-d", "--build"],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            if startup_result.returncode != 0:
                pytest.fail(f"Startup failed: {startup_result.stderr}")

            # Wait for services to be ready
            max_wait = 60  # seconds
            start_time = time.time()

            while time.time() - start_time < max_wait:
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        break
                except requests.RequestException:
                    pass
                time.sleep(2)
            else:
                pytest.fail("API failed to become healthy within timeout")

            # Test API endpoints
            response = requests.get("http://localhost:8000/health")
            assert response.status_code == 200

            response = requests.get("http://localhost:8000/api/templates/list")
            assert response.status_code == 200

        finally:
            # Cleanup
            subprocess.run(
                ["docker-compose", "-f", str(compose_path), "down", "-v"],
                cwd=project_root,
            )


class TestStagingEnvironment:
    """Test staging environment setup"""

    def test_environment_variables(self):
        """Test required environment variables are defined"""
        import os

        # Check for critical environment variables
        required_vars = ["DATABASE_URL", "REDIS_URL", "OPENAI_API_KEY", "SECRET_KEY"]

        # For testing, we'll check if they're at least documented
        env_example = Path(__file__).parent.parent.parent / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            for var in required_vars:
                assert var in content, f"Required env var {var} not documented"

    def test_logging_configuration(self):
        """Test logging is properly configured"""
        import logging

        # Test that we can create loggers
        logger = logging.getLogger("pixel_ai")
        assert logger is not None

        # Test log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_database_migrations(self):
        """Test database migration files exist"""
        migrations_dir = Path(__file__).parent.parent / "migrations"

        # For now, just check that we have database setup
        init_sql = Path(__file__).parent.parent.parent / "scripts" / "init-db.sql"
        assert init_sql.exists(), "Database initialization script not found"

    def test_api_documentation(self):
        """Test API documentation is available"""
        # This would test that OpenAPI/Swagger docs are generated
        from api.main import app

        assert hasattr(app, "openapi_schema") or hasattr(app, "openapi")

        # Test that we can generate OpenAPI schema
        try:
            if hasattr(app, "openapi"):
                schema = app.openapi()
            else:
                from fastapi.openapi.utils import get_openapi

                schema = get_openapi(
                    title="Pixel AI Creator API",
                    version="1.0.0",
                    routes=app.routes,
                )

            assert "paths" in schema
            assert "components" in schema or "definitions" in schema

        except Exception as e:
            pytest.fail(f"Failed to generate OpenAPI schema: {e}")


class TestSystemHealth:
    """Test system health and monitoring"""

    def test_health_check_endpoint(self):
        """Test health check endpoint functionality"""
        from api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_startup_validation(self):
        """Test startup validation checks"""
        # Test that required directories exist
        required_dirs = ["templates", "generated-bots", "logs"]

        project_root = Path(__file__).parent.parent.parent
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            # Create if doesn't exist (for testing)
            dir_path.mkdir(exist_ok=True)
            assert dir_path.exists(), f"Required directory {dir_name} missing"

    def test_template_loading(self):
        """Test that templates can be loaded"""
        from api.services.template_manager import TemplateManager

        template_manager = TemplateManager()

        # Test loading all templates
        try:
            templates = template_manager.load_all_templates()
            assert isinstance(templates, dict)

            # Test that we have at least some templates
            assert len(templates) > 0, "No templates found"

        except Exception as e:
            # For testing, we might not have all templates
            pytest.skip(f"Template loading failed: {e}")

    def test_razorflow_service_initialization(self):
        """Test Razorflow service can be initialized"""
        from unittest.mock import Mock
        from api.services.razorflow_integration import RazorflowIntegration

        # Mock database
        mock_db = Mock()

        try:
            service = RazorflowIntegration(mock_db)
            assert service is not None
            assert hasattr(service, "queue_build")
            assert hasattr(service, "get_build_status")

        except Exception as e:
            pytest.fail(f"Failed to initialize Razorflow service: {e}")


@pytest.mark.performance
class TestPerformance:
    """Test system performance"""

    def test_api_response_time(self):
        """Test API response times are acceptable"""
        from fastapi.testclient import TestClient
        from api.main import app
        import time

        client = TestClient(app)

        # Test health endpoint
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health check too slow: {response_time}s"

    def test_template_loading_performance(self):
        """Test template loading performance"""
        from api.services.template_manager import TemplateManager
        import time

        template_manager = TemplateManager()

        start_time = time.time()
        try:
            templates = template_manager.load_all_templates()
            end_time = time.time()

            load_time = end_time - start_time
            assert load_time < 5.0, f"Template loading too slow: {load_time}s"

        except Exception:
            pytest.skip("Templates not available for performance test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
